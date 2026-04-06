"""PySide6 widgets composing the validator UI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import sys

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    Signal,
)
from PySide6.QtGui import QAction, QColor, QPainter, QBrush
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMessageBox,
    QInputDialog,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QStyledItemDelegate,
    QStyleOptionViewItem,
)

from .context_utils import build_highlighted_html
from .data_loader import (
    DEFAULT_DATASET,
    DatasetLoadError,
    load_dataset,
    save_dataset,
)
from .export_utils import export_review_markdown, export_review_txt
from .models import AnnotationSample, Metadata
from .project_store import (
    load_project_state,
    persist_source_text,
    persist_tags_file,
    persist_target_text,
    resolve_data_dir,
    save_project_state,
)

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts import convert_inputs  # type: ignore
from parser import cli as parser_cli, tag_defs as parser_tag_defs


class SampleListModel(QAbstractListModel):
    def __init__(self, samples: List[AnnotationSample]):
        super().__init__()
        self._samples = samples

    def rowCount(self, parent: QModelIndex | None = None) -> int:  # noqa: N802
        return len(self._samples)

    def data(self, index: QModelIndex, role: int):  # noqa: D401
        if not index.isValid():
            return None
        sample = self._samples[index.row()]

        if role in {
            Qt.ItemDataRole.DisplayRole,
            Qt.ItemDataRole.ToolTipRole,
        }:
            return sample.summary()

        if role == Qt.ItemDataRole.BackgroundRole:
            if sample.validado:
                if sample.low_confidence:
                    return QColor(255, 235, 205)  # light orange
                return QColor(220, 255, 220)  # green tint
            return QColor(255, 255, 255)  # neutral white

        return None

    def sample_at(self, row: int) -> Optional[AnnotationSample]:
        if 0 <= row < len(self._samples):
            return self._samples[row]
        return None

    def update_samples(self, samples: List[AnnotationSample]) -> None:
        self.beginResetModel()
        self._samples = samples
        self.endResetModel()

    def all_tags(self) -> List[str]:
        return sorted({sample.tag for sample in self._samples})

    def refresh_row(self, row: int) -> None:
        index = self.index(row, 0)
        if index.isValid():
            self.dataChanged.emit(index, index)


class SampleItemDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option, index):  # type: ignore
        painter.save()
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        bg = index.data(Qt.ItemDataRole.BackgroundRole)
        if isinstance(bg, QColor):
            opt.backgroundBrush = QBrush(bg)

        # Prevent default selection fill from wiping our background
        opt.showDecorationSelected = False
        opt.state &= ~QStyle.StateFlag.State_Selected
        super().paint(painter, opt, index)

        if option.state & QStyle.StateFlag.State_Selected:
            pen = painter.pen()
            pen.setColor(QColor(90, 90, 90))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(option.rect.adjusted(1, 1, -1, -1))
        painter.restore()


class SampleFilterModel(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._tag_filter: Optional[str] = None
        self._status_filter: Optional[str] = None
        self._search_text: str = ""

    def set_tag_filter(self, tag: Optional[str]) -> None:
        self._tag_filter = tag
        self.invalidateFilter()

    def set_status_filter(self, status: Optional[str]) -> None:
        self._status_filter = status
        self.invalidateFilter()

    def set_search_text(self, text: str) -> None:
        self._search_text = text.lower().strip()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent):  # noqa: N802
        model = self.sourceModel()
        if not isinstance(model, SampleListModel):
            return True
        sample = model.sample_at(source_row)
        if sample is None:
            return True

        if self._tag_filter and sample.tag != self._tag_filter:
            return False

        if self._status_filter == "ok" and sample.necessita_revisao_humana:
            return False
        if (
            self._status_filter == "revisar"
            and not sample.necessita_revisao_humana
        ):
            return False

        if self._search_text:
            haystack = " ".join(
                filter(
                    None,
                    [
                        sample.contexto_anotacao,
                        sample.trecho_alvo or "",
                        sample.trecho_fonte or "",
                    ],
                )
            ).lower()
            if self._search_text not in haystack:
                return False

        return True


class DetailPanel(QWidget):
    sample_updated = Signal(int, str)
    prev_requested = Signal()
    tag_change_requested = Signal()
    validate_requested = Signal()
    next_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._current_sample: Optional[AnnotationSample] = None
        self._current_row: Optional[int] = None

        self._tag_label = QLabel("TAG: --")
        self._review_label = QLabel("Revisao: --")
        self._updated_label = QLabel("Atualizado: --")

        self._context_box = QTextEdit()
        self._context_box.setReadOnly(True)
        self._context_box.setPlaceholderText(
            "Selecione uma anotacao para ver detalhes"
        )
        self._force_ltr_text(self._context_box)

        self._source_box = QTextEdit()
        self._source_box.setReadOnly(True)
        self._force_ltr_text(self._source_box)
        self._target_box = QTextEdit()
        self._target_box.setReadOnly(True)
        self._force_ltr_text(self._target_box)

        self._review_checkbox = QCheckBox("Baixo nivel de confianca")
        self._review_checkbox.stateChanged.connect(self._on_review_toggled)

        self._notes_box = QTextEdit()
        self._notes_box.setPlaceholderText(
            "Adicione uma nota justificando o baixo nivel de confianca (obrigatorio se checkbox marcado)"
        )
        self._force_ltr_text(self._notes_box)
        self._notes_box.textChanged.connect(self._on_notes_changed)

        self._reviewer_input = QLineEdit()
        self._reviewer_input.setPlaceholderText("Revisor (iniciais)")
        self._reviewer_input.editingFinished.connect(self._on_reviewer_changed)

        self._history_box = QPlainTextEdit()
        self._history_box.setReadOnly(True)
        self._force_ltr_text(self._history_box)

        # Action bar (bottom of detail panel)
        self._prev_button = QPushButton("Voltar")
        self._prev_button.clicked.connect(self.prev_requested.emit)
        self._change_tag_button = QPushButton("Alterar TAG")
        self._change_tag_button.clicked.connect(
            self.tag_change_requested.emit
        )
        self._validate_button = QPushButton("Validar")
        self._validate_button.clicked.connect(self.validate_requested.emit)
        self._next_button = QPushButton("Proximo")
        self._next_button.clicked.connect(self.next_requested.emit)

        layout = QVBoxLayout()
        layout.addWidget(self._tag_label)
        layout.addWidget(self._review_label)
        layout.addWidget(self._updated_label)
        layout.addWidget(QLabel("Revisor"))
        layout.addWidget(self._reviewer_input)
        layout.addWidget(QLabel("Contexto da Anotacao"))
        layout.addWidget(self._context_box)
        layout.addWidget(QLabel("Trecho Alvo"))
        layout.addWidget(self._target_box)
        layout.addWidget(QLabel("Trecho Fonte"))
        layout.addWidget(self._source_box)
        layout.addWidget(self._review_checkbox)
        layout.addWidget(QLabel("Notas / Motivo da revisao"))
        layout.addWidget(self._notes_box)
        layout.addWidget(QLabel("Historico"))
        layout.addWidget(self._history_box)
        action_row = QHBoxLayout()
        action_row.addStretch(1)
        action_row.addWidget(self._prev_button)
        action_row.addWidget(self._change_tag_button)
        action_row.addWidget(self._validate_button)
        action_row.addWidget(self._next_button)
        layout.addLayout(action_row)
        self.setLayout(layout)

    def set_sample(
        self, sample: Optional[AnnotationSample], row: Optional[int] = None
    ) -> None:
        self._current_sample = sample
        self._current_row = row
        if sample is None:
            self._tag_label.setText("TAG: --")
            self._review_label.setText("Revisao: --")
            self._updated_label.setText("Atualizado: --")
            self._context_box.clear()
            self._target_box.clear()
            self._source_box.clear()
            self._review_checkbox.setChecked(False)
            self._notes_box.clear()
            self._reviewer_input.setText("")
            self._history_box.clear()
            return

        self._tag_label.setText(f"TAG: {sample.tag} | {sample.nome}")
        if sample.validado:
            review = "Validado (baixo)" if sample.low_confidence else "Validado"
        else:
            review = "Pendente"
        self._review_label.setText(f"Revisao: {review}")
        self._updated_label.setText(
            f"Atualizado: {sample.updated_at or 'n/d'}"
        )
        self._review_checkbox.blockSignals(True)
        self._review_checkbox.setChecked(sample.necessita_revisao_humana)
        self._review_checkbox.blockSignals(False)
        self._context_box.setText(sample.contexto_anotacao)
        self._target_box.setText(
            sample.trecho_alvo or sample.texto_paragrafo_alvo
        )
        self._source_box.setText(
            sample.trecho_fonte or (sample.texto_paragrafo_fonte or "")
        )
        self._notes_box.blockSignals(True)
        self._notes_box.setText(sample.motivo_revisao or "")
        self._notes_box.blockSignals(False)
        self._reviewer_input.blockSignals(True)
        self._reviewer_input.setText(sample.reviewer or "")
        self._reviewer_input.blockSignals(False)
        self.refresh_history(sample)

    def refresh_history(self, sample: AnnotationSample) -> None:
        lines = []
        for entry in sample.history:
            timestamp = entry.get("timestamp", "?")
            reviewer = entry.get("reviewer", "-")
            action = entry.get("action", "acao")
            note = entry.get("notes")
            line = f"[{timestamp}] {reviewer}: {action}"
            if note:
                line += f" | {note}"
            lines.append(line)
        if not lines:
            lines = ["Sem historico"]
        self._history_box.setPlainText("\n".join(lines))

    def _emit_update(self, action: str) -> None:
        if self._current_row is None:
            return
        self.sample_updated.emit(self._current_row, action)

    def _on_review_toggled(self, state: int) -> None:
        if self._current_sample is None:
            return
        self._current_sample.low_confidence = (
            state == Qt.CheckState.Checked
        )
        self._current_sample.necessita_revisao_humana = self._current_sample.low_confidence
        if self._current_sample.low_confidence:
            self._current_sample.validado = False
            if not self._current_sample.motivo_revisao:
                self._notes_box.setFocus()
        else:
            self._notes_box.blockSignals(True)
            self._notes_box.clear()
            self._notes_box.blockSignals(False)
            self._current_sample.motivo_revisao = None
        text = self._notes_box.toPlainText().strip()
        self._current_sample.motivo_revisao = text or None
        self._emit_update("review_toggle")

    def _on_notes_changed(self) -> None:
        if self._current_sample is None:
            return
        text = self._notes_box.toPlainText().strip()
        self._current_sample.motivo_revisao = text or None
        if text and not self._current_sample.low_confidence:
            self._current_sample.low_confidence = True
            self._current_sample.necessita_revisao_humana = True
            self._review_checkbox.blockSignals(True)
            self._review_checkbox.setChecked(True)
            self._review_checkbox.blockSignals(False)
            self._current_sample.validado = False
        # Do not refresh the detail panel while typing to avoid cursor jumps.
        self._emit_update("notes_changed")

    def _on_reviewer_changed(self) -> None:
        if self._current_sample is None:
            return
        text = self._reviewer_input.text().strip()
        self._current_sample.reviewer = text or None
        self._emit_update("reviewer_changed")

    def _force_ltr_text(self, widget) -> None:
        # Enforce Left-to-Right typing and alignment to avoid RTL cursor issues.
        try:
            widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        except Exception:
            pass
        try:
            widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        except Exception:
            pass
        try:
            opt = widget.document().defaultTextOption()
            opt.setTextDirection(Qt.LayoutDirection.LeftToRight)
            widget.document().setDefaultTextOption(opt)
        except Exception:
            pass


class ContextPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._fallback_source_text = ""
        self._fallback_target_text = ""

        self._source_context_box = QTextEdit()
        self._source_context_box.setReadOnly(True)
        self._source_context_box.setPlaceholderText("Sem contexto fonte")

        self._target_context_box = QTextEdit()
        self._target_context_box.setReadOnly(True)
        self._target_context_box.setPlaceholderText("Sem contexto alvo")

        splitter = QSplitter()
        splitter.addWidget(self._source_context_box)
        splitter.addWidget(self._target_context_box)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        header = QHBoxLayout()
        header.addWidget(QLabel("Contexto Fonte"))
        header.addStretch(1)
        header.addWidget(QLabel("Contexto Alvo"))
        layout.addLayout(header)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def set_external_context(
        self,
        source_text: str | None,
        target_text: str | None,
    ) -> None:
        self._fallback_source_text = source_text or ""
        self._fallback_target_text = target_text or ""

    def set_sample(self, sample: Optional[AnnotationSample]) -> None:
        if sample is None:
            self._source_context_box.clear()
            self._target_context_box.clear()
            return

        source_text = sample.texto_paragrafo_fonte or self._fallback_source_text
        target_text = sample.texto_paragrafo_alvo or self._fallback_target_text

        source_html, source_focus = build_highlighted_html(
            source_text,
            sample.trecho_fonte,
        )
        self._source_context_box.setHtml(source_html)
        if source_focus:
            self._source_context_box.scrollToAnchor("focus")

        target_html, target_focus = build_highlighted_html(
            target_text,
            sample.trecho_alvo,
        )
        self._target_context_box.setHtml(target_html)
        if target_focus:
            self._target_context_box.scrollToAnchor("focus")


class MainWindow(QMainWindow):
    def __init__(self, dataset_path: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Validator Modelo 1")
        self.resize(1100, 700)

        self._data_dir = resolve_data_dir()
        self._project_state = load_project_state()
        self._tag_definitions: dict[str, dict[str, str]] = {}

        self._metadata: Optional[Metadata] = None
        self._samples: List[AnnotationSample] = []

        self._list_view = QListView()
        self._list_model = SampleListModel([])
        self._filter_model = SampleFilterModel()
        self._filter_model.setSourceModel(self._list_model)
        self._list_view.setModel(self._filter_model)
        self._list_view.setItemDelegate(SampleItemDelegate(self._list_view))

        self._context_panel = ContextPanel()
        self._detail_panel = DetailPanel()
        self._detail_panel.sample_updated.connect(self._on_sample_updated)
        self._detail_panel.prev_requested.connect(self._select_prev_row)
        self._detail_panel.tag_change_requested.connect(
            self._open_change_tag_dialog
        )
        self._detail_panel.validate_requested.connect(self._on_validate_clicked)
        self._detail_panel.next_requested.connect(self._select_next_row)
        self._reload_button = QPushButton("Recarregar")
        self._reload_button.clicked.connect(
            lambda: self._load_dataset(self._current_path)
        )
        self._save_button = QPushButton("Salvar...")
        self._save_button.clicked.connect(self._open_save_dialog)

        self._tag_filter = QComboBox()
        self._tag_filter.addItem("Todas as tags", None)
        self._tag_filter.currentIndexChanged.connect(
            self._handle_tag_filter_changed
        )
        self._status_filter = QComboBox()
        self._status_filter.addItem("Todos os status", None)
        self._status_filter.addItem("Somente OK", "ok")
        self._status_filter.addItem("Necessita revisar", "revisar")
        self._status_filter.currentIndexChanged.connect(
            self._handle_status_filter_changed
        )
        self._search_filter = QLineEdit()
        self._search_filter.setPlaceholderText(
            "Pesquisar por contexto, alvo ou fonte"
        )
        self._search_filter.textChanged.connect(self._handle_search_changed)

        splitter = QSplitter()
        splitter.addWidget(self._list_view)
        splitter.addWidget(self._context_panel)
        splitter.addWidget(self._detail_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)

        container = QWidget()
        container_layout = QVBoxLayout()
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Tag"))
        filter_row.addWidget(self._tag_filter)
        filter_row.addWidget(QLabel("Status"))
        filter_row.addWidget(self._status_filter)
        filter_row.addWidget(QLabel("Busca"))
        filter_row.addWidget(self._search_filter)
        filter_row.addStretch(1)
        button_row = QHBoxLayout()
        button_row.addWidget(self._reload_button)
        button_row.addWidget(self._save_button)
        button_row.addStretch(1)
        container_layout.addLayout(filter_row)
        container_layout.addLayout(button_row)
        container_layout.addWidget(splitter)
        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self._build_menu()

        self._current_path = self._resolve_initial_dataset_path(dataset_path)
        self._refresh_tag_definitions()
        self._refresh_associated_context()
        selection_model = self._list_view.selectionModel()
        if selection_model:
            selection_model.currentChanged.connect(
                self._on_selection_changed
            )
        self._load_dataset(self._current_path)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        open_action = QAction("Abrir dataset...", self)
        open_action.triggered.connect(self._open_dataset_dialog)
        file_menu.addAction(open_action)
        save_action = QAction("Salvar como...", self)
        save_action.triggered.connect(self._open_save_dialog)
        file_menu.addAction(save_action)

        export_md_action = QAction("Exportar revisao (Markdown)...", self)
        export_md_action.triggered.connect(
            lambda: self._export_human_readable("md")
        )
        file_menu.addAction(export_md_action)

        export_txt_action = QAction("Exportar revisao (TXT)...", self)
        export_txt_action.triggered.connect(
            lambda: self._export_human_readable("txt")
        )
        file_menu.addAction(export_txt_action)

        tools_menu = self.menuBar().addMenu("Ferramentas")
        import_action = QAction("Importar Documento (DOCX/PDF)...", self)
        import_action.triggered.connect(self._open_import_dialog)
        tools_menu.addAction(import_action)

        manage_tags_action = QAction("Gerenciar Arquivo de Tags...", self)
        manage_tags_action.triggered.connect(self._manage_tags_file)
        tools_menu.addAction(manage_tags_action)

        source_action = QAction("Associar Texto Fonte...", self)
        source_action.triggered.connect(self._associate_source_text)
        tools_menu.addAction(source_action)

        target_action = QAction("Associar Texto Alvo...", self)
        target_action.triggered.connect(self._associate_target_text)
        tools_menu.addAction(target_action)

        parser_action = QAction("Executar Parser...", self)
        parser_action.triggered.connect(self._open_parser_dialog)
        tools_menu.addAction(parser_action)

    def _resolve_initial_dataset_path(
        self,
        dataset_path: Path | None,
    ) -> Path:
        if dataset_path is not None:
            return Path(dataset_path)

        last = self._project_state.last_dataset_path
        if last:
            candidate = Path(last)
            if candidate.exists():
                return candidate
        return DEFAULT_DATASET

    def _save_project_state(self) -> None:
        save_project_state(self._project_state)

    def _refresh_tag_definitions(self) -> None:
        tags_path = self._project_state.tags_path
        self._tag_definitions = {}
        if not tags_path:
            return
        path = Path(tags_path)
        if not path.exists():
            return
        try:
            self._tag_definitions = parser_tag_defs.load_tag_definitions(path)
        except Exception:
            self._tag_definitions = {}

    def _refresh_associated_context(self) -> None:
        source_text = self._read_text_if_exists(
            self._project_state.source_text_path
        )
        target_text = self._read_text_if_exists(
            self._project_state.target_text_path
        )
        self._context_panel.set_external_context(source_text, target_text)

    def _read_text_if_exists(self, path_str: str | None) -> str | None:
        if not path_str:
            return None
        path = Path(path_str)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def _manage_tags_file(self) -> None:
        selected = self._select_path(
            title="Selecionar arquivo de tags",
            file_filter="Markdown (*.md *.txt)",
            start_dir=self._data_dir,
        )
        if not selected:
            return
        try:
            stored = persist_tags_file(selected)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Falha ao salvar tags",
                f"Nao foi possivel atualizar tab_est.md: {exc}",
            )
            return

        self._project_state.tags_path = str(stored)
        self._save_project_state()
        self._refresh_tag_definitions()
        QMessageBox.information(
            self,
            "Tags atualizadas",
            f"Arquivo de tags ativo: {stored}",
        )

    def _associate_source_text(self) -> None:
        self._associate_context_file(kind="source")

    def _associate_target_text(self) -> None:
        self._associate_context_file(kind="target")

    def _associate_context_file(self, kind: str) -> None:
        title = (
            "Selecionar texto fonte"
            if kind == "source"
            else "Selecionar texto alvo"
        )
        selected = self._select_path(
            title=title,
            file_filter="Documentos (*.md *.txt)",
            start_dir=self._data_dir,
        )
        if not selected:
            return

        try:
            if kind == "source":
                stored = persist_source_text(selected)
                self._project_state.source_text_path = str(stored)
            else:
                stored = persist_target_text(selected)
                self._project_state.target_text_path = str(stored)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Falha ao associar arquivo",
                f"Nao foi possivel salvar arquivo no data/: {exc}",
            )
            return

        self._save_project_state()
        self._refresh_associated_context()
        self._context_panel.set_sample(None)
        self.statusBar().showMessage(f"Arquivo associado: {stored}", 4000)

    def _resolve_or_prompt_source_path(self) -> Path | None:
        path_str = self._project_state.source_text_path
        if path_str:
            path = Path(path_str)
            if path.exists():
                return path

        default_path = BASE_DIR / "patriotismo_st.md"
        if default_path.exists():
            stored = persist_source_text(default_path)
            self._project_state.source_text_path = str(stored)
            self._save_project_state()
            self._refresh_associated_context()
            return stored

        selected = self._select_path(
            title="Arquivo fonte (Markdown)",
            file_filter="Markdown (*.md *.txt)",
            start_dir=self._data_dir,
        )
        if not selected:
            return None

        stored = persist_source_text(selected)
        self._project_state.source_text_path = str(stored)
        self._save_project_state()
        self._refresh_associated_context()
        return stored

    def _resolve_or_prompt_target_path(self) -> Path | None:
        path_str = self._project_state.target_text_path
        if path_str:
            path = Path(path_str)
            if path.exists():
                return path

        default_path = BASE_DIR / "patriotismo_tt.md"
        if default_path.exists():
            stored = persist_target_text(default_path)
            self._project_state.target_text_path = str(stored)
            self._save_project_state()
            self._refresh_associated_context()
            return stored

        selected = self._select_path(
            title="Arquivo alvo anotado (Markdown)",
            file_filter="Markdown (*.md *.txt)",
            start_dir=self._data_dir,
        )
        if not selected:
            return None

        stored = persist_target_text(selected)
        self._project_state.target_text_path = str(stored)
        self._save_project_state()
        self._refresh_associated_context()
        return stored

    def _resolve_or_prompt_tags_path(self) -> Path | None:
        path_str = self._project_state.tags_path
        if path_str:
            path = Path(path_str)
            if path.exists():
                return path

        default_path = BASE_DIR / "tab_est.md"
        if default_path.exists():
            stored = persist_tags_file(default_path)
            self._project_state.tags_path = str(stored)
            self._save_project_state()
            self._refresh_tag_definitions()
            return stored

        selected = self._select_path(
            title="Arquivo de tags (tab_est.md)",
            file_filter="Markdown (*.md *.txt)",
            start_dir=self._data_dir,
        )
        if not selected:
            return None

        stored = persist_tags_file(selected)
        self._project_state.tags_path = str(stored)
        self._save_project_state()
        self._refresh_tag_definitions()
        return stored

    def _open_dataset_dialog(self) -> None:
        target, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar dataset_raw.json",
            str(self._current_path.parent),
            "Arquivos JSON (*.json)",
        )
        if target:
            self._current_path = Path(target)
            self._load_dataset(self._current_path)

    def _open_import_dialog(self) -> None:
        start_dir = self._current_path.parent if self._current_path else BASE_DIR
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo para converter",
            str(start_dir),
            "Documentos (*.docx *.pdf *.txt *.md)",
        )
        if not path:
            return
        input_path = Path(path)
        output_path = input_path.with_suffix(".md")
        try:
            convert_inputs.convert_file(input_path, output_path)
        except convert_inputs.ConversionError as exc:
            QMessageBox.critical(self, "Falha na conversao", str(exc))
            return
        except Exception as exc:  # pragma: no cover - unexpected
            QMessageBox.critical(
                self,
                "Falha na conversao",
                f"Erro inesperado ao converter: {exc}",
            )
            return

        QMessageBox.information(
            self,
            "Arquivo convertido",
            (
                "Arquivo convertido com sucesso.\n"
                f"Saida: {output_path}\n\n"
                "Edite o Markdown em um editor externo para adicionar as anotacoes e, em seguida, use Ferramentas -> Executar Parser."
            ),
        )

    def _select_path(self, title: str, file_filter: str, start_dir: Path) -> Path | None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            title,
            str(start_dir),
            file_filter,
        )
        return Path(selected) if selected else None

    def _open_parser_dialog(self) -> None:
        source_path = self._resolve_or_prompt_source_path()
        if not source_path:
            return
        target_path = self._resolve_or_prompt_target_path()
        if not target_path:
            return
        tags_path = self._resolve_or_prompt_tags_path()
        if not tags_path:
            return

        default_output = target_path.with_name("dataset_raw.json")
        output_str, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar dataset gerado",
            str(default_output),
            "Arquivos JSON (*.json)",
        )
        output_path = Path(output_str) if output_str else default_output

        try:
            parser_cli.main(
                source_path=source_path,
                target_path=target_path,
                tags_path=tags_path,
                output_path=output_path,
            )
        except Exception as exc:  # pragma: no cover - user-facing dialog
            QMessageBox.critical(
                self,
                "Falha ao executar parser",
                f"Erro ao gerar dataset: {exc}",
            )
            return

        QMessageBox.information(
            self,
            "Parser concluido",
            (
                "dataset_raw.json gerado com sucesso.\n"
                f"Arquivo: {output_path}\n\n"
                "Carregando o dataset no VAEST."
            ),
        )
        self._current_path = output_path
        self._load_dataset(self._current_path)

    def _load_dataset(self, path: Path) -> None:
        try:
            metadata, samples = load_dataset(path)
        except DatasetLoadError as exc:
            QMessageBox.critical(self, "Erro ao carregar", str(exc))
            return

        # UX: start neutral (white). Only human actions set review/validated states.
        for sample in samples:
            if (not sample.validado) and (not sample.history) and (sample.reviewer is None):
                sample.necessita_revisao_humana = False
                sample.low_confidence = False

        self._metadata = metadata
        self._samples = samples
        self._project_state.last_dataset_path = str(path)
        self._save_project_state()
        self._list_model.update_samples(samples)
        self._filter_model.invalidate()
        self._populate_tag_filter()
        self._reset_filter_controls()
        self._filter_model.invalidateFilter()
        self._clear_selection()
        self.statusBar().showMessage(
            "Projeto: {proj} | Amostras: {count} | Arquivo: {file}".format(
                proj=metadata.projeto,
                count=len(samples),
                file=path,
            )
        )
        self._detail_panel.set_sample(None)
        self._context_panel.set_sample(None)

    def _available_tags(self) -> list[str]:
        defined_tags = sorted(
            tag.strip()
            for tag in self._tag_definitions
            if tag and tag.strip()
        )
        if defined_tags:
            return defined_tags

        fallback = sorted(tag for tag in self._list_model.all_tags() if tag)
        return fallback

    def _open_change_tag_dialog(self) -> None:
        selection_model = self._list_view.selectionModel()
        if not selection_model or not selection_model.currentIndex().isValid():
            QMessageBox.information(
                self,
                "Selecao necessaria",
                "Selecione um item para alterar a TAG.",
            )
            return

        source_index = self._filter_model.mapToSource(
            selection_model.currentIndex()
        )
        sample = self._list_model.sample_at(source_index.row())
        if sample is None:
            return

        choices = self._available_tags()
        if sample.tag and sample.tag not in choices:
            choices.insert(0, sample.tag)
        if not choices:
            QMessageBox.warning(
                self,
                "Sem TAGs",
                "Nao ha TAGs disponiveis para selecao.",
            )
            return

        current_index = 0
        if sample.tag in choices:
            current_index = choices.index(sample.tag)

        selected_tag, ok = QInputDialog.getItem(
            self,
            "Alterar TAG",
            "Selecione a nova TAG:",
            choices,
            current_index,
            False,
        )
        if not ok:
            return

        selected_tag = selected_tag.strip()
        if not selected_tag or selected_tag == sample.tag:
            return

        old_tag = sample.tag
        sample.tag = selected_tag
        tag_info = self._tag_definitions.get(selected_tag)
        if tag_info:
            sample.nome = tag_info.get("nome", sample.nome)
            sample.tipo_nivel = tag_info.get("tipo_nivel", sample.tipo_nivel)

        self._on_sample_updated(
            source_index.row(),
            f"tag_changed:{old_tag}->{selected_tag}",
        )
        self._populate_tag_filter()
        self._filter_model.invalidateFilter()

    def _handle_selection(self, index: QModelIndex) -> None:
        if not index.isValid():
            self._detail_panel.set_sample(None)
            self._context_panel.set_sample(None)
            return
        source_index = self._filter_model.mapToSource(index)
        sample = self._list_model.sample_at(source_index.row())
        if sample is None:
            self._detail_panel.set_sample(None)
            self._context_panel.set_sample(None)
            return
        self._detail_panel.set_sample(sample, row=source_index.row())
        self._context_panel.set_sample(sample)

    def _on_validate_clicked(self) -> None:
        selection_model = self._list_view.selectionModel()
        if not selection_model or not selection_model.currentIndex().isValid():
            QMessageBox.information(
                self,
                "Selecao necessaria",
                "Selecione um item para validar.",
            )
            return
        source_index = self._filter_model.mapToSource(
            selection_model.currentIndex()
        )
        sample = self._list_model.sample_at(source_index.row())
        if sample is None:
            return

        sample.validado = True
        sample.necessita_revisao_humana = sample.low_confidence
        sample.motivo_revisao = None if not sample.low_confidence else sample.motivo_revisao

        self._list_model.refresh_row(source_index.row())
        self._filter_model.invalidateFilter()
        proxy_index = self._filter_model.mapFromSource(source_index)
        if proxy_index.isValid():
            self._list_view.update(proxy_index)
        self._list_view.viewport().update()
        self._on_sample_updated(source_index.row(), "validated")

    def _select_prev_row(self) -> None:
        selection_model = self._list_view.selectionModel()
        if not selection_model:
            return
        current = selection_model.currentIndex()
        row = current.row() if current.isValid() else 0
        prev_row = row - 1
        if prev_row < 0:
            return
        prev_index = self._filter_model.index(prev_row, 0)
        selection_model.setCurrentIndex(
            prev_index, selection_model.SelectionFlag.ClearAndSelect
        )
        self._handle_selection(prev_index)

    def _select_next_row(self) -> None:
        selection_model = self._list_view.selectionModel()
        if not selection_model:
            return
        current = selection_model.currentIndex()
        # Move in filter model, then map to source
        row = current.row() if current.isValid() else -1
        next_row = row + 1
        if next_row >= self._filter_model.rowCount():
            return
        next_index = self._filter_model.index(next_row, 0)
        selection_model.setCurrentIndex(
            next_index, selection_model.SelectionFlag.ClearAndSelect
        )
        self._handle_selection(next_index)

    def _on_sample_updated(self, row: int, action: str) -> None:
        sample = self._list_model.sample_at(row)
        if sample is None:
            return
        if action.startswith("tag_changed:"):
            old_new = action.split(":", maxsplit=1)[1]
            action_label = f"TAG alterada ({old_new})"
        else:
            action_labels = {
                "review_toggle": "Status de revisao",
                "notes_changed": "Notas atualizadas",
                "reviewer_changed": "Revisor atribuido",
                "validated": "Marcado como validado",
            }
            action_label = action_labels.get(action, action)
        timestamp = datetime.now().isoformat(timespec="seconds")
        sample.log_change(
            action=action_label,
            reviewer=sample.reviewer,
            notes=sample.motivo_revisao,
            timestamp=timestamp,
        )
        if 0 <= row < len(self._samples):
            self._samples[row] = sample
        self._list_model.refresh_row(row)
        self._filter_model.invalidateFilter()
        proxy_index = self._filter_model.mapFromSource(self._list_model.index(row, 0))
        if proxy_index.isValid():
            self._list_view.update(proxy_index)
        self._list_view.viewport().update()
        if action != "notes_changed":
            self._detail_panel.set_sample(sample, row=row)
        status = (
            "Validado"
            if sample.validado
            else "Necessita revisao"
            if sample.necessita_revisao_humana
            else "Pendente"
        )
        self.statusBar().showMessage(
            f"Atualizado {sample.id} ({status})", 4000
        )

    def _populate_tag_filter(self) -> None:
        tags = self._list_model.all_tags()
        previous = self._tag_filter.currentData()
        self._tag_filter.blockSignals(True)
        self._tag_filter.clear()
        self._tag_filter.addItem("Todas as tags", None)
        for tag in tags:
            label = tag or "(sem tag)"
            self._tag_filter.addItem(label, tag)
        index = self._tag_filter.findData(previous)
        if index == -1:
            index = 0
        self._tag_filter.setCurrentIndex(index)
        self._tag_filter.blockSignals(False)
        self._filter_model.set_tag_filter(self._tag_filter.currentData())

    def _reset_filter_controls(self) -> None:
        self._tag_filter.blockSignals(True)
        self._tag_filter.setCurrentIndex(0)
        self._tag_filter.blockSignals(False)
        self._filter_model.set_tag_filter(self._tag_filter.currentData())

        self._status_filter.blockSignals(True)
        self._status_filter.setCurrentIndex(0)
        self._status_filter.blockSignals(False)
        self._filter_model.set_status_filter(None)

        self._search_filter.blockSignals(True)
        self._search_filter.clear()
        self._search_filter.blockSignals(False)
        self._filter_model.set_search_text("")

    def _handle_tag_filter_changed(self) -> None:
        self._filter_model.set_tag_filter(self._tag_filter.currentData())

    def _handle_status_filter_changed(self) -> None:
        self._filter_model.set_status_filter(self._status_filter.currentData())

    def _handle_search_changed(self, text: str) -> None:
        self._filter_model.set_search_text(text)

    def _on_selection_changed(
        self, current: QModelIndex, _: QModelIndex
    ) -> None:
        if current and current.isValid():
            self._handle_selection(current)
        else:
            self._detail_panel.set_sample(None)

    def _clear_selection(self) -> None:
        selection_model = self._list_view.selectionModel()
        if selection_model:
            selection_model.clearSelection()
        self._detail_panel.set_sample(None)
        self._context_panel.set_sample(None)

    def _open_save_dialog(self) -> None:
        if not self._metadata:
            return
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar dataset revisado",
            str(self._current_path.with_name("dataset_reviewed.json")),
            "Arquivos JSON (*.json)",
        )
        if target:
            self._save_dataset(Path(target))

    def _save_dataset(self, path: Path) -> None:
        if not self._metadata:
            QMessageBox.warning(
                self, "Sem dados", "Nenhum dataset carregado para salvar."
            )
            return
        try:
            save_dataset(path, self._metadata, self._samples)
        except OSError as exc:
            QMessageBox.critical(
                self, "Erro ao salvar", f"Nao foi possivel salvar: {exc}"
            )
            return
        QMessageBox.information(
            self,
            "Dataset salvo",
            f"Alteracoes gravadas em {path}",
        )

    def _export_human_readable(self, fmt: str) -> None:
        if not self._metadata:
            QMessageBox.warning(
                self,
                "Sem dados",
                "Nenhum dataset carregado para exportar.",
            )
            return

        suffix = ".md" if fmt == "md" else ".txt"
        filter_spec = (
            "Markdown (*.md)" if fmt == "md" else "Texto (*.txt)"
        )
        default_name = self._current_path.stem + "_review_report" + suffix
        default_path = self._current_path.with_name(default_name)

        output, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar revisao",
            str(default_path),
            filter_spec,
        )
        if not output:
            return

        path = Path(output)
        try:
            if fmt == "md":
                export_review_markdown(path, self._metadata, self._samples)
            else:
                export_review_txt(path, self._metadata, self._samples)
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Falha na exportacao",
                f"Nao foi possivel exportar o relatorio: {exc}",
            )
            return

        QMessageBox.information(
            self,
            "Exportacao concluida",
            f"Relatorio salvo em {path}",
        )


def run(dataset_path: Path | None = None) -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(dataset_path=dataset_path)
    window.show()
    app.exec()

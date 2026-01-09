# Executive Summary — Unified Roadmap for VAEST (Validator as Workflow Hub)

VAEST has transitioned from a functional prototype into a mature validation environment. The remaining challenges are no longer algorithmic but **architectural, ergonomic, and workflow-oriented**. Addressing them requires a structured roadmap that balances **cognitive load reduction**, **data integrity**, and **long-term maintainability**, while preserving the tool’s defining constraint: **no installation and low technical burden for end users**.

This executive summary consolidates all identified issues—both previously known and newly surfaced—and proposes a unified, professional approach to guide development from this point onward.

---

## 1. Current State Diagnosis

VAEST currently succeeds at:

* Loading and validating parsed datasets
* Preserving review history and reviewer attribution
* Ensuring dataset integrity for downstream ML training

However, usability analysis and real-world usage exposed five critical friction points and two architectural gaps:

### Identified Issues (Complete List)

1. **No human-readable export** after validation (only JSON).
2. **Lack of contextual access** to source and target texts during review.
3. **Inability to change tags** when a different simplification strategy becomes more appropriate.
4. **Notes / Motivo da Revisão field typing bug**, currently right-to-left oriented.
5. **No visual indication of validation state** in the segment list, causing excessive cognitive load.
6. **Source text not treated as a first-class input**, despite being essential for contextual validation.
7. **Repeated prompting for stable auxiliary files** (notably `tab_est.md`), despite their curated and rarely changing nature.

---

## 2. Core Design Reframing

Two realizations redefine the roadmap:

> **Validation is a project-level activity, not a file-level one.**
> **Context is epistemically necessary for linguistic validation.**

These imply that VAEST must evolve from:

> *A dataset viewer*

into:

> **A lightweight, portable workflow hub for contextual linguistic validation**

This evolution does **not** imply scope explosion. It implies better lifecycle modeling of existing artifacts.

---

## 3. Architectural Adjustments (Foundational)

### 3.1 Source Text as a First-Class Artifact

**Problem**
The source text was previously assumed to be relevant only during parsing. Side-by-side validation reveals this assumption is invalid.

**Decision**
The validation phase must explicitly include:

* Source (non-annotated) text
* Target (annotated) text

These texts must be persistently associated with the dataset, not repeatedly re-selected.

---

### 3.2 Introduction of a Local, Portable `data/` Folder

**Problem**
Curated auxiliary files (e.g., `tab_est.md`) are treated as transient inputs, causing unnecessary friction.

**Solution**
VAEST will create and manage a local subfolder relative to the executable:

```
./data/
  ├── tab_est.md          # Tag definitions (project-level)
  ├── source_text.md      # Source text
  ├── target_text.md      # Annotated target text
  └── metadata.json       # Associations & project state
```

**Principles**

* No installation
* No hidden paths
* Fully portable
* Explicit and inspectable

---

### 3.3 Persistent Management of Tag Definitions

**Decision**

* `tab_est.md` is treated as **project configuration**, not dataset input.
* Loaded once, reused across sessions.

**UX**

```
Ferramentas → Gerenciar Arquivo de Tags…
```

* View current tag file
* Replace/update intentionally
* Reload into memory
* Log changes (timestamp + reviewer)

This preserves taxonomy integrity and avoids silent drift.

---

## 4. UX & Ergonomic Improvements (Cognitive Load Reduction)

### 4.1 Fix RTL Typing Bug (Immediate)

**Issue**
“Notas / Motivo da Revisão” is right-to-left oriented.

**Action**
Force left-to-right layout and alignment explicitly at the widget level.

**Impact**

* Zero architectural risk
* Immediate usability improvement

---

### 4.2 Visual Validation State Mapping (Critical)

**Issue**
Users cannot visually distinguish validated vs. unvalidated segments.

**Solution**

* Color-map the segment list:

  * 🟢 Green: validated
  * ⚪ White: untouched
  * (Optional) 🔴 Light red: flagged

**Impact**

* Drastically reduces cognitive load
* Enables visual progress tracking
* Aligns with professional annotation tools

---

### 4.3 Side-by-Side Contextual Review Panels (Highest UX Impact)

**Problem**
Users currently rely on external software to assess context.

**Solution**
Introduce read-only, synchronized panels:

```
[ Segment List ] | [ Source Text ] | [ Target Text ]
```

**Behavior**

* Auto-scroll to the relevant segment
* Highlight corresponding spans
* No editing inside VAEST

**Rationale**

* Zero data mutation
* Maximum epistemic clarity
* Transforms validation quality

---

## 5. Controlled Power Features (Data Integrity Preserved)

### 5.1 Tag Changes as Review Actions (Not Edits)

**Problem**
Tags may need correction during validation.

**Risk**
Uncontrolled mutation can corrupt training data.

**Solution**

* Clicking a tag opens a controlled context menu
* Tag changes:

  * Require explicit selection
  * Are logged in review history
  * Preserve auditability

This treats tag changes as **review decisions**, not casual edits.

---

## 6. Output & Distribution

### 6.1 Human-Readable Export

**Requirement**
After validation, users must export:

* Machine-readable JSON (training)
* Human-readable TXT / Markdown (sharing)
* PDF as a later enhancement

**Approach**

* Generate structured Markdown/TXT from existing JSON
* Preserve reviewer notes and decisions
* Defer PDF layout complexity

---

## 7. Sequenced Roadmap (Authoritative)

### Phase A — Immediate Fixes

* Fix RTL typing bug
* Add validation-state color mapping

### Phase B — Foundational UX

* Introduce persistent `data/` folder
* Treat source text as first-class input
* Simplify dataset loading (no repeated prompts)

### Phase C — Core Review Experience

* Side-by-side contextual panels
* Auto-scroll and highlight logic

### Phase D — Controlled Editing

* Tag changes with audit logging

### Phase E — Output & Sharing

* Markdown/TXT export
* PDF (optional, later)

---

## 8. Bottom Line

VAEST is no longer a prototype. It is becoming a **context-aware linguistic validation environment**. The roadmap must now prioritize:

* Cognitive ergonomics
* Auditability
* Context preservation
* Minimal but persistent project state

This unified executive summary supersedes earlier planning documents and should serve as the **authoritative reference** for all future development decisions.

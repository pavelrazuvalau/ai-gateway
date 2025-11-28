# Current Session Context

## 📊 Metadata

**Artifact Version:** 2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Operational memory for managing current task state  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) should contain only data, not instructions.  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

---

## Current Session

**Quick Reference:** This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT). For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

**Date:** YYYY-MM-DD  
**Focus:** [Current session focus]  
**Goal:** [Session goal]

---

## Work State

### Last Actions (last 5)

1. ✅ [Action 1]
2. ✅ [Action 2]
3. ⏳ [Action 3]
4. 🔴 [Action 4 - blocked]

---

## Active Context

### Files in Focus
- `file1.[ext]` - [reason]
- `file2.[ext]` - [reason]

### Target Structure
[Target structure or goal]

---

## Temporary Notes

- [Temporary note 1]
- [Temporary note 2]

---

## Intermediate Decisions

- [Decision 1] - [rationale]
- [Decision 2] - [rationale]

---

## Artifact Links

- **PLAN:** Phase X, Step Y
- **QUESTIONS:** [Active questions if any]
- **CHANGELOG:** Last entry - Phase X, Step Y

---

## Next Steps

1. ⏳ [Next step 1]
2. ⏳ [Next step 2]

---

## 📐 Formatting Reference

### Status Icons (for actions)

- ✅ **Completed** - Action completed successfully
- ⏳ **In Progress** - Action currently in progress
- 🔴 **Blocked** - Action blocked, waiting for resolution

### Structure Formatting

**Current Session:**
- Date: YYYY-MM-DD
- Focus: Current session focus (brief description)
- Goal: Session goal (what to achieve)

**Work State - Last Actions:**
- Maximum 5 entries
- Format: `1. [Status Icon] [Action description]`
- Sort: Newest first (1 = most recent)
- Remove oldest when adding new (if > 5)

**Active Context:**
- Files in Focus: List with file paths and reasons
- Target Structure: Description of target structure or goal

**Temporary Notes:**
- Bullet list format
- Clear when step completes
- Move to CHANGELOG if important

**Intermediate Decisions:**
- Format: `- [Decision] - [rationale]`
- Document decisions made during work
- Move to CHANGELOG if important

**Artifact Links:**
- PLAN: Phase X, Step Y
- QUESTIONS: List active questions if any
- CHANGELOG: Last entry - Phase X, Step Y

**Next Steps:**
- Bullet list format
- Use status icons: ⏳
- Immediate next actions

### Cross-Artifact Links

**Link format:** `@[ARTIFACT_NAME]` notation

**Examples:**
- `@[TASK_NAME]_PLAN.md` - link to PLAN
- `@[TASK_NAME]_CHANGELOG.md (Phase 1, Step 1.1)` - link to specific entry
- `QX.Y in @[TASK_NAME]_QUESTIONS.md` - link to question

**Rules:**
- Always use artifact file name
- Include phase/step or question identifier when linking to specific content
- Use consistent format across all artifacts
- Verify links point to existing content

### Anchor Links for Navigation

**Concept**: Anchor links provide fast navigation for both AI agents and humans. They enable quick jumping to specific sections within artifacts.

**Format**: `[Text](#anchor-name)` where anchor is generated from heading text.

**Anchor Generation Rules**:
- Markdown automatically creates anchors from headings
- Format: lowercase, spaces converted to hyphens, special characters removed
- Example: `#### Step 4.3: E2E тесты` → anchor `#step-43-e2e-тесты`
- For headings with special characters, use the exact heading text and let Markdown generate the anchor

**Usage**:
- Use anchor links when referencing specific sections in other artifacts
- Anchor links enable both agents and humans to quickly navigate to relevant sections

**Important**: Always verify anchor links point to existing headings in the artifact.

## Work Rules

- Update this file during work
- Clear when task completes or new session starts
- Use for quick navigation to current context
- Keep temporary information only (move important info to CHANGELOG)
- Maximum 5 entries in "Last Actions"

---

## 🤖 Instructions for AI agent

**Important:** This section is part of the template (View layer). When creating actual artifacts (Model layer), **COPY this instruction section** into the artifact at the end of the document. This ensures that instructions for working with the artifact are always available within the artifact itself, making it self-sufficient and independent of external prompts or templates.

**Artifact System Overview:**

This artifact is part of a system of 4 required artifacts that work together:

1. **PLAN** (`*_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
2. **CHANGELOG** (`*_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
3. **QUESTIONS** (`*_QUESTIONS.md`) - Knowledge base for doubts and solutions. Contains active questions (blockers) and resolved questions.
4. **SESSION_CONTEXT** (`*_SESSION_CONTEXT.md`) - Current work state. Contains temporary notes, intermediate decisions, and active context.

**Artifact Relationships:**
- PLAN references blockers in QUESTIONS and recent changes in CHANGELOG
- CHANGELOG entries link to PLAN steps and related questions in QUESTIONS
- QUESTIONS link to PLAN steps and CHANGELOG entries where solutions were applied
- SESSION_CONTEXT tracks current PLAN phase/step and active questions

**When to update artifacts:**
- **PLAN**: When step status changes, when starting/completing steps, when blocked
- **CHANGELOG**: When step completes, when question is resolved, when approach changes
- **QUESTIONS**: When creating new question, when answering question
- **SESSION_CONTEXT**: When starting step, when discovering blocker, when completing step, when making intermediate decisions

**How to read artifacts (created from this template):**
1. Check "Current Session" for current focus and goal
2. Review "Work State" for recent actions (last 5)
3. Check "Active Context" for files in focus and target structure
4. Review "Temporary Notes" and "Intermediate Decisions" for context
5. Check "Artifact Links" for current phase/step and active questions
6. Review "Next Steps" for immediate actions

**How to update artifacts (created from this template):**
1. When starting new step → update:
   - "Current Session": Date, Focus, Goal
   - "Artifact Links": Current PLAN phase/step
   - "Next Steps": Immediate actions
2. When discovering blocker → document:
   - "Work State": Add blocker action
   - "Temporary Notes": Blocker details
   - "Artifact Links": Link to created question
3. When completing step → cleanup:
   - Move relevant info from SESSION_CONTEXT to CHANGELOG
   - Clear temporary notes (move to CHANGELOG if important)
   - Clear intermediate decisions (move to CHANGELOG if important)
   - Remove completed actions from "Last Actions"
   - Update "Artifact Links" to reflect completion
   - Update "Next Steps" for next step
4. When making intermediate decision → document:
   - "Intermediate Decisions": Add decision with rationale
5. Update "Last Actions" (keep last 5):
   - Add new action at the top
   - Remove oldest if more than 5
   - Use status icons: ✅ Completed, ⏳ In Progress, 🔴 Blocked

**Formatting rules:**
- Use exact structure as defined in sections above
- Date format: YYYY-MM-DD
- Status icons: ✅ ⏳ 🔴
- Links use `@[ARTIFACT_NAME]` notation
- Keep "Last Actions" to maximum 5 entries
- Clear temporary information when step completes

**Update triggers:**
- Starting new step (add current task focus)
- Discovering blocker (document blocker state)
- Completing step (prepare for cleanup)
- Making intermediate decision (document decision)
- Significant context change (update active context)

**When to use this file:**
- When checking current work state
- When tracking temporary notes and decisions
- When navigating to current context
- When documenting intermediate decisions
- When tracking work progress

**Related artifacts:**
- `*_PLAN.md` - for understanding current phase/step
- `*_QUESTIONS.md` - for checking active questions
- `*_CHANGELOG.md` - for history of completed work


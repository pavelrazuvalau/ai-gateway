# [Task Name]

## 📊 Metadata

**Artifact Version:** 2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** [Purpose of this plan]  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) should contain only data, not instructions.

**Status:** 🟢 COMPLETED | 🟡 IN PROGRESS | 🔴 BLOCKED | ⚪ PENDING  
**Current Phase:** Phase X  
**Current Step:** Step X.Y  
**Last Update:** YYYY-MM-DD  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

---

## 🎯 Current Focus

> **Current Step:** [Phase X, Step Y: Step Name](#phase-x-step-xy-step-name)  
> **Status:** 🟡 IN PROGRESS | 🔴 BLOCKED | ⚪ PENDING  
> **Requires Action:** [Yes/No - if BLOCKED and needs user input]

---

## 🎯 Description

[Brief description of the task, goals, and business value]

## 🚦 Quick Navigation for AI agent

**Quick Reference:** This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT). For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

- **Start here:** Phase X, Step Y
- **Blockers:** See @*_QUESTIONS.md (section [X])
- **Recent changes:** See @*_CHANGELOG.md (entry from [date])

---

## Implementation Phases

### Phase X: [Phase Name]

**Context:** [Context of related tasks in this phase]  
**Goal:** [Expected outcome]  
**Status:** 🟢 COMPLETED | 🟡 IN PROGRESS | 🔴 BLOCKED | ⚪ PENDING

#### Step X.Y: [Step Name]

**Status:** ⚪ Pending | 🟡 In Progress | 🟢 Done | 🔴 Blocked

**What needs to be done:**
- [Specific action 1]
- [Specific action 2]

**Why this approach:**
[Justification of approach - critical for AI agent to understand context and avoid hallucinations]

**Where to make changes:**
- Files: `path/to/file.[ext]`, `docs/section.md`
- Functions/Classes: `ClassName.method_name()`

**Completion criteria:**
- [ ] [Checkpoint 1]
- [ ] [Checkpoint 2]

**Related questions:** QX.Y in @*_QUESTIONS.md

---

[Repeat structure for all phases and steps]

---

## 📐 Formatting Reference

This section defines all formatting rules, icons, and structure for PLAN artifacts. Use these definitions when creating or updating PLAN artifacts.

### Status Icons

**For Steps and Phases:**
- 🟢 **COMPLETED** / **Done** - All completion criteria met, changes documented in CHANGELOG, no blocking issues
- 🟡 **IN PROGRESS** / **In Progress** - Actively working on this step, some criteria may be incomplete
- 🔴 **BLOCKED** / **Blocked** - Cannot proceed due to blocking issue, question created in QUESTIONS, waiting for resolution
- ⚪ **PENDING** / **Pending** - Not started yet, waiting for prerequisites or previous steps

**Status transition rules:**
- ⚪ PENDING → 🟡 IN PROGRESS (when work begins)
- 🟡 IN PROGRESS → 🟢 COMPLETED (when all criteria met)
- 🟡 IN PROGRESS → 🔴 BLOCKED (when blocker discovered)
- 🔴 BLOCKED → 🟡 IN PROGRESS (when question answered)

**For Questions:**
- ⏳ **Pending** - Question created, waiting for answer
- ✅ **Resolved** - Question answered, solution documented, moved to resolved section

### Priority Icons (for questions)

- 🔴 **High** - Blocks work, cannot proceed
- 🟡 **Medium** - Affects work, can proceed with assumptions
- 🟢 **Low** - Optimization, can proceed without answer

**Priority sorting:** Questions must be sorted by priority: 🔴 High → 🟡 Medium → 🟢 Low

### Blocker Type Icons (for questions)

- 🔍 **Requires user clarification** - needs clarification of context or requirements
- 🏗️ **Architectural problem** - design contradiction
- 🐛 **Bug discovered** - technical blocker
- 📊 **Requirements unclear** - needs clarification of business logic
- 🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation

### Structure Formatting

**Metadata section:**
- Must include: Artifact Version, Last Adaptation Date, Purpose, Status, Current Phase, Current Step, Last Update
- Status values: 🟢 COMPLETED | 🟡 IN PROGRESS | 🔴 BLOCKED | ⚪ PENDING

**Phase structure:**
- Format: `### Phase X: [Phase Name]`
- Must include: Context, Goal, Status
- Status uses same icons as steps

**Step structure:**
- Format: `#### Step X.Y: [Step Name]`
- Must include sections:
  - Status (with icon)
  - What needs to be done (bullet list)
  - Why this approach (paragraph)
  - Where to make changes (bullet list with files/functions)
  - Completion criteria (checklist)
  - Related questions (if any)

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
- Use anchor links in "Current Focus" and "Quick Navigation" sections
- Update anchor links when current step/question changes
- Anchor links enable both agents and humans to quickly navigate to relevant sections

**Example**:
- In PLAN artifact "Current Focus" section: `[Phase 1, Step 1.1: Setup](#phase-1-step-11-setup)`
- In QUESTIONS artifact "Current Focus" section: `[Q2.1: Question Title](#q21-question-title-phase-2-step-1)`

**Important**: Always verify anchor links point to existing headings in the artifact.

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
1. Start with section "🚦 Quick Navigation for AI agent" to understand current state (blockers are referenced here)
2. Study current step in section "Implementation Phases"
3. Follow the instructions in this section for working with the artifact

**How to update artifacts (created from this template):**
1. When step status changes → update metadata at the beginning of file:
   - Update "Status" field
   - Update "Current Phase" and "Current Step" if changed
   - Update "Last Update" date
   - **Update "🎯 Current Focus" section** with new step link and status
2. When step completes → update step status (🟢 Done) and metadata:
   - Change step status to 🟢 Done
   - Update phase status if all steps complete
   - Update metadata fields
   - **Update "🎯 Current Focus" section** to next step (if any) or mark as completed
3. When blocked → update status (🔴 Blocked) and add blocker reference:
   - Change step status to 🔴 Blocked
   - Update phase status to 🔴 BLOCKED if needed
   - Add blocker reference to "🚦 Quick Navigation for AI agent" section
   - Update metadata
   - **Update "🎯 Current Focus" section** with blocked status and set "Requires Action: Yes" if needs user input
4. When starting work → update status to 🟡 In Progress:
   - Change step status from ⚪ Pending to 🟡 In Progress
   - Update metadata
   - **Update "🎯 Current Focus" section** with In Progress status
5. After changes → add entry to `*_CHANGELOG.md` (see CHANGELOG artifact instructions for procedure)

**How to update Current Focus section:**

**For PLAN:**
1. When Current Step changes → update "🎯 Current Focus" section:
   - Update "Current Step" link to point to new step using anchor format: `[Phase X, Step Y: Step Name](#phase-x-step-xy-step-name)`
   - Update "Status" to match step status
   - Update "Requires Action" if step is BLOCKED and needs user input
2. When step status changes (but Current Step remains the same) → update "🎯 Current Focus" section:
   - Update "Status" to match new step status
   - Update "Requires Action" if step becomes BLOCKED and needs user input, or remove it if step is no longer blocked
3. When all steps are completed → update "🎯 Current Focus" section:
   - Set to: "All steps completed" or remove the section if preferred
4. Format for anchor links: `[Phase X, Step Y: Step Name](#phase-x-step-xy-step-name)`
   - Markdown automatically creates anchors from headings
   - Format: lowercase, spaces to hyphens, special chars removed
   - Example: `#### Step 4.3: E2E тесты` → `#step-43-e2e-тесты`
   - For steps with special characters, use the exact heading text and let Markdown generate the anchor
   - To find the correct anchor, look at the actual heading in the document and use the format shown above

**Formatting rules:**
- Use exact status icons as defined in "📐 Formatting Reference" section above
- Follow structure: Phase → Step → What/Why/Where/Completion criteria
- Use consistent phase/step numbering (Phase X, Step X.Y)
- Links to other artifacts use `@[ARTIFACT_NAME]` notation
- Metadata fields must be updated when status changes

**When to use this file:**
- When starting work on a task from the plan
- When checking current project state
- When deciding on next step
- When updating work status
- When checking blockers and current progress

**Related artifacts:**
- `*_QUESTIONS.md` - for checking active questions and blockers
- `*_CHANGELOG.md` - for history of completed changes
- `*_SESSION_CONTEXT.md` - for current session context

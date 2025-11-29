# [Task Name]

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** [Purpose of this plan]  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) contain data AND copied instructions (for self-sufficiency). Instructions section will be copied from this template.

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

**⚠️ IMPORTANT FOR CREATION AGENT (planning agent):**

These instructions are for FUTURE USE by the execution agent.
DO NOT try to execute these instructions while creating the artifact.
Your job is to COPY this entire section into the artifact as-is, at the end of the document.
These instructions will be used later when working with the artifact during execution phase.
Do NOT follow "How to update" or "When to update" instructions during artifact creation.

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

**Simple rule:** Show the highest priority active step (first step that is not completed).

**Procedure:**
1. Find the first step with status: 🟡 IN PROGRESS, 🔴 BLOCKED, or ⚪ PENDING (in order of phases and steps)
2. Update "🎯 Current Focus" section with that step's link and status
3. If step is BLOCKED and needs user input → set "Requires Action: Yes"
4. If all steps completed → show "All steps completed"

**Examples:**

**Example 1: Step in progress**
```
## 🎯 Current Focus

> **Current Step:** [Phase 1, Step 1.1: Setup environment](#phase-1-step-11-setup-environment)
> **Status:** 🟡 IN PROGRESS
> **Requires Action:** No
```

**Example 2: Step blocked**
```
## 🎯 Current Focus

> **Current Step:** [Phase 2, Step 2.3: Implement feature](#phase-2-step-23-implement-feature)
> **Status:** 🔴 BLOCKED
> **Requires Action:** Yes
```

**Example 3: All completed**
```
## 🎯 Current Focus

> **Status:** All steps completed
```

**Anchor link format:** `[Phase X, Step Y: Step Name](#phase-x-step-xy-step-name)` (Markdown auto-creates anchors from headings)
   - Example: `#### Step 4.3: E2E тесты` → `#step-43-e2e-тесты`
   - For steps with special characters, use the exact heading text and let Markdown generate the anchor
   - To find the correct anchor, look at the actual heading in the document and use the format shown above

**Formatting rules:**
- Use exact status icons as defined in "📐 Formatting Reference" section above
- Follow structure: Phase → Step → What/Why/Where/Completion criteria
- Use consistent phase/step numbering (Phase X, Step X.Y)
- Links to other artifacts use `@[ARTIFACT_NAME]` notation
- Metadata fields must be updated when status changes

**Technical Update Procedures:**

When updating this artifact, especially for long lists of phases and steps, follow these technical procedures:

1. **Determine if list is "long":**
   - Count elements: more than 3-5 phases OR more than 3-5 steps within a phase
   - Estimate content size: more than 50-100 lines of content for all phases/steps OR more than 3-5 KB of data
   - If matches ANY of these criteria → use sequential filling

2. **Sequential filling for PLAN:**
   - **Phases:** Create phases one at a time (one phase per iteration) via `search_replace`
   - **Steps:** Within each phase, create steps one at a time (one step per iteration) via `search_replace`
   - **MANDATORY:** After each phase/step, verify success via `read_file`
   - Example: If plan contains 3 phases with 5 steps each → create phase 1, verify, create steps of phase 1 (one by one), verify each step, then proceed to phase 2

3. **Success verification after each element:**
   - `read_file` to verify file exists
   - Verify that file is not empty
   - Verify that element was added correctly (file contains the new phase/step, structure is preserved)
   - If verification fails → retry with the same element (maximum 1-2 times)
   - If after 1-2 attempts element not added → continue with next element (do not block entire process)

**For detailed information:** See "Sequential Content Filling for Long Lists" section in system prompt (impl-planner.agent.md or vibe-coder.agent.md) or PROMPT_ENGINEERING_KNOWLEDGE_BASE.md

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

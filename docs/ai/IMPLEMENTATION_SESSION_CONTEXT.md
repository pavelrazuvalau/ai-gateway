# Current Session Context

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Universal operational memory for managing current task state  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) contain data AND copied instructions (for self-sufficiency). Instructions section will be copied from this template.  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

**Universal Usage:**
- **Simplified Workflow**: Primary artifact (only artifact needed for trivial tasks)
- **Full Workflow**: Operational memory during planning (intermediate results) and execution (current state)
- **Planning Phase**: Store intermediate analysis results
- **Execution Phase**: Track current work state

---

## Current Session

**Quick Reference:** 
- **For Simplified Workflow**: This is the primary artifact (no PLAN needed for trivial tasks)
- **For Full Workflow**: This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT)
- For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

**Date:** YYYY-MM-DD  
**Task Type:** [Trivial | Complex]  
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

## Analysis Context (Where Agent is Looking)

**Purpose**: This section provides visibility into where the agent is looking for information, what files are being analyzed, and what search queries are being used. This is critical for developers to understand the agent's focus and provide guidance if needed.

### Files Analyzed
- `file1.[ext]` - [what was analyzed, what was found]
- `file2.[ext]` - [what was analyzed, what was found]

### Search Queries Used
- **codebase_search**: "[query]" - [what was searched for, what was found]
- **grep**: "[pattern]" - [what pattern was searched, what was found]

### Directions Explored
- [Direction 1] - [what part of codebase was explored, why, what was found]
- [Direction 2] - [what part of codebase was explored, why, what was found]

### Key Findings from Analysis
- [Finding 1] - [what was discovered, where it was found]
- [Finding 2] - [what was discovered, where it was found]

**Important**: Update this section after each analysis step to show developers where you're looking and what you're finding. This allows them to guide you if you're looking in the wrong places or missing important context.

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

**For Full Workflow only:**
- **PLAN:** Phase X, Step Y
- **QUESTIONS:** [Active questions if any]
- **CHANGELOG:** Last entry - Phase X, Step Y

**For Simplified Workflow:**
- No PLAN exists (this is the primary artifact)
- Add links to related files or code if needed

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
- Move to CHANGELOG when step completes (all temporary notes and decisions should be moved)

**Intermediate Decisions:**
- Format: `- [Decision] - [rationale]`
- Document decisions made during work
- Move to CHANGELOG when step completes (all temporary notes and decisions should be moved)

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

- Update this file during work (both planning and execution phases)
- **For Simplified Workflow**: This is the primary artifact - contains all task information
- **For Full Workflow**: This is operational memory - complements PLAN, CHANGELOG, QUESTIONS
- Clear temporary information when task completes or new session starts
- Use for quick navigation to current context
- **Minimize context clutter**: Store only current, relevant information
- **Cleanup after completion**: Remove temporary notes and intermediate decisions after task completion
- Maximum 5 entries in "Last Actions"

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

**Universal Usage:**
- **Simplified Workflow**: SESSION_CONTEXT is the primary artifact (no PLAN, CHANGELOG, or QUESTIONS needed for trivial tasks)
- **Full Workflow**: SESSION_CONTEXT is part of a 4-artifact system that works together:
  1. **PLAN** (`*_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
  2. **CHANGELOG** (`*_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
  3. **QUESTIONS** (`*_QUESTIONS.md`) - Knowledge base for doubts and solutions. Contains active questions (blockers) and resolved questions.
  4. **SESSION_CONTEXT** (`*_SESSION_CONTEXT.md`) - Current work state. Contains temporary notes, intermediate decisions, and active context.

**Artifact Relationships:**
- **For Full Workflow**:
  - PLAN references blockers in QUESTIONS and recent changes in CHANGELOG
  - CHANGELOG entries link to PLAN steps and related questions in QUESTIONS
  - QUESTIONS link to PLAN steps and CHANGELOG entries where solutions were applied
  - SESSION_CONTEXT tracks current PLAN phase/step and active questions
- **For Simplified Workflow**:
  - SESSION_CONTEXT contains all task information (task description, files to change, action plan)
  - No other artifacts needed

**When to update artifacts:**
- **For Full Workflow**:
  - **PLAN**: When step status changes, when starting/completing steps, when blocked
  - **CHANGELOG**: When step completes, when question is resolved, when approach changes
  - **QUESTIONS**: When creating new question, when answering question
  - **SESSION_CONTEXT**: During planning (intermediate analysis results), when starting step, when discovering blocker, when completing step, when making intermediate decisions
- **For Simplified Workflow**:
  - **SESSION_CONTEXT**: When gathering context, when making changes, when completing task

**How to read artifacts (created from this template):**
1. Check "Current Session" for current focus and goal
2. Review "Work State" for recent actions (last 5)
3. Check "Active Context" for files in focus and target structure
4. **Review "Analysis Context" for visibility into where agent is looking** (files analyzed, search queries, directions explored)
5. Review "Temporary Notes" and "Intermediate Decisions" for context
6. Check "Artifact Links" for current phase/step and active questions
7. Review "Next Steps" for immediate actions

**How to update artifacts (created from this template):**

**For Simplified Workflow:**
1. When gathering context → update:
   - "Current Session": Date, Task Type (Trivial), Focus, Goal
   - "Active Context": Files analyzed, context gathered
   - "Analysis Context": Files analyzed, search queries used, directions explored, key findings
   - "Temporary Notes": Key findings from analysis
2. When creating action plan → update:
   - "Next Steps": Simple action plan (1-3 steps)
   - "Active Context": Files to be changed
3. When making changes → update:
   - "Work State": Add action with status
   - "Active Context": Update with changes made
4. When completing task → cleanup:
   - Remove all temporary information
   - Keep only essential results (if needed)
   - Clear "Temporary Notes" and "Intermediate Decisions"

**For Full Workflow:**
1. During planning (intermediate results) → update:
   - "Current Session": Date, Task Type (Complex), Focus, Goal
   - "Analysis Context": Files analyzed, search queries used, directions explored, key findings (CRITICAL: show where you're looking)
   - "Temporary Notes": Analysis findings
   - "Intermediate Decisions": Decisions made during analysis
2. After planning complete → update:
   - "Artifact Links": Link to PLAN (first phase, first step)
   - "Next Steps": First step from PLAN
3. When starting new step → update:
   - "Current Session": Date, Focus, Goal
   - "Artifact Links": Current PLAN phase/step
   - "Next Steps": Immediate actions
4. When discovering blocker → document:
   - "Work State": Add blocker action
   - "Temporary Notes": Blocker details
   - "Artifact Links": Link to created question
5. When completing step → cleanup:
   - Move relevant info from SESSION_CONTEXT to CHANGELOG
   - Clear temporary notes (move to CHANGELOG when step completes)
   - Clear intermediate decisions (move to CHANGELOG when step completes)
   - Remove completed actions from "Last Actions"
   - Update "Artifact Links" to reflect completion
   - Update "Next Steps" for next step
6. When making intermediate decision → document:
   - "Intermediate Decisions": Add decision with rationale
7. Update "Last Actions" (keep last 5):
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

**Technical Update Procedures:**

When updating this artifact, especially for large sections, follow these technical procedures:

1. **Determine if section is "large":**
   - Estimate content size: more than 50-100 lines of content OR more than 3-5 KB of data
   - If matches this criteria → use sequential filling for that section

2. **Sequential filling for SESSION_CONTEXT:**
   - Large sections are created one at a time (one section per iteration) via `search_replace`
   - **MANDATORY:** After each section, verify success via `read_file`
   - Part size: 3-5 KB or 50-100 lines (same as Priority 3 incremental addition)
   - Applies only to large sections (> 50-100 lines or > 3-5 KB)

3. **Success verification after each section:**
   - `read_file` to verify file exists
   - Verify that file is not empty
   - Verify that section was added correctly (file contains the new section, structure is preserved)
   - If verification fails → retry with the same section (maximum 1-2 times)
   - If after 1-2 attempts section not added → continue with next section (do not block entire process)

**For detailed information:** See "Sequential Content Filling for Long Lists" section in system prompt (impl-planner.agent.md or vibe-coder.agent.md) or PROMPT_ENGINEERING_KNOWLEDGE_BASE.md

**Update triggers:**
- **For Simplified Workflow**:
  - Gathering context (store analysis results)
  - Creating action plan (document plan)
  - Making changes (track progress)
  - Completing task (cleanup)
- **For Full Workflow**:
  - During planning (store intermediate analysis results)
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


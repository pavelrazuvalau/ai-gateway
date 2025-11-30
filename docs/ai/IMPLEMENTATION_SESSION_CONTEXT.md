# Current Session Context

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Universal operational memory for managing current task state  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) contain data AND copied instructions (for self-sufficiency). Instructions section will be copied from this template.  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

**Universal Usage:**
- **Planning Phase**: Store intermediate analysis results (temporary, cleared after planning)
- **Execution Phase**: Track current work state (only current step, cleared after step completion)

**⚠️ CRITICAL: Short-term Memory (SESSION_CONTEXT) - Poor Memory**
- Information in SESSION_CONTEXT **is lost** without fixation to long-term memory
- Long-term memory (PLAN, CHANGELOG, QUESTIONS) - **very good**, can recall details
- **ALWAYS** fix important information to long-term memory
- Without fixation - information is **lost forever**

**Short-term Memory Principles:**
- **Only active data**: Store only information used in current step/operation
- **⚠️ Poor memory**: Information is lost without fixation to long-term memory
- **Temporary storage**: Clear after step completion (FIX critical info to long-term memory first)
- **Limited volume**: Only minimum necessary for current work
- **Current operation only**: No history, no future steps, no completed work
- **Fast access**: Quick reference to current context only

**What NOT to store (this is in other artifacts):**
- ❌ History of all actions (this is in CHANGELOG)
- ❌ All questions (this is in QUESTIONS)
- ❌ Full plan (this is in PLAN)
- ❌ Information about completed steps (this is in CHANGELOG)
- ❌ Information about future steps (this is in PLAN)

---

## Current Session

**Quick Reference:** 
- This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT)
- For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

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

## Analysis Context (Where Agent is Looking)

**Purpose**: This section provides visibility into where the agent is looking for information, what files are being analyzed, and what search queries are being used. This is critical for developers to understand the agent's focus and provide guidance when the agent is looking in wrong places or missing important context.

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
- **PLAN:** Phase X, Step Y (only reference to current step, NOT full plan information)
- **QUESTIONS:** Only current blocking question (QX.Y) if exists. If no blocking question exists, write "No blocking question"
- **CHANGELOG:** Reference to last entry (only link, NOT full entry content)

**Short-term Memory Principle:** Store only references/links to artifacts, NOT full information. Full information is in artifacts themselves (long-term memory).

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
- **FIX to long-term memory** (CHANGELOG) when step completes (all temporary notes and decisions should be fixed to long-term memory)

**Intermediate Decisions:**
- Format: `- [Decision] - [rationale]`
- Document decisions made during work
- **FIX to long-term memory** (CHANGELOG) when step completes (all temporary notes and decisions should be fixed to long-term memory)

**Artifact Links (Short-term Memory Principle - only references, not full information):**
- PLAN: Phase X, Step Y (only reference to current step)
- QUESTIONS: Only current blocking question (QX.Y) if exists
- CHANGELOG: Reference to last entry (only link, not content)

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
- Example: `#### Step 4.3: E2E Tests` → anchor `#step-43-e2e-tests`
- For headings with special characters, use the exact heading text and let Markdown generate the anchor

**Usage**:
- Use anchor links when referencing specific sections in other artifacts
- Anchor links enable both agents and humans to quickly navigate to relevant sections

**Important**: Always verify anchor links point to existing headings in the artifact.

## Work Rules (Short-term Memory Principles)

**⚠️ CRITICAL: Short-term Memory (SESSION_CONTEXT) - Poor Memory**
- Information in SESSION_CONTEXT **is lost** without fixation to long-term memory
- Long-term memory (PLAN, CHANGELOG, QUESTIONS) - **very good**, can recall details
- **ALWAYS** fix important information to long-term memory
- Without fixation - information is **lost forever**

**Short-term Memory Rules:**
- **Only current step**: Store only information needed for current step/operation
- **⚠️ Poor memory**: Information is lost without fixation to long-term memory
- **Temporary storage**: All information is temporary, cleared after step completion
- **Limited volume**: Maximum 5 entries in "Last Actions", only files in current focus
- **No history**: Do not store information about completed steps (this is in CHANGELOG - long-term memory)
- **No future**: Do not store information about future steps (this is in PLAN - long-term memory)
- **No duplicates**: Do not duplicate information from other artifacts (use links/references only)
- **⚠️ CRITICAL: Before deletion → check criticality → if critical for justification → FIX to long-term memory (PLAN/CHANGELOG/QUESTIONS) → then delete**
- **Cleanup mandatory**: After step completion → check criticality → **FIX critical info to long-term memory** (CHANGELOG/PLAN/QUESTIONS) → clear all temporary data

**Update this file during work (both planning and execution phases)**
- This is short-term memory - complements PLAN, CHANGELOG, QUESTIONS (long-term memory)
- **Minimize context clutter**: Store only information used RIGHT NOW in current step
- **⚠️ CRITICAL: Cleanup after step completion**: Check criticality → **FIX critical info to long-term memory** (PLAN/CHANGELOG/QUESTIONS) → remove all temporary information
- Maximum 5 entries in "Last Actions" (only for current work context)

---

## 🤖 Instructions for AI agent

**Important:** This section is part of the template (View layer). When creating actual artifacts (Model layer), **COPY this instruction section** into the artifact at the end of the document. This ensures that instructions for working with the artifact are always available within the artifact itself, making it self-sufficient and independent of external prompts or templates.

**⚠️ IMPORTANT FOR CREATION AGENT (planning agent):**

These instructions are for FUTURE USE by the execution agent.
DO NOT try to execute these instructions while creating the artifact.
Your job is to COPY this entire section into the artifact as-is, at the end of the document.
These instructions will be used later when working with the artifact during execution phase.
Do NOT follow "How to update" or "When to update" instructions during artifact creation.

**Contract Definition:**
- This template defines the contract for working with artifacts
- Template (View layer) = Structure and formatting rules
- Artifact (Model layer) = Data + Copied instructions (self-sufficient)
- Instructions in this section define how to work with artifacts
- Model follows contract: uses artifacts according to instructions, generates responses in expected format

**Artifact System Overview:**

SESSION_CONTEXT is part of a 4-artifact system that works together:
1. **PLAN** (`*_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
2. **CHANGELOG** (`*_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
3. **QUESTIONS** (`*_QUESTIONS.md`) - Repository for doubts and solutions. Contains active questions (blockers) and resolved questions.
4. **SESSION_CONTEXT** (`*_SESSION_CONTEXT.md`) - Current work state. Contains temporary notes, intermediate decisions, and active context.

**Artifact Relationships:**
- PLAN references blockers in QUESTIONS and recent changes in CHANGELOG
- CHANGELOG entries link to PLAN steps and related questions in QUESTIONS
- QUESTIONS link to PLAN steps and CHANGELOG entries where solutions were applied
- SESSION_CONTEXT tracks current PLAN phase/step (only reference, not full plan) and current blocking question (only reference, not all questions)

**When to update artifacts:**
- **PLAN**: When step status changes, when starting/completing steps, when blocked
- **CHANGELOG**: When step completes, when question is resolved, when approach changes
- **QUESTIONS**: When creating new question, when answering question
- **SESSION_CONTEXT**: During planning (intermediate analysis results, cleared after planning), when starting step (only current step info), when discovering blocker (only current blocker), when completing step (cleanup and **FIX critical info to long-term memory**), when making intermediate decisions (only decisions for current step)

**How to read artifacts (created from this template):**
1. Check "Current Session" for current focus and goal
2. Review "Work State" for recent actions (last 5)
3. Check "Active Context" for files in focus and target structure
4. **Review "Analysis Context" for visibility into where agent is looking** (files analyzed, search queries, directions explored)
5. Review "Temporary Notes" and "Intermediate Decisions" for context
6. Check "Artifact Links" for current phase/step reference and current blocking question reference (not full information)
7. Review "Next Steps" for immediate actions

**How to update artifacts (created from this template):**

1. During planning (intermediate results) → update:
   - "Current Session": Date, Focus, Goal
   - "Analysis Context": Files analyzed, search queries used, directions explored, key findings (CRITICAL: show where you're looking)
   - "Temporary Notes": Analysis findings
   - "Intermediate Decisions": Decisions made during analysis
2. After planning complete → cleanup and update:
   - **MANDATORY**: Check criticality of analysis results (needed for plan justification?)
   - **MANDATORY**: Move critical analysis results to PLAN (if needed for justification)
   - **MANDATORY**: Clear "Analysis Context" (planning complete, not needed anymore, after moving critical info)
   - **MANDATORY**: Check criticality of "Temporary Notes" (needed for plan justification?)
   - **MANDATORY**: Move critical temporary notes to PLAN (if needed for justification)
   - **MANDATORY**: Clear "Temporary Notes" (after moving critical info)
   - "Artifact Links": Link to PLAN (first phase, first step - only reference)
   - "Next Steps": First step from PLAN (only next step, not all steps)
3. When starting new step → update:
   - "Current Session": Date, Focus, Goal
   - "Artifact Links": Current PLAN phase/step
   - "Next Steps": Immediate actions
4. When discovering blocker → document (only current blocker):
   - "Work State": Add blocker action (only current blocker)
   - "Temporary Notes": Blocker details (only current blocker, will be moved to CHANGELOG)
   - "Artifact Links": Link to created question (only current blocking question reference, not all questions)
5. When completing step → cleanup (Short-term Memory cleanup principle):
   - **⚠️ CRITICAL: Short-term memory loses information without fixation**
   - **MANDATORY**: Check criticality of all information (needed for justification of decisions/approach?)
   - **MANDATORY**: **FIX critical information to long-term memory**:
     * Temporary notes → **FIX to** CHANGELOG (if critical for "Why this solution")
     * Intermediate decisions → **FIX to** CHANGELOG (if critical for "Why this solution")
     * Analysis results → **FIX to** CHANGELOG (if critical for justification)
   - **MANDATORY**: Clear "Temporary Notes" (after fixing critical info to long-term memory)
   - **MANDATORY**: Clear "Intermediate Decisions" (after fixing critical info to long-term memory)
   - Without fixation - information is **lost forever**
   - **MANDATORY**: Remove completed actions from "Last Actions" (keep only last 5, remove oldest)
   - **MANDATORY**: Clear "Analysis Context" if not needed for next step (after moving critical info)
   - **MANDATORY**: Clear "Files in Focus" if files are no longer being edited
   - Update "Artifact Links" to next step (only reference, not full information)
   - Update "Next Steps" for next step (only next step, not all future steps)
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

**For detailed information:** See "Sequential Content Filling for Long Lists" section in system prompt (planning agent or execution agent) or PROMPT_ENGINEERING_KNOWLEDGE_BASE.md

**Update triggers:**
- During planning (store intermediate analysis results)
- Starting new step (add current task focus)
- Discovering blocker (document blocker state)
- Completing step (prepare for cleanup)
- Making intermediate decision (document decision)
- Significant context change (update active context when files in focus change or target structure changes)

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


# Current Session Context

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Operational memory for current task state  
**Status:** Template file (View layer)  
**How to use:** See "🤖 Instructions for you" at the end

---

## 📍 Current Session

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

## ⏭️ Next Steps

1. ⏳ [Next step 1]
2. ⏳ [Next step 2]

---

<!-- ═══════════════════════════════════════════════════════════════════════════ -->
<!-- 🤖 AI REFERENCE SECTION - Rules, formats, and instructions below            -->
<!-- ═══════════════════════════════════════════════════════════════════════════ -->

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

**Concept**: Anchor links provide fast navigation. They enable quick jumping to specific sections within artifacts.

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
- **Poor memory**: Information is lost without fixation to long-term memory
- **Temporary storage**: All information is temporary, cleared after step completion
- **Limited volume**: Maximum 5 entries in "Last Actions", only files in current focus
- **No history**: Do not store information about completed steps (this is in CHANGELOG - long-term memory)
- **No future**: Do not store information about future steps (this is in PLAN - long-term memory)
- **No duplicates**: Do not duplicate information from other artifacts (use links/references only)
- Before deletion → check criticality → if critical for justification → FIX to long-term memory (PLAN/CHANGELOG/QUESTIONS) → then delete
- **Cleanup mandatory**: After step completion → check criticality → **FIX critical info to long-term memory** (CHANGELOG/PLAN/QUESTIONS) → clear all temporary data

**Update this file during work (both planning and execution phases)**
- This is short-term memory - complements PLAN, CHANGELOG, QUESTIONS (long-term memory)
- **Minimize context clutter**: Store only information used RIGHT NOW in current step
- **Cleanup after step completion**: Check criticality → FIX critical info to long-term memory (PLAN/CHANGELOG/QUESTIONS) → remove all temporary information
- Maximum 5 entries in "Last Actions" (only for current work context)

---

## 🤖 Instructions for you

> **Quick Reference:** This is short-term memory. Use sections above for current work state. FIX critical info to long-term memory (CHANGELOG) before cleanup.

**Template Contract:**
- Template (View layer) = Structure and formatting rules
- Artifact (Model layer) = Data + Copied instructions (self-sufficient)
- When creating artifacts: COPY this entire section into the artifact at the end

**Artifact System (4 artifacts):**

| Artifact | Purpose | Memory Type |
|----------|---------|-------------|
| PLAN | Execution roadmap | Long-term |
| CHANGELOG | Change history | Long-term |
| QUESTIONS | Blockers & solutions | Long-term |
| SESSION_CONTEXT | Current state | **Short-term** |

**⚠️ Short-term Memory Critical Rule:**
- Information is **LOST** without fixation to long-term memory
- **ALWAYS** FIX critical info to CHANGELOG before cleanup

**When to update:**
- During planning (analysis results)
- Starting step (focus, goal)
- Discovering blocker (document state)
- Completing step (**FIX to CHANGELOG** → cleanup)
- Making decisions (document rationale)

**How to update:**

| Trigger | Action |
|---------|--------|
| Start step | Update Current Session, Artifact Links, Next Steps |
| During work | Update Last Actions (max 5), Temporary Notes |
| Blocker found | Add to Work State, link to QUESTIONS |
| Complete step | **FIX critical info** → Clear temporary sections |

**Cleanup procedure:**
1. Check criticality of all temporary info
2. **FIX** critical notes/decisions → CHANGELOG
3. Clear: Temporary Notes, Intermediate Decisions, Analysis Context
4. Update: Artifact Links → next step, Next Steps

**Technical procedures:**
- Large sections: create one at a time via `search_replace`
- Verify success via `read_file` after each update

**Related artifacts:**
- `*_PLAN.md` - current phase/step
- `*_QUESTIONS.md` - active questions
- `*_CHANGELOG.md` - completed work history


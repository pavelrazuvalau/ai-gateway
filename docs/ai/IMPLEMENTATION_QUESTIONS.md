# Implementation Questions and Clarifications

## 📊 Metadata

**Artifact Version:** 2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Knowledge base (doubts and solutions)  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) should contain only data, not instructions.  
**How to use for AI agent:** See section "🤖 Instructions for AI agent" at the end of this document

---

## 🎯 Current Focus

> **Requires Your Answer:** [QX.Y: Question Title](#qxy-question-title-phase-x-step-y)  
> **Priority:** 🔴 High | 🟡 Medium | 🟢 Low  
> **Status:** ⏳ Pending

> **Note:** If no active questions requiring your answer, show: "No active questions requiring your answer"

---

## Active Questions (require answer)

**Quick Reference:** This artifact is part of a 4-artifact system (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT). For full instructions on working with this artifact, see "🤖 Instructions for AI agent" section at the end of this document.

> **📌 Note:** Questions are sorted by priorities: 🔴 High → 🟡 Medium → 🟢 Low. Within same priority, order by question numbers is preserved.

### Question Format

```
### QX.Y: [Question Title] (Phase X, Step Y)

**Phase/Step:** Phase X, Step Y  
**Creation Date:** YYYY-MM-DD  
**Priority:** 🔴 High | 🟡 Medium | 🟢 Low

**Context:**
[Detailed description of situation that caused the question]

**Question:**
[Specific question requiring clarification]

**Why important:**
[Explanation of how answer will affect further work]

**Solution options:**
1. [Option A] - pros/cons
2. [Option B] - pros/cons

**Status:** ⏳ Pending
```

**Required fields:**
- Phase/Step: Phase X, Step Y
- Creation Date: YYYY-MM-DD
- Priority: 🔴 High | 🟡 Medium | 🟢 Low
- Context: Detailed situation description
- Question: Specific question text
- Why important: Impact explanation
- Solution options: List with pros/cons (at least one option)
- Status: ⏳ Pending (for active questions)

**Question criteria:**
- Cannot be resolved by code analysis alone
- Requires user input, architectural decision, or external information
- Has clear impact on work progress
- Has at least one solution option (even if "wait for user")
- If uncertain and might hallucinate an answer → create question instead

### Example: QX.Y: [Question Title] (Phase X, Step Y)

**Phase/Step:** Phase X, Step Y  
**Creation Date:** YYYY-MM-DD  
**Priority:** 🔴 High

**Context:**
[Detailed description of situation that caused the question]

**Question:**
[Specific question requiring clarification]

**Why important:**
[Explanation of how answer will affect further work]

**Solution options:**
1. [Option A] - pros/cons
2. [Option B] - pros/cons

**Status:** ⏳ Pending

---

## Answered Questions (knowledge base)

### Answered Question Format

```
### QX.Y: [Question Title]

**Answer:** [Accepted solution]  
**Rationale:** [Why this was chosen]  
**Closing Date:** YYYY-MM-DD  
**Applied in:** [CHANGELOG entry link]
```

**Required fields:**
- Answer: Accepted solution
- Rationale: Why this solution was chosen
- Closing Date: YYYY-MM-DD
- Applied in: Link to CHANGELOG entry where solution was applied

### Example: QX.Y: [Question Title]

**Answer:** [Accepted solution]  
**Rationale:** [Why this was chosen]  
**Closing Date:** YYYY-MM-DD  
**Applied in:** Changelog entry [link]

---

## 📐 Formatting Reference

### Status Icons

**For Questions:**
- ⏳ **Pending** - Question created, waiting for answer
- ✅ **Resolved** - Question answered, solution documented, moved to resolved section

### Priority Icons

- 🔴 **High** - Blocks work, cannot proceed
- 🟡 **Medium** - Affects work, can proceed with assumptions
- 🟢 **Low** - Optimization, can proceed without answer

**Priority sorting:** Questions must be sorted by priority: 🔴 High → 🟡 Medium → 🟢 Low

### Blocker Types

🔍 **Requires user clarification** - needs clarification of context or requirements  
🏗️ **Architectural problem** - design contradiction  
🐛 **Bug discovered** - technical blocker  
📊 **Requirements unclear** - needs clarification of business logic  
🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation

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
- Example: `### Q2.1: E2E тесты - моки провайдеров` → anchor `#q21-e2e-тесты---моки-провайдеров`
- For headings with special characters, use the exact heading text and let Markdown generate the anchor

**Usage**:
- Use anchor links in "Current Focus" and "Quick Navigation" sections
- Update anchor links when current step/question changes
- Anchor links enable both agents and humans to quickly navigate to relevant sections

**Example**:
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
1. Start with section "Active Questions" to check blockers
2. Questions are sorted by priorities: 🔴 High → 🟡 Medium → 🟢 Low
3. Each question contains: Context, Question, Why important, Solution options, Status
4. Use section "Answered Questions" to search for solutions to similar problems
5. Check "Blocker Types" section to understand question categories

**How to update artifacts (created from this template):**
1. When creating new question → add to "Active Questions" section:
   - Add question with correct priority (🔴 High, 🟡 Medium, 🟢 Low)
   - Sort by priority: 🔴 → 🟡 → 🟢
   - Use format: `### QX.Y: [Title] (Phase X, Step Y)`
   - Include all required sections (see "Question Format" section above)
   - **Update "🎯 Current Focus" section** following the logic in "How to update Current Focus section" below:
     - If new question is High priority → always update Current Focus to show it
     - If new question is Medium/Low → update only if there are no higher priority questions
2. Question format: `QX.Y: [Title] (Phase X, Step Y)`
   - QX.Y: Question number (Phase X, Step Y)
   - Title: Brief descriptive title
3. Required sections for active questions:
   - Phase/Step: Phase X, Step Y
   - Creation Date: YYYY-MM-DD
   - Priority: 🔴 High | 🟡 Medium | 🟢 Low
   - Context: Detailed description of situation
   - Question: Specific question requiring clarification
   - Why important: Explanation of impact
   - Solution options: List of options with pros/cons
   - Status: ⏳ Pending
4. When answering question → move to "Answered Questions" section:
   - Update status: ⏳ Pending → ✅ Resolved
   - Add answer information:
     - Answer (accepted solution)
     - Rationale (why chosen)
     - Closing Date: YYYY-MM-DD
     - Applied in: CHANGELOG link
   - Move question from "Active Questions" to "Answered Questions"
   - Create CHANGELOG entry about resolution
   - **Update "🎯 Current Focus" section** to show next highest priority question (if any)
5. Update question status (⏳ Pending → ✅ Resolved) when answered

**How to update Current Focus section:**

**For QUESTIONS:**
1. When question is created/answered → update "🎯 Current Focus" section:
   - **If new High priority question** → always update to show it
   - **If new Medium/Low priority question** → update only if there are no higher priority active questions
   - **If High question answered** → show next High, or Medium if no High, or Low if no Medium
   - **If Medium question answered** → show next Medium, or Low if no Medium
   - **If Low question answered** → show next Low, or "No active questions" if none
   - **If no active questions** → set to "No active questions requiring your answer"
2. Logic for selecting question to display (always follow this priority order):
   - **Step 1:** Check for 🔴 High priority questions with ⏳ Pending status → show first one found
   - **Step 2:** If no High, check for 🟡 Medium priority questions with ⏳ Pending status → show first one found
   - **Step 3:** If no Medium, check for 🟢 Low priority questions with ⏳ Pending status → show first one found
   - **Step 4:** If no active questions → show "No active questions requiring your answer"
3. Format for anchor links: `[QX.Y: Question Title](#qxy-question-title-phase-x-step-y)`
   - Markdown automatically creates anchors from headings
   - Format: lowercase, spaces to hyphens, special chars removed
   - Example: `### Q2.1: E2E тесты - моки провайдеров` → `#q21-e2e-тесты---моки-провайдеров`
   - For questions with special characters, use the exact heading text and let Markdown generate the anchor
   - To find the correct anchor, look at the actual question heading in the document and use the format shown above

**Formatting rules:**
- Use exact question format as defined in "Question Format" section above
- Sort questions by priority: 🔴 High → 🟡 Medium → 🟢 Low
- Use consistent date format: YYYY-MM-DD
- Links use `@[ARTIFACT_NAME]` notation
- Status icons: ⏳ Pending, ✅ Resolved

**When to use this file:**
- When discovering blocker or unclear requirements
- When searching for solutions to similar problems
- When checking active questions before starting work
- When making architectural decisions
- When uncertain and might hallucinate an answer (create question instead)

**Related artifacts:**
- `*_PLAN.md` - for understanding question context (phase/step)
- `*_CHANGELOG.md` - for history of applied solutions
- `*_SESSION_CONTEXT.md` - for current session context

**Question Types:**
- 🔍 **Requires user clarification** - needs clarification of context or requirements
- 🏗️ **Architectural problem** - design contradiction
- 🐛 **Bug discovered** - technical blocker
- 📊 **Requirements unclear** - needs clarification of business logic
- 🤔 **Requires deeper analysis** - model is uncertain and risks hallucinating an answer; needs more thorough investigation or user confirmation

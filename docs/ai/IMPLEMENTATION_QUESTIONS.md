# Implementation Questions and Clarifications

## 📊 Metadata

**Artifact Version:** 0.2.0  
**Last Adaptation Date:** YYYY-MM-DD  
**Purpose:** Repository for doubts and solutions  
**Note:** This is a template file (View layer). Instructions below are for creating artifacts. Final artifacts (Model layer) contain data AND copied instructions (for self-sufficiency). Instructions section will be copied from this template.  
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

**Context analysis:**
- [What was analyzed: code, documentation, artifacts, SESSION_CONTEXT]
- [What was found: patterns, libraries, existing solutions]
- [Can answer be determined from context: yes/no/partially]

**Solution options:**

- [ ] **Option 1:** [Description] - pros/cons
- [x] **⭐ Option 2 (Recommended):** [Description] - pros/cons
- [ ] **Option 3:** [Description] - pros/cons

**Recommendation and justification:**
⭐ **Option X is recommended** for the following reasons:
- **Comparison with Option Y:** [Comparison]
- **Advantages of recommended option:** [Advantages]
- **When other options are preferable:** [When other options are better]

**Your answer:**
- [ ] Use one of the options above (check your choice in Solution options)
- [ ] Provide custom answer:

```
[Place for your answer]
```

**Status:** ⏳ Pending
```

**Required fields:**
- Phase/Step: Phase X, Step Y
- Creation Date: YYYY-MM-DD
- Priority: 🔴 High | 🟡 Medium | 🟢 Low
- Context: Detailed situation description
- Question: Specific question text
- Why important: Impact explanation
- **Context analysis:** Analysis of available context (code, documentation, artifacts) - MANDATORY
- **Solution options:** List with interactive checkboxes, pros/cons, when applicable (at least one option) - MANDATORY
- **Recommendation and justification:** Recommended option with justification through comparison - MANDATORY if options can be proposed based on context
- **Your answer:** Interactive markup for user response - MANDATORY
- Status: ⏳ Pending (for active questions)

**Special case: When input from user is required:**
If context analysis shows that answer cannot be determined from available context, use this format:

```
**⚠️ User input required:**
- Context analysis cannot determine the answer
- Requirements/preferences clarification needed
- Please provide your answer below:

```
[Place for your answer]
```
```

**Question criteria:**
- Cannot be resolved by code analysis alone
- Requires user input, architectural decision, or external information
- Has clear impact on work progress
- Has at least one solution option (even if "wait for user")
- If uncertain and risk hallucinating an answer (cannot determine answer from available context) → create question instead of guessing

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

**Context analysis:**
- Analyzed codebase: Found existing authentication implementation using JWT tokens in `src/auth/jwt.ts`
- Analyzed dependencies: OAuth2 library available in `package.json`
- Analyzed artifacts: No existing API keys implementation found
- **Can answer be determined from context:** Partially - can propose options based on analysis

**Solution options:**

- [ ] **Option 1: JWT Tokens**
  - **Pros:** Already used in project, aligns with current architecture, simple integration
  - **Cons:** Requires token management, may be less secure for some scenarios
  - **When applicable:** For internal APIs, when simple integration with existing system is needed

- [x] **⭐ Option 2: OAuth2 (Recommended)**
  - **Pros:** More secure approach, standardized protocol, better for external APIs, library already available
  - **Cons:** More complex implementation, requires additional configuration
  - **When applicable:** For external APIs, when high security is needed

- [ ] **Option 3: API Keys**
  - **Pros:** Simple implementation, easy to use
  - **Cons:** Less secure approach, no standardization in project
  - **When applicable:** For internal APIs with low security requirements

**Recommendation and justification:**
⭐ **Option 2 (OAuth2) is recommended** for the following reasons:
- **Comparison with Option 1 (JWT):** OAuth2 is more secure for external APIs, although JWT is easier to integrate. For a new external API, security is more important than simplicity.
- **Comparison with Option 3 (API Keys):** OAuth2 provides a standardized approach, while API Keys are less secure. OAuth2 library is already available in the project.
- **Advantages of recommended option:** Aligns with best practices for external APIs, library already available, provides high security.
- **When other options are preferable:** JWT may be preferable if quick implementation for internal API is needed. API Keys may be preferable for simple internal services.

**Your answer:**
- [x] Use one of the options above (checked Option 2 in Solution options)
- [ ] Provide custom answer:

```
[Place for your answer]
```

**Status:** ⏳ Pending

---

## Answered Questions

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
- Example: `### Q2.1: E2E Tests - Provider Mocks` → anchor `#q21-e2e-tests---provider-mocks`
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

This artifact is part of a system of 4 required artifacts that work together:

1. **PLAN** (`*_PLAN.md`) - Execution roadmap with phases and steps. Contains current status, blockers references, and navigation.
2. **CHANGELOG** (`*_CHANGELOG.md`) - History of completed changes. Contains chronological entries with what, why, and results.
  3. **QUESTIONS** (`*_QUESTIONS.md`) - Repository for doubts and solutions. Contains active questions (blockers) and resolved questions.
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
   - **Update "🎯 Current Focus" section** (see "How to update Current Focus section" below)
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
4. When answering question → **MOVE to "Answered Questions" section (NOT copy!)**:
   - Update status: ⏳ Pending → ✅ Resolved
   - Add answer information:
     - Answer (accepted solution)
     - Rationale (why chosen)
     - Closing Date: YYYY-MM-DD
     - Applied in: CHANGELOG link
   - **REMOVE question from "Active Questions" section** (delete the entire question block)
   - **ADD question with answer to "Answered Questions" section**
   - ⚠️ Question must NOT appear in both sections!
   - Create CHANGELOG entry about resolution
   - **Update "🎯 Current Focus" section**: If another active question exists → show next highest priority question, if no active questions → show "No active questions requiring your answer"
5. Update question status (⏳ Pending → ✅ Resolved) when answered

**How to update Current Focus section:**

**Simple rule:** Show the highest priority active question (first question with ⏳ Pending status, in priority order: 🔴 High → 🟡 Medium → 🟢 Low).

**Procedure:**
1. Find first active question (⏳ Pending) in priority order: 🔴 High → 🟡 Medium → 🟢 Low
2. Update "🎯 Current Focus" section with that question's link and priority
3. If no active questions → show "No active questions requiring your answer"

**Examples:**

**Example 1: High priority question**
```
## 🎯 Current Focus

> **Requires Your Answer:** [Q2.1: Database migration strategy](#q21-database-migration-strategy-phase-2-step-1)
> **Priority:** 🔴 High
> **Status:** ⏳ Pending
```

**Example 2: Medium priority question (no High priority)**
```
## 🎯 Current Focus

> **Requires Your Answer:** [Q3.2: API endpoint naming](#q32-api-endpoint-naming-phase-3-step-2)
> **Priority:** 🟡 Medium
> **Status:** ⏳ Pending
```

**Example 3: No active questions**
```
## 🎯 Current Focus

> **Note:** No active questions requiring your answer
```

**Anchor link format:** `[QX.Y: Question Title](#qxy-question-title-phase-x-step-y)` (Markdown auto-creates anchors from headings)

**Formatting rules:**
- Use exact question format as defined in "Question Format" section above
- Sort questions by priority: 🔴 High → 🟡 Medium → 🟢 Low
- Use consistent date format: YYYY-MM-DD
- Links use `@[ARTIFACT_NAME]` notation
- Status icons: ⏳ Pending, ✅ Resolved

**Technical Update Procedures:**

When updating this artifact, especially for long lists of questions, follow these technical procedures:

1. **Determine if list is "long":**
   - Count elements: more than 3-5 questions
   - Estimate content size: more than 50-100 lines of content for all questions OR more than 3-5 KB of data
   - If matches ANY of these criteria → use sequential filling

2. **Sequential filling for QUESTIONS:**
   - Create questions one at a time (one question per iteration) via `search_replace`
   - **MANDATORY:** After each question, verify success via `read_file`
   - Example: If need to add 4 questions → create question 1, verify, create question 2, verify, etc.

3. **Success verification after each element:**
   - `read_file` to verify file exists
   - Verify that file is not empty
   - Verify that question was added correctly (file contains the new question, structure is preserved)
   - If verification fails → retry with the same question (maximum 1-2 times)
   - If after 1-2 attempts question not added → continue with next question (do not block entire process)

**For detailed information:** See "Sequential Content Filling for Long Lists" section in system prompt (planning agent or execution agent) or PROMPT_ENGINEERING_KNOWLEDGE_BASE.md

**When to use this file:**
- When discovering blocker or unclear requirements
- When searching for solutions to similar problems
- When checking active questions before starting work
- When making architectural decisions
- When uncertain and risk hallucinating an answer (cannot determine answer from available context) → create question instead of guessing

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

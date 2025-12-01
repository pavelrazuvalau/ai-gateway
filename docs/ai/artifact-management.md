# Artifact Management System Prompts

**Version:** 0.5.0  
**Date:** 2025-12-01  
**Purpose:** Documentation explaining the artifact management system architecture with separation of concerns

---

## Context and Design Philosophy

**Target Use Case**: This system is designed for serious projects where developers want to avoid monotonous work but need to maintain control over every step. Developers want to guide the model at intermediate stages and have a clear view of where the agent is looking for information based on business requirements.

**Key Design Principles:**

1. **Developer Control**: Frequent stops and checkpoints allow developers to:
   - Review intermediate results and provide guidance
   - Correct the agent's understanding if needed
   - Provide additional context or clarification
   - Redirect the agent's focus if it's looking in wrong places

2. **Visibility into Agent's Focus**: The system provides clear visibility into:
   - What files the agent is analyzing
   - What search queries are being used
   - What directions the analysis is taking
   - What findings are being discovered

3. **Preventing Deep Dives Without Context**: Frequent stops prevent:
   - Going too deep into analysis without checking if on the right track
   - Wasting time analyzing irrelevant parts of the codebase
   - Missing important business context that developers could provide
   - Creating plans based on incomplete or incorrect understanding

4. **Intermediate Results Preservation**: Frequent stops with SESSION_CONTEXT updates ensure:
   - Intermediate findings are preserved even if something goes wrong
   - Progress is visible and trackable
   - Developers can see the agent's thought process and reasoning
   - Context can be corrected or enriched at any point

---

## Overview

The artifact management system follows MVC-like architecture with clear separation of concerns:

1. **System Prompts (Controller)** - Logic, procedures, workflow
   - **`impl-planner.agent.md`** (v0.5.0) - Planning and artifact creation (frequent stops for developer control)
   - **`vibe-coder.agent.md`** (v0.5.0) - Execution and artifact maintenance (frequent stops for developer control)

2. **Template Files (View)** - Formatting, structure, presentation
   - `docs/ai/IMPLEMENTATION_PLAN.md` - PLAN artifact template
   - `docs/ai/IMPLEMENTATION_CHANGELOG.md` - CHANGELOG artifact template
   - `docs/ai/IMPLEMENTATION_QUESTIONS.md` - QUESTIONS artifact template
   - `docs/ai/IMPLEMENTATION_SESSION_CONTEXT.md` - SESSION_CONTEXT artifact template

3. **Artifacts (Model)** - Data and context
   - PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT artifacts

This separation provides clearer responsibilities, eliminates duplication, and ensures consistent formatting.

---

## When to Use Which Prompt

### Use `impl-planner.agent.md` when:

- Starting a new task from scratch
- Need to analyze codebase and create a plan
- Want to break down a task into phases and steps
- Need to create artifacts step by step (critical artifacts first, conditional artifacts as needed)
- Identifying questions and blockers upfront
- Planning phase of work

**Input**: Task description, codebase (plan draft, Jira ticket, business description)  
**Output**: Complete set of artifacts ready for execution (PLAN, SESSION_CONTEXT, optional CHANGELOG/QUESTIONS)

### Use `vibe-coder.agent.md` when:

- Artifacts already exist (created by planner or manually)
- Ready to execute tasks following a plan (or SESSION_CONTEXT for trivial tasks)
- Need to implement code changes
- Updating artifacts during work
- Handling blockers and questions during execution
- Execution phase of work

**Input**: Existing artifacts (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT)  
**Output**: Code changes and updated artifacts

---

## Workflow

### Typical Workflow

1. **Task Complexity Assessment** (use `impl-planner.agent.md`):
   - Analyze input data
   - Analyze codebase context
   - Determine: task is complex

2. **MANDATORY Context Gathering Phase**:
   - **Step 1: Analyze Codebase** (MANDATORY - use VS Code/GitHub Copilot tools):
     - Use `list_dir`, `read_file`, `codebase_search`, `grep`
     - Read key configuration files
     - Understand architecture
     - **Update SESSION_CONTEXT** with intermediate results (files analyzed, search queries used, key findings, directions explored)
     - **STOP and verify** - Provide summary using standardized format
     - **Wait for confirmation** before proceeding to Step 2
     - **VALIDATION**: Verify minimum requirements met
   - **Step 2: Understand Task Requirements** (MANDATORY):
     - Use tools to understand requirements
     - **Update SESSION_CONTEXT** with intermediate results
     - **STOP and verify** - Provide summary
     - **Wait for confirmation** before proceeding to Step 3
   - **Step 3: Break Down into Phases** (MANDATORY - based on context):
     - Use tools to identify where changes needed
     - **Update SESSION_CONTEXT** with intermediate results
     - **STOP and verify** - Provide summary
     - **Wait for confirmation** before proceeding to Step 4
   - **Step 4: Break Down into Steps** (MANDATORY - based on phases):
     - Use tools to understand implementation details
     - **Update SESSION_CONTEXT** with intermediate results
     - **STOP and verify** - Provide summary
     - **Wait for confirmation** before proceeding to Step 5
   - **Step 5: Identify Questions** (MANDATORY):
     - Note questions in SESSION_CONTEXT at ANY stage (will be moved to QUESTIONS in Step 7)
     - **VALIDATION CHECKPOINT**: Verify Steps 1-5 complete before Step 6

3. **SESSION_CONTEXT During Planning** (optional during Steps 1-5, mandatory in Step 8):
   - Can create/update SESSION_CONTEXT during Steps 1-5 for intermediate analysis results
   - Must contain **Analysis Context (CRITICAL)**: Files analyzed, search queries used, directions explored, key findings
   - This provides visibility into "where the agent is looking" for developers to review and guide
   - Must be filled in Step 8 after planning is complete

4. **Step 6: Create PLAN Artifact** (STOP after completion):
   - Create PLAN with phases and steps
   - Add instructions section ("🤖 Instructions for you") - AFTER creating all content
   - **STOP IMMEDIATELY** and provide summary
   - **Wait for user confirmation**

5. **Step 7: Create Additional Artifacts** (as needed, STOP after completion):
   - QUESTIONS (if questions exist) - create ONE at a time, wait for completion
   - CHANGELOG (if completed steps to document) - create ONE at a time, wait for completion
   - Add instructions section to each artifact - AFTER creating all content
   - **STOP** after each artifact creation

6. **Step 8: Fill SESSION_CONTEXT After Planning** (STOP after completion):
   - Ensure SESSION_CONTEXT exists (create if needed, update if exists)
   - Reflect current state of project according to new plan
   - Link to PLAN (first phase, first step)
   - Add instructions section - AFTER creating all content
   - **STOP** - Wait for confirmation before proceeding to validation

7. **Step 9: Validate and Finalize** (STOP - planning complete):
   - Run validation checklists
   - Verify all required information included
   - Verify instructions section exists in all created artifacts
   - **STOP** - Planning is complete, ready for execution

**Output**: PLAN, SESSION_CONTEXT, optional CHANGELOG/QUESTIONS

2. **Execution Phase** (use `vibe-coder.agent.md`):
   - Read existing artifacts (PLAN, SESSION_CONTEXT, QUESTIONS, CHANGELOG)
   - Follow core workflow: Analysis → Solution → Action → Documentation
   - Follow PLAN step by step
   - Implement code changes
   - **Create/modify files sequentially** (ONE at a time, wait for completion)
   - **Update artifacts sequentially** (ONE at a time, wait for completion)
   - Handle blockers by creating questions (STOP rules apply)
   - Complete steps and document in CHANGELOG
   - **STOP after completing each step** - Wait for confirmation before next step
   - **STOP after completing each phase** - Wait for confirmation before next phase
   - **STOP after answering questions** - Wait for confirmation before continuing

### Iterative Workflow

You can switch between prompts as needed:
- If new questions arise during execution → can use planner to update PLAN
- If plan needs major restructuring → can use planner to revise artifacts
- Execution can pause and resume using same artifacts

---

## Separation of Concerns

### System Prompts (Controller)
**Responsibility:** Logic, procedures, workflow, validation

**What they contain:**
- Logic: What to do, when to do it, how to validate
- Procedures: Step-by-step instructions for creating/updating artifacts
- Workflow: Analysis → Solution → Action → Documentation
- Validation: Checklists and criteria
- **Sequential Content Filling for Long Lists**: Strategy for handling large data volumes in artifacts (criteria, procedures, success verification)

**What they DON'T contain:**
- Formatting rules (icons, statuses, structure)
- Examples of formatting
- Detailed structure definitions

**Files:**
- `impl-planner.agent.md` (v0.4.0) - Planning and artifact creation (with two workflow modes, frequent stops for developer control)
- `vibe-coder.agent.md` (v0.4.0) - Execution and artifact maintenance (frequent stops for developer control)

### Template Files (View)
**Responsibility:** Formatting, structure, presentation, examples

**What they contain:**
- Formatting rules: Icons, statuses, priority indicators
- Structure definitions: Sections, metadata fields, entry formats
- Instructions: How to read, how to update, when to use
- **Technical Update Procedures**: Sequential content filling for long lists (criteria, procedures, success verification) - ensures artifacts are self-sufficient
- Examples: Format examples for each artifact type
- Formatting reference: Complete formatting guide
- Navigation sections: Quick navigation for humans (e.g., "Current Focus" section)

**What they DON'T contain:**
- Logic or procedures
- Workflow definitions
- Validation rules

**Files:**
- `docs/ai/IMPLEMENTATION_PLAN.md` - PLAN template
- `docs/ai/IMPLEMENTATION_CHANGELOG.md` - CHANGELOG template
- `docs/ai/IMPLEMENTATION_QUESTIONS.md` - QUESTIONS template
- `docs/ai/IMPLEMENTATION_SESSION_CONTEXT.md` - SESSION_CONTEXT template

### Artifacts (Model)
**Responsibility:** Data and context

**What they contain:**
- Current state: Status, progress, context
- History: Completed work, decisions, solutions
- Questions: Active and resolved questions
- Context: Current session state
- Instructions: Copied instruction section from template (for self-sufficiency)

## Key Differences

| Aspect | impl-planner.agent.md | vibe-coder.agent.md |
|--------|----------------------|---------------------|
| **Version** | 0.4.0 | 0.4.0 |
| **Focus** | Analysis and planning | Implementation and execution |
| **Input** | Task description, codebase (plan draft, Jira ticket, business description) | Existing artifacts (PLAN, CHANGELOG, QUESTIONS, SESSION_CONTEXT) |
| **Output** | PLAN + artifacts | Code changes + updated artifacts |
| **Workflow Modes** | Full workflow | Works with artifacts |
| **Status Rules** | Definitions only | Full transition rules |
| **Procedures** | Creation procedures (step by step) | Update procedures |
| **Workflow** | Full workflow (PLAN + artifacts) | Core workflow: Analysis → Solution → Action → Documentation |
| **Stop Rules** | STOP after PLAN creation, validation | STOP after step/phase completion, question resolution |
| **Artifact Creation** | PLAN first, SESSION_CONTEXT filled after planning, conditional as needed | Updates existing artifacts |
| **Sequential Operations** | Create files ONE at a time, context gathering can be parallel | Create/modify files ONE at a time, update artifacts sequentially |
| **Tools** | VS Code/GitHub Copilot tools (read_file, codebase_search, grep, list_dir, etc.) | VS Code/GitHub Copilot tools (read_file, write, search_replace, codebase_search, grep, etc.) |
| **Assumptions** | No artifacts exist | Artifacts already exist (or SESSION_CONTEXT for Simplified) |

---

## Shared Elements

Both prompts share:
- Reference to template files in `docs/ai/` directory
- Cross-artifact link format (`@[ARTIFACT_NAME]` notation)
- Anchor links for navigation (`[Text](#anchor-name)` format)
- Working without templates (instructions creation concept)
- Universalization principles
- Quality criteria (adapted for creation vs. updates)
- Key principles (adapted for planning vs. execution)
- **Sequential Operations Rules**: File creation/modification must be sequential, but context gathering can be parallel
- **Tool Usage (VS Code/GitHub Copilot)**: Explicit instructions on which tools to use (read_file, write, search_replace, codebase_search, grep, list_dir, read_lints, glob_file_search)
- **Two Workflow Modes**: Simplified (trivial tasks) and Full (complex tasks)
- **Universal SESSION_CONTEXT**: Same template for both modes and both phases (planning and execution)

**Important:** All formatting rules (icons, statuses, structure, examples) are in template files, not in system prompts.

## Key Features

### impl-planner.agent.md (v0.4.0)
- Code-first analysis approach (repository files as primary source)
- **MANDATORY Context Gathering**: Steps 1-5 must be completed before creating PLAN
  - Each step requires STOP and summary with standardized format (files analyzed, search queries, key findings, directions explored)
  - SESSION_CONTEXT updated after each step with Analysis Context (CRITICAL)
  - Wait for confirmation before proceeding to next step
- **Sequential Operations**: Create files ONE at a time, but context gathering can be parallel
- **Sequential Content Filling for Long Lists**: Strategy for handling large data volumes in artifacts (criteria: >3-5 elements OR >50-100 lines OR >3-5 KB, mandatory verification after each element)
- **Stop rules**: STOP after creating PLAN (Full), after SESSION_CONTEXT (Simplified), validation
- **Tool Usage (VS Code/GitHub Copilot)**: Explicit tools (read_file, codebase_search, grep, list_dir, glob_file_search, write, search_replace, read_lints)
- **Universal SESSION_CONTEXT**: Used in both modes and both phases (planning and execution)
- Identifies questions and blockers upfront
- **Working without templates**: Creates instructions based on artifact descriptions if templates not provided
- **Anchor links**: Supports navigation with anchor links in artifacts
- Universal and technology-agnostic
- References template files for formatting (no formatting rules in prompt)

### vibe-coder.agent.md (v0.4.0)
- **Core Workflow**: Analysis → Solution → Action → Documentation
- **Two Workflow Modes**: Works with both Simplified (SESSION_CONTEXT only) and Full (PLAN + artifacts) workflows
- **Sequential Operations**: Create/modify files ONE at a time, update artifacts sequentially, but context gathering can be parallel
- **Sequential Content Filling for Long Lists**: Strategy for handling large data volumes in artifacts (criteria: >3-5 elements OR >50-100 lines OR >3-5 KB, mandatory verification after each element)
- **Stop Rules**: Explicit rules for when to STOP (blockers, deep analysis, uncertainty, step/phase completion, question resolution)
- **Stop after step/phase completion**: Always STOP and wait for confirmation before proceeding
- **Tool Usage (VS Code/GitHub Copilot)**: Explicit tools (read_file, write, search_replace, codebase_search, grep, list_dir, read_lints, glob_file_search)
- Artifacts as source of truth
- Detailed update procedures for each artifact
- Status transition rules
- **Working without templates**: Uses instructions from artifacts (if template not provided)
- **Anchor links**: Supports navigation with anchor links in artifacts
- References template files for formatting (no formatting rules in prompt)

---

## Template Files

Both prompts reference template files in `docs/ai/`:
- `IMPLEMENTATION_PLAN.md` - PLAN artifact template
- `IMPLEMENTATION_CHANGELOG.md` - CHANGELOG artifact template
- `IMPLEMENTATION_QUESTIONS.md` - QUESTIONS artifact template
- `IMPLEMENTATION_SESSION_CONTEXT.md` - SESSION_CONTEXT artifact template

**Template files contain:**
- Complete formatting rules (icons, statuses, priority indicators)
- Structure definitions (sections, metadata fields, entry formats)
- Instructions (how to read, how to update, when to use)
- **Technical Update Procedures**: Sequential content filling for long lists (criteria, procedures, success verification) - ensures artifacts are self-sufficient
- Formatting reference (complete formatting guide)
- Examples for each artifact type
- Navigation sections (e.g., "Current Focus" for quick access to current step/question)
- Anchor links for navigation (instructions and examples)

**Template files are the source of truth for formatting and instructions.** System prompts contain only logic and procedures, with references to templates for formatting details.

**Important MVC principle:** 
- **Templates (View)** contain instructions and structure for copying into artifacts
- **Artifacts (Model)** contain data AND copied instructions (for self-sufficiency)
- When creating artifacts, **COPY the instruction section** ("🤖 Instructions for you") from templates into artifacts
- This ensures artifacts are self-sufficient and can be used independently of templates
- Instructions in artifacts are copied from templates, making templates the source of truth

---

## Migration from Old Prompt

The original `artifact-management.agent.md` (v1.0.0) combined both planning and execution. It has been split into:

- **Planning parts** → `impl-planner.agent.md`
- **Execution parts** → `vibe-coder.agent.md`

If you have existing artifacts created with the old prompt, they are compatible with the new execution prompt (`vibe-coder.agent.md`).

---

## Architecture Benefits

**Separation of Concerns:**
- System prompts focus on logic and procedures
- Template files focus on formatting, structure, and instructions (source of truth)
- Artifacts contain data AND copied instructions (for self-sufficiency)
- Instructions are copied from templates to artifacts, maintaining templates as source of truth
- Clear boundaries of responsibility

**MVC Principle:**
- **Model (Artifacts)**: Data (metadata, phases, steps, entries, questions, context) AND copied instructions
- **View (Templates)**: Formatting, structure, instructions for agents (source of truth for copying)
- **Controller (System Prompts)**: Logic, procedures, workflow

**Critical Rules:**

1. **Artifact Creation Priority**: 
   - **Critical artifacts** (always create): PLAN (permanent memory)
   - **Post-Planning artifacts**: SESSION_CONTEXT (operational memory) - can be used during planning for intermediate results, filled AFTER planning
   - **Conditional artifacts** (create only if content exists): CHANGELOG (only if completed steps), QUESTIONS (only if questions exist)
   - Do NOT create empty conditional artifacts
   - **Sequential creation**: Create files ONE at a time, wait for completion before creating next file
   - **Context gathering**: Can be parallel (reading multiple files for analysis is OK)

2. **Instructions in Artifacts**: 
   - When creating artifacts from templates, **COPY the instruction section** ("🤖 Instructions for you") from templates into artifacts
   - This includes **Technical Update Procedures** section (sequential content filling for long lists, success verification)
   - If template is NOT provided, create instructions based on artifact descriptions in system prompts
   - This ensures artifacts are self-sufficient and can be used independently
   - Templates remain the source of truth for instructions, which are copied into artifacts for convenience and independence

3. **Stop Rules**:
   - STOP after creating PLAN (with summary), additional artifacts, SESSION_CONTEXT filling, and validation
   - Execution: STOP after completing each step/phase and after answering questions
   - Always wait for confirmation before proceeding
   - After STOP, provide summary of what was done and what's next

4. **Sequential Operations Rules**:
   - Files must be created/modified sequentially, one at a time
   - Wait for each file operation to complete before starting next
   - Artifact operations are sequential: Create or update artifacts one at a time (PLAN → Wait → CHANGELOG → Wait → QUESTIONS → Wait → SESSION_CONTEXT)
   - **Sequential Content Filling for Long Lists**: When filling long lists in artifacts (>3-5 elements OR >50-100 lines OR >3-5 KB), fill one element at a time with mandatory verification after each element
   - **Context gathering can be parallel**: Reading multiple files for analysis is OK and encouraged
   - Prevents race conditions and data corruption

5. **Universal SESSION_CONTEXT**:
   - Used during planning (intermediate results) and execution (current state)
   - Operational memory (complements PLAN, CHANGELOG, QUESTIONS)
   - **Analysis Context (CRITICAL)**: Must contain files analyzed, search queries used, directions explored, key findings - provides visibility into "where the agent is looking" for developers to review and guide
   - During planning: Optional creation/update during Steps 1-5 (for intermediate analysis results), mandatory filling in Step 8 (after planning is complete)
   - Each step of context gathering (Steps 1-4) requires STOP and summary with standardized format (files analyzed, search queries, key findings, directions explored)
   - Cleanup after completion to minimize context clutter

**Maintainability:**
- Formatting changes only require template updates (instructions are copied from templates)
- Logic changes only require system prompt updates
- Templates are the source of truth for formatting and instructions
- When templates are updated, new artifacts will include updated instructions
- Existing artifacts retain their copied instructions (may need manual update if template changes significantly)
- Easier to understand and modify

**Consistency:**
- Same templates used for both planning and execution
- Consistent formatting across all artifacts
- Clear formatting reference in templates
- No conflicting formatting rules
- Instructions are copied from templates to artifacts, ensuring consistency

## Notes

- Both prompts are independent and can be used separately
- Planning prompt produces artifacts ready for execution
- Execution prompt works with any properly formatted artifacts
- Template files serve as single source of truth for formatting and instructions
- Both prompts reference templates for formatting details and instructions
- System prompts contain only logic, procedures, and workflow
- Both prompts are universal and technology-agnostic

**Critical MVC Rules:**

1. **Artifact Creation**:
     - Create critical artifact first (PLAN)
     - STOP after PLAN creation and provide summary
     - Can create/update SESSION_CONTEXT during planning (for intermediate results)
     - Fill SESSION_CONTEXT AFTER planning (reflects project state according to plan)
     - Create conditional artifacts only when content exists (CHANGELOG, QUESTIONS)
   - Create files sequentially (ONE at a time)
   - Context gathering can be parallel
   - STOP after each creation phase

2. **Instructions in Artifacts**:
   - When creating artifacts from templates, **COPY the instruction section** ("🤖 Instructions for you") from templates into artifacts
   - This includes **Technical Update Procedures** section (sequential content filling for long lists, success verification)
   - If template is NOT provided, create instructions based on artifact descriptions
   - Artifacts (Model) contain data (metadata, phases, steps, entries, questions, context) AND copied/created instructions
   - Instructions are part of templates (View) and are copied into artifacts for self-sufficiency
   - This ensures artifacts are self-sufficient and can be used independently of templates
   - Templates remain the source of truth for instructions, which are copied into artifacts
   - This maintains clean separation: Model = data + copied instructions, View = instructions/formatting (source of truth), Controller = logic

3. **Navigation**:
   - Use anchor links (`[Text](#anchor-name)`) for fast navigation within artifacts
   - Anchor links enable both agents and humans to quickly navigate to relevant sections
   - Update anchor links in "Current Focus" sections when current step/question changes

---

**End of Documentation**

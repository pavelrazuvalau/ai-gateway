# Knowledge Base: Prompt Engineering for System Prompts

**Version:** 0.4.0  
**Purpose:** Reference documentation for best practices, style guide, and proven techniques. **The knowledge base serves as an "interpreter" between the user and the system prompt** - helping people and AI agents properly formulate prompts to achieve the best results. The knowledge base contains guard rails - clear rules, criteria, and constraints for decision-making.

**⚠️ CRITICALLY IMPORTANT:** The knowledge base is a reference for proven practices, NOT a place for ongoing research during work. Current information during active research will confuse the model when updating the knowledge base (for example, project-related and general practices may be mixed in the final result). This file describes how to work with obtained information, not how to work fully autonomously. Artifact templates should follow a clear purpose.

**⚠️ IMPORTANT:** The knowledge base does NOT contain concepts for working with artifacts or project-specific templates. This is a universal reference on prompt engineering that teaches how to write prompts correctly. Specific projects with system prompts describe work with artifacts in their system prompts.

---

## 🛡️ Knowledge Base as Guard Rails

**⚠️ IMPORTANT:** This knowledge base serves as **guard rails for people and AI agents** - contains clear rules, criteria, and constraints for decision-making.

**📖 Guard Rails Definition:** See [Glossary of Terms](#glossary-of-terms) for the full definition of the term "Guard Rails" and its characteristics.

**How it works:**
- ✅ **For people:** Clear rules and decision-making criteria, best practices and anti-patterns, objective criteria instead of subjective assessments
- ✅ **For AI agents:** Objective stopping criteria (preventing overthinking), rules for preventing cyclical changes, clear guard rails for decision-making
- ✅ **Preventing undesirable behavior:** Over-optimization, cyclical changes, subjective assessments
- ✅ **Source of truth:** All sections contain proven best practices, research confirms recommendations
- ✅ **Working with obtained information:** Knowledge base describes how to work with obtained information, not how to work fully autonomously. Agents should use knowledge base as guidance when working with information.

**Key guard rails in the knowledge base:**
- [Guard Rails for Vibe Coding](#guard-rails-for-vibe-coding-on-large-projects) - Preventing cyclical changes when working with code
- [Guard Rails for Planning](#guard-rails-for-planning) - Preventing over-planning and analysis paralysis
- [When to Stop](#when-to-stop) - "Good enough" criteria
- [Sufficient Quality Gateway](#sufficient-quality-gateway) - "Good enough" checks for critical transitions
- [System Prompt Universality Principle](#universality-principle) - Universality without mentioning specific technologies

---

<a id="knowledge-base-as-input-context"></a>

### Knowledge Base as Input Context
**⚠️ CRITICALLY IMPORTANT:** Knowledge base is **input context** provided by the agent, not part of the prompt workflow.

**Key concept:**
- Knowledge base **does not participate in prompt work**, but only provides context (if available)
- Agent manages context population, including KB if available
- Instructions about working with KB **should NOT be in system prompts or templates**, since KB does not participate in prompt work
- By default, assume projects don't have KB (but don't need to mention this in prompts)

**What this means:**

**For system prompts:**
- ❌ Should NOT contain instructions about working with knowledge base
- ❌ Should NOT mention knowledge base as part of workflow
- ❌ Should NOT contain procedures for searching in knowledge base
- ✅ Can use information from knowledge base if provided in context

**For artifact templates:**
- ❌ Should NOT contain instructions about working with knowledge base
- ❌ Should NOT mention knowledge base as part of workflow
- ✅ Can reference knowledge base as a reference source (if needed)

**For agents:**
- ✅ Manage context population, including KB if available
- ✅ Decide when and what information from KB to provide to the model
- ✅ Don't pass instructions about working with KB to the system prompt

**Why this matters:**
- System prompts should be universal and work without knowledge base
- Knowledge base is an optional resource that may or may not be available
- Instructions about working with KB in prompts create dependency on KB availability
- Agent should manage context, not the prompt

**Practical conclusions:**
1. **When creating system prompts:**
   - Don't mention knowledge base as part of workflow
   - Don't add instructions for searching in knowledge base
   - Use universal formulations that work with or without context

2. **When working with knowledge base:**
   - Agent decides when to provide information from KB
   - Agent manages searching and extracting information from KB
   - Model works with provided context without knowing where it came from

3. **When updating knowledge base:**
   - Knowledge base is updated outside of prompt workflow
   - Updates don't require changes to system prompts
   - Knowledge base remains an independent resource

**Sources:**
- [Separation of Responsibilities: Agent and Model](#agent-model-separation) - Definition of working contract between agent and model

**Related sections:**
- [Separation of Responsibilities: Agent and Model](#agent-model-separation) - What the model knows, what the agent controls
- [Nature of System Prompt](#system-prompt-nature) - Instructions for decision-making, not a program
- [Strategy for Working with Knowledge Base as Database](#knowledge-base-strategy-db) - Indexing and efficient search

---

## 📚 Table of Contents

**Critical sections (read first):**
- [📖 Glossary of Terms](#glossary-of-terms) - **Defines the language of communication** - read first to understand terminology

**🧭 Navigation and Knowledge Base Updates (for AI agents):**
- [Where to Add New Information](#where-to-add-content) - Procedure for determining location for new information
- [New Section Template](#section-template) - Formalized section structure
- [Knowledge Base Categories Map](#kb-categories-map) - Taxonomy of topics and their boundaries
- [Criteria for Adding Information to KB](#kb-addition-criteria) - What can and cannot be added

**Main sections:**
1. [Style Guide for System Prompts](#style-guide) - Writing principles and system prompt structure
2. [Common Mistakes in System Prompts](#common-mistakes) - Top-10 mistakes and how to avoid them
3. [Best Practices](#best-practices) - Recommendations for creating effective prompts
   - [Working with Tools and Creating Files](#file-creation-best-practices) - Multi-level file creation strategy, success verification, state preservation
4. [Prompting Techniques](#prompting-techniques) - Chain-of-Thought, Few-shot, Zero-shot and other techniques
   - [Thinking Tags](#thinking-tags) - Explicit separation of reasoning and result through tags
   - [Self-Consistency](#self-consistency) - Multiple reasonings with consistent answer selection
   - [Tree of Thoughts](#tree-of-thoughts) - Branching reasoning tree with path evaluation
5. [Prompt Security](#security) - Prompt injection, Jailbreaking, attack protection
   - [Hallucination Prevention](#hallucination-prevention) - Strategies for combating unreliable generation
6. [Structured Output](#structured-output) - JSON mode, Structured Outputs, obtaining structured data
7. [Anti-Patterns](#anti-patterns) - What to avoid when writing prompts
8. [Conditional Logic in Prompts](#conditional-logic) - When and how to use conditions in prompts
9. [Model-Specific Optimization](#model-optimization) - Balance between optimization and universality
10. [Instruction Duplication](#duplication) - When duplication is justified and when it's not
11. [Using Templates in Prompts](#template-usage) - Universal practices for working with templates

**Guard Rails and Quality Criteria:**
- [When to Stop](#when-to-stop) - **Core principles** of "good enough" criteria and improvement prioritization
- [Informing About Further Development Direction](#informing-about-further-development-direction) - Informing user about optional improvements when "good enough" criteria is met
- [Sufficient Quality Gateway](#sufficient-quality-gateway) - Systematic "good enough" checks for critical transitions (applies principles from "When to Stop")
- [Guard Rails for Vibe Coding](#guard-rails-for-vibe-coding-on-large-projects) - Preventing cyclical changes when working with code (applies principles from "When to Stop")
- [Guard Rails for Planning](#guard-rails-for-planning) - Preventing over-planning and analysis paralysis during planning

**Working with templates and artifacts:**
- [Using Templates in Prompts](#template-usage) - Universal principles for working with templates, including the "storage + contract" concept

**Prompt Structure and Components:**
- [Nature of System Prompt](#system-prompt-nature) - System prompt as instructions for decision-making, not a program
- [Separation of Responsibilities: Agent and Model](#agent-model-separation) - What the model knows, what the agent controls, practical conclusions for system prompts
- [Role Definition in System Prompts](#role-definition-structure) - Optimal structure and components of role definition (practical application of Role-based Prompting technique)
- [Role-based Prompting](#prompting-techniques) - Prompting technique (see also "Role Definition" for system prompts)
- [System Prompt Length](#system-prompt-length) - Principles for working with system prompt length and optimality assessment criteria

**Practical Recommendations:**
- [Conclusions and Recommendations for AI Agents](#ai-generated-prompts) - Practical guide for using the knowledge base
- [Output Size Optimization in Tokens](#output-size-optimization) - Strategies for controlling and optimizing AI agent output size

**Research and Specialized Sections:**
- [Research: Knowledge Base Universalization for AI Agents](#universalization-research) - Preparation for universalization and navigation optimization
- [Research: File Operations Strategies](#file-operations-research) - Strategies for optimized file operations with standard development tools
- [Agent-Agnostic Knowledge Base and Coding Agent Tools](#agent-agnostic-knowledge-base) - Universal tools and approaches
- [Strategy for Working with Knowledge Base as Database](#knowledge-base-strategy-db) - Indexing and efficient search
- [Deep Investigation Mechanism in System Prompts](#deep-investigation-mechanism) - Using internal resources to justify decisions
- [Reference File Structuring](#reference-files-structure) - General structuring practices for quick search
- [Agent Architecture: Separate vs Combined](#agent-architecture-separation) - Optimal system prompt architecture
- [Agent Loop Patterns](#agent-loop-patterns) - Loop patterns for iterative task execution by agents
- [System Prompt Consistency Checklist](#system-prompt-consistency) - Consistency validation procedures
- [Open Questions for Further Research](#open-questions) - Completed research and their conclusions

---

<a id="where-to-add-content"></a>

## 📝 Where to Add New Information (for AI agents)

**Purpose:** Determine the correct location for adding new information to the Knowledge Base  
**When to use:** When adding new information (best practices, anti-patterns, research, guard rails)  
**Related sections:** [New Section Template](#section-template), [Categories Map](#kb-categories-map), [Addition Criteria](#kb-addition-criteria), [Strategy for Working with Knowledge Base](#knowledge-base-strategy-db)

---

### 🤖 Instructions for you

**How to use this section:**
- When adding new information → follow the procedure for determining location
- When uncertain → use the categories map to determine the topic
- After adding → update Table of Contents

---

### Procedure for Determining Location for New Information

**Step 1: Determine information type**

| Information Type | Target Section | Anchor |
|-----------------|----------------|--------|
| Best Practice (proven practice) | Best Practices | `#best-practices` |
| Anti-Pattern (what to avoid) | Anti-Patterns | `#anti-patterns` |
| Prompting Technique | Prompting Techniques | `#prompting-techniques` |
| Guard Rail (constraint/rule) | Corresponding Guard Rails section | See categories map |
| Common Mistake | Common Mistakes | `#common-mistakes` |
| Research (completed) | Open Questions | `#open-questions` |
| New Term | Glossary of Terms | `#glossary-of-terms` |

**Step 2: Check existing sections**

```
1. Use grep to search for similar topic:
   grep -pattern "keyword" [knowledge_base_path]
   
2. Read found section metadata:
   - Purpose: does new information match section purpose?
   - When to use: does context fit?
   
3. If matching section found → add to it
   If no matching section → create new one using template
```

**Step 3: Make decision**

```
✅ ADD to existing section if:
- Topic matches section purpose (from metadata)
- Information supplements existing content
- Doesn't create duplication

✅ CREATE new section if:
- No matching existing section
- Topic is broad enough for separate section (> 50 lines of content)
- Topic is not a subtopic of existing section

❌ DO NOT ADD if:
- Information already exists (check via grep)
- Information is project-specific (not universal)
- Information is not verified (see addition criteria)
```

**Step 4: After adding**

1. **Update Table of Contents** (if new section created):
   - Find corresponding group in contents (lines 97-156)
   - Add link in format: `- [Name](#anchor) - Brief description`

2. **Add connections**:
   - Add links to "Related sections" of new section
   - Add back-links in related sections (if appropriate)

3. **Check integrity**:
   - Anchor link works
   - Format matches section template

---

### Procedure for Updating Table of Contents

**When to update:**
- After creating new section
- After renaming existing section
- After deleting section

**Where to add link (by content type):**

| Content Type | ToC Group |
|--------------|-----------|
| KB Navigation | "🧭 Navigation and Knowledge Base Updates" |
| Guard Rails | "Guard Rails and Quality Criteria" |
| Prompting Techniques | "Main sections" (item 4) |
| Best Practices | "Main sections" (item 3) |
| Prompt Structure | "Prompt Structure and Components" |
| Research | "Research and Specialized Sections" |
| Practical Recommendations | "Practical Recommendations" |

**ToC entry format:**
```markdown
- [Section Name](#anchor-name) - Brief description (up to 100 characters)
```

---

<a id="section-template"></a>

## 📋 New Section Template

**Purpose:** Ensure uniform section structure in the Knowledge Base  
**When to use:** When creating a new section in the Knowledge Base  
**Related sections:** [Where to Add New Information](#where-to-add-content), [Reference File Structuring](#reference-files-structure)

---

### 🤖 Instructions for you

**How to use this section:**
- When creating new section → copy template and fill in
- All fields **Purpose**, **When to use**, **Related sections** are required
- Section "🤖 Instructions for you" is required for sections used by agents

---

### Required Section Structure

```markdown
<a id="unique-anchor-name"></a>

## [Emoji] Section Name

**Purpose:** [One sentence: what the section does/is for]  
**When to use:** [Criteria: when to refer to this section]  
**Related sections:** [Links to 2-5 related sections]

**Context:** [Optional: additional context if needed]

---

### 🤖 Instructions for you

**How to use this section:**
- When [scenario 1] → [action]
- When [scenario 2] → [action]
- When [scenario 3] → [action]

**Sources:**
- [Source 1](URL) - Brief description
- [Source 2](URL) - Brief description

---

### [Subsection 1: Main Content]

[Section content]

### [Subsection 2]

[Content]

---

### Conclusions

**Key principles:**
1. [Principle 1]
2. [Principle 2]
3. [Principle 3]

**Practical recommendations:**
- [Recommendation 1]
- [Recommendation 2]

---
```

### Template Filling Rules

**Anchor link (`<a id="..."></a>`):**
- Use lowercase with hyphens: `my-section-name`
- Unique within the file (check via `grep -pattern 'id="anchor"'`)
- No spaces or special characters

**Emoji in heading:**
- 📋 — Guides, templates, structure
- 🎯 — Best Practices, recommendations
- 🚫 — Anti-Patterns, mistakes
- 🔒 — Security
- 🛑 — Guard Rails, constraints
- 🧠 — Techniques, methods
- 📊 — Data, metrics, output
- 🔬 — Research
- 📖 — References, glossaries
- 💡 — Conclusions, recommendations

**Section metadata:**
- **Purpose** — one sentence, starts with a verb
- **When to use** — specific scenarios/criteria
- **Related sections** — 2-5 links to relevant sections

**Section "🤖 Instructions for you":**
- Required for sections that AI agents use
- Format: "When [scenario] → [action]"
- 3-5 specific usage scenarios

---

<a id="kb-categories-map"></a>

## 🗺️ Knowledge Base Categories Map

**Purpose:** Provide topic taxonomy for quick orientation when adding/searching for information  
**When to use:** When determining location for new information, when searching for relevant section  
**Related sections:** [Where to Add New Information](#where-to-add-content), [Strategy for Working with Knowledge Base](#knowledge-base-strategy-db)

---

### 🤖 Instructions for you

**How to use this section:**
- When adding information → find category by topic
- When searching for information → determine category and use anchors
- When uncertain → start from top level and descend

---

### Category Hierarchy

```
Knowledge Base
├── 🧭 Navigation and meta (this section)
│   ├── Where to add information
│   ├── Section template
│   ├── Categories map
│   └── Addition criteria
│
├── 📖 Basics (read first)
│   ├── Glossary of Terms (#glossary-of-terms)
│   └── Style Guide (#style-guide)
│
├── 📋 Prompt Structure
│   ├── Nature of System Prompt (#system-prompt-nature)
│   ├── Separation of Responsibilities (#agent-model-separation)
│   ├── Role Definition (#role-definition-structure)
│   └── Prompt Length (#system-prompt-length)
│
├── 🎯 Best Practices (#best-practices)
│   ├── Working with Tools (#file-creation-best-practices)
│   ├── Using Templates (#template-usage)
│   └── Instruction Duplication (#duplication)
│
├── 🚫 Problems and Mistakes
│   ├── Common Mistakes (#common-mistakes)
│   ├── Anti-Patterns (#anti-patterns)
│   └── Conditional Logic (#conditional-logic)
│
├── 🧠 Prompting Techniques (#prompting-techniques)
│   ├── Zero-shot, Few-shot, Chain-of-Thought
│   ├── Role-based Prompting
│   ├── Thinking Tags (#thinking-tags)
│   ├── Self-Consistency (#self-consistency)
│   └── Tree of Thoughts (#tree-of-thoughts)
│
├── 🛑 Guard Rails
│   ├── When to Stop (#when-to-stop) ← FOUNDATION
│   ├── Sufficient Quality Gateway (#sufficient-quality-gateway)
│   ├── Guard Rails for Vibe Coding (#guard-rails-for-vibe-coding-on-large-projects)
│   └── Guard Rails for Planning (#guard-rails-for-planning)
│
├── 🔒 Security (#security)
│   ├── Prompt Injection
│   ├── Jailbreaking
│   ├── Data Leakage
│   └── Hallucination Prevention (#hallucination-prevention)
│
├── 📊 Output and Data
│   ├── Structured Output (#structured-output)
│   └── Output Size Optimization (#output-size-optimization)
│
├── 💡 Practical Recommendations
│   ├── Conclusions for AI Agents (#ai-generated-prompts)
│   └── Model-Specific Optimization (#model-optimization)
│
└── 🔬 Research
    ├── Universalization (#universalization-research)
    ├── File Operations Strategies (#file-operations-research)
    ├── Agent-Agnostic KB (#agent-agnostic-knowledge-base)
    ├── Working with KB as DB (#knowledge-base-strategy-db)
    ├── Deep Investigation (#deep-investigation-mechanism)
    ├── File Structuring (#reference-files-structure)
    ├── Agent Architecture (#agent-architecture-separation)
    ├── Agent Loop Patterns (#agent-loop-patterns)
    ├── Prompt Consistency (#system-prompt-consistency)
    └── Open Questions (#open-questions)
```

### Quick Topic Search

| If information about... | Search in category | Main anchor |
|------------------------|-------------------|-------------|
| How to write prompts | 📋 Prompt Structure | `#style-guide` |
| What to do | 🎯 Best Practices | `#best-practices` |
| What not to do | 🚫 Problems and Mistakes | `#anti-patterns` |
| When to stop | 🛑 Guard Rails | `#when-to-stop` |
| Improvement techniques | 🧠 Techniques | `#prompting-techniques` |
| Attack protection | 🔒 Security | `#security` |
| Output format | 📊 Output | `#structured-output` |
| Terminology | 📖 Basics | `#glossary-of-terms` |

---

<a id="kb-addition-criteria"></a>

## ✅ Criteria for Adding Information to Knowledge Base

**Purpose:** Determine what can and cannot be added to the Knowledge Base  
**When to use:** Before adding new information to verify compliance with criteria  
**Related sections:** [Where to Add Information](#where-to-add-content), [Sufficient Quality Gateway](#sufficient-quality-gateway), [When to Stop](#when-to-stop)

---

### 🤖 Instructions for you

**How to use this section:**
- Before adding information → check all criteria below
- When in doubt → information is NOT added to KB
- After adding → verify through checklist

---

### Compliance Criteria

**✅ ADD to Knowledge Base:**

| Criterion | Description | Example |
|-----------|-------------|---------|
| Universality | Applicable to any project, not project-specific | "Use Chain-of-Thought for complex tasks" |
| Verification | Confirmed by sources or practical experience | Link to research or documented experience |
| Repeatability | Applicable repeatedly, not a one-time solution | Best practice, not a workaround for a specific bug |
| Objectivity | Contains objective criteria, not subjective assessments | "Use examples for tasks with accuracy < 90%" |
| Completeness | Research/practice is complete, not in progress | Research conclusions, not current hypotheses |

**❌ DO NOT ADD to Knowledge Base:**

| Criterion | Description | Example |
|-----------|-------------|---------|
| Project-specific | Specific to a particular project | "In our project we use structure X" |
| In progress | Current research not completed | "Researching approach Y, results unknown" |
| Temporary | Workaround, not a long-term solution | "For now using hack Z" |
| Subjective | Based on subjective assessments | "It seems better to do it this way" |
| Duplication | Already exists in KB | Check via grep before adding |
| Outdated | Information is outdated or irrelevant | Practices for deprecated versions |

### Checklist Before Adding

```markdown
**Before adding to Knowledge Base:**

- [ ] Information is universal (not project-specific)
- [ ] Information is verified (has sources or documented experience)
- [ ] Information doesn't duplicate existing (checked via grep)
- [ ] Information is complete (not in research process)
- [ ] Information matches KB structure (see section template)
- [ ] Location for adding determined (see categories map)

**After adding:**

- [ ] Table of Contents updated (if new section)
- [ ] Related sections added
- [ ] Anchor link works
- [ ] Format matches template
```

### Sufficient Quality Gateway for Adding to KB

**Apply before adding:**

1. **Criteria check (above)** — all ✅ criteria met
2. **Quality check 85-90%+** — information is sufficiently complete
3. **Contradiction check** — doesn't contradict existing information in KB
4. **Format check** — matches section template

**If any criterion is not met → DO NOT add to KB.**

---

<a id="glossary-of-terms"></a>

## 📖 Glossary of Terms

**Purpose:** Ensure uniform terminology in the knowledge base  
**When to use:** When creating or updating knowledge base sections for consistent term usage

**⚠️ CRITICALLY IMPORTANT:** The glossary defines the language of communication between people and AI agents. All terms used in the knowledge base should be defined here. Read the glossary first to understand the terminology.

### Core Terms

**Prompt:** Text instruction or request passed to the model to perform a task.

**System Prompt:** A prompt that defines the role, behavior, and operating rules of an AI agent. Usually passed through a system message in the API. **Important:** A system prompt is not a program, but a set of instructions for guiding the model toward correct decision-making through many intermediate steps. It provides instructions on how to gather context and how to use decision-making principles to achieve the user's desired result. See [Nature of System Prompt](#system-prompt-nature).

**Prompt Engineering:** The process of creating and optimizing prompts to achieve desired results from the model.

**Knowledge Base:** Reference documentation containing proven practices, recommendations, and guard rails for AI agents and people.

**Guard Rails:** Predefined constraints or rules implemented in an AI system (through system prompts, knowledge base, or other mechanisms) to control model behavior and prevent generation of undesirable, harmful, or unsafe responses. Guard rails ensure that the model operates within specified parameters that comply with ethical standards, security requirements, and quality criteria.

**Key Guard Rails Characteristics:**
- **Predefinition:** Rules and constraints are established in advance, before task execution
- **Behavior Control:** Guide the model toward correct decision-making
- **Preventing Undesirable Results:** Block or redirect undesirable behavior
- **Objectivity:** Use objective criteria instead of subjective assessments
- **Explicitness:** Must be explicitly defined and available in the working context

**Guard Rails Examples:**
- "Good enough" criteria to prevent over-optimization
- Rules for preventing cyclical code changes
- Topic or content type restrictions
- Objective criteria for stopping improvements
- Safety and ethics rules

**Application in Knowledge Base Context:**
In this knowledge base, Guard Rails are used for:
- Preventing over-optimization and endless improvement cycles
- Ensuring objective decision-making criteria
- Controlling AI agent work quality
- Guiding the model toward correct behavior through clear rules

**Important:** Guard rails must be explicit and always available in the working context. They should not be hidden in links or external files that may be unavailable to the model.

**Correct usage of "Guard Rails" examples:**
- ✅ "Guard rails prevent over-optimization" - correct usage, as it refers to rules preventing undesirable behavior
- ✅ "'Good enough' criteria serve as guard rails" - correct usage, as criteria are predefined constraints
- ✅ "Guard rails for preventing cyclical changes" - correct usage, as rules control model behavior

**Incorrect usage of "Guard Rails" examples:**
- ❌ "Best practices are guard rails" - incorrect, as best practices are recommendations, not constraints
- ❌ "Documentation serves as guard rails" - incorrect, as documentation is reference information, not constraints
- ❌ "Code examples are guard rails" - incorrect, as examples are illustrations, not behavior control rules

**AI Agent:** An autonomous system based on LLM, capable of performing tasks using tools and following instructions from the system prompt.

### Terms for Working with Files

**File:** A specific file in the file system (e.g., `config.py`, `README.md`).

**Document:** A general term for any text file or artifact that may contain instructions, documentation, or data.

**Artifact:** A structured document created by an AI agent during work (e.g., plans, change logs, context files).

**Template:** A predefined file or document structure used as a base for creating new content.

### Terms for Tasks and Processes

**Task:** A general concept of work to be done. Can be simple or complex, consisting of multiple steps.

**Step:** A specific action within a task or phase. Usually has clear completion criteria.

**Phase:** A group of related steps united by a common goal or work stage.

**Workflow:** A sequence of steps and procedures for performing a task.

### Terms for Quality

**Best Practices:** Proven practices and recommendations ensuring effectiveness and quality.

**Anti-Pattern:** A pattern to avoid because it leads to problems or undesirable results.

**Sufficient Quality Gateway:** A systematic "good enough" check before critical transitions in the workflow.

**"Good Enough":** A principle stating that a solution is acceptable when it reaches a target quality level (usually 85-90%+), without the need to achieve perfection.

### Terms for Models and Technologies

**LLM (Large Language Model):** A large language model capable of understanding and generating text.

**Agent-agnostic:** A universality principle meaning that prompts and instructions work with any models and tools without being tied to specific technologies.

**Universality:** The property of prompts and instructions to work effectively with different models and environments without mentioning specific technologies.

### Usage Notes

- **"File" vs "Document":** In the context of working with the file system, use "file". In the context of documentation or artifacts, "document" can be used.
- **"Step" vs "Task":** "Step" is a specific action. "Task" is a more general concept that may include multiple steps.
- **"Prompt" vs "System Prompt":** "Prompt" is a general term. "System prompt" is a specific type of prompt for defining agent behavior.

---

<a id="style-guide"></a>

## 📋 Style Guide for System Prompts

**Purpose:** Defines the structure and principles of writing effective system prompts  
**When to use:** When creating a new system prompt or improving an existing one  
**Related sections:** [Best Practices](#best-practices), [Anti-Patterns](#anti-patterns), [Common Mistakes](#common-mistakes)

### 🤖 Instructions for you

**How to use this section:**
- When creating a prompt → follow the recommended structure (Role, Workflow, Output Management, Quality, Quick Reference)
- When writing → apply principles (clarity, structure, examples, uniformity, objectivity)
- When checking → use the checklist from section [Conclusions and Recommendations](#ai-generated-prompts)

**Sources:**
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) - Official OpenAI guide
- [Anthropic Claude Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) - Anthropic guide
- [The Prompt Canvas: A Literature-Based Practitioner Guide](https://arxiv.org/abs/2412.05127) - Practical guide for creating effective prompts (2024)
- [Awesome AI System Prompts](https://github.com/dontriskit/awesome-ai-system-prompts) - Collection of real system prompts from ChatGPT, Claude, v0, Cursor, Manus, Bolt.new and others (2025)

---

<a id="universality-principle"></a>

### System Prompt Universality Principle
**⚠️ CRITICALLY IMPORTANT:** Even if system prompts are optimized for working with specific technologies (e.g., GitHub Copilot, Claude Sonnet 4.5, Cursor IDE), the system prompts themselves should NOT mention these specific technologies.

**Why this matters:**
- Mentioning specific technologies doesn't help the model make decisions
- Mentioning specific technologies only complicates the decision-making process
- The model should focus on task execution, not technology analysis
- Universal descriptions work for all models and environments

**What should NOT be in system prompts:**
- ❌ Mentions of specific models (Claude Sonnet 4.5, GPT-4, etc.)
- ❌ Mentions of specific IDEs (Cursor IDE, VS Code, etc.)
- ❌ Mentions of specific tools (GitHub Copilot, etc.)
- ❌ Mentions of specific versions or specific capabilities

**What SHOULD be in system prompts:**
- ✅ Universal tool descriptions ("standard development tools", "available tools in your environment")
- ✅ Universal model descriptions ("modern LLMs", "compatible with various models")
- ✅ Universal principles and strategies
- ✅ Objective criteria and rules

**Examples of correct universalization:**

**❌ INCORRECT:**
```markdown
**Model Compatibility:**
- Primary: Claude Sonnet 4.5 (optimized)
- Note for Claude Sonnet 4.5: Follow instructions step-by-step

**Important:** This section uses VS Code/GitHub Copilot tools. Cursor IDE is used as development environment.
```

**✅ CORRECT:**
```markdown
**Model Compatibility:**
- Compatible with modern LLMs
- Follow instructions step-by-step without overthinking

**Important:** This section describes strategies for working with large files using standard development tools. These tools are available in most modern IDEs and development environments.
```

**Where specific technology information can remain:**
- ✅ In the knowledge base (as documentation for people)
- ✅ In code comments (if applicable)
- ✅ In project metadata (version, date, etc.)
- ❌ NOT in system prompts

**Applying the principle:**
- When creating a new system prompt: use only universal descriptions
- When updating an existing prompt: remove all mentions of specific technologies
- When optimizing for a specific model: optimize structure and formulations, but don't mention the model explicitly

---

<a id="system-prompt-nature"></a>

### Nature of System Prompt: Instructions for Decision-Making, Not a Program
**⚠️ CRITICALLY IMPORTANT:** A system prompt is **not a program**. Its task is to guide the model toward correct decision-making in many intermediate steps that the user may not be aware of.

**Key concept:**
- A system prompt provides **instructions** on how to gather context and how to use decision-making principles from that context to achieve the user's desired result
- Unlike a program that executes deterministic instructions, a system prompt **guides a probabilistic process** of text generation by the model
- A system prompt acts as a **guide**, influencing the model's decision-making process at each intermediate step

**Difference from a program:**

| **Program** | **System Prompt** |
|-------------|-------------------|
| Deterministic instruction execution | Probabilistic guidance of decision-making process |
| Clearly defined execution steps | Instructions for many intermediate steps |
| Predictable and reproducible result | Result depends on context and model's intermediate decisions |
| Executes an algorithm | Guides through a sequence of logical steps |

**How a system prompt works:**

1. **Context gathering instructions:**
   - System prompt indicates what information sources to consider
   - Defines how to analyze available data
   - Sets information relevance criteria

2. **Decision-making principles:**
   - System prompt provides rules and criteria for evaluating options
   - Defines priorities and importance of various factors
   - Sets guard rails to prevent undesirable behavior

3. **Guiding through intermediate steps:**
   - System prompt breaks complex tasks into a sequence of steps
   - Indicates when and how to pause for checking intermediate results
   - Ensures transparency of the decision-making process

**Application examples:**

**Example 1: Gathering context for codebase analysis**
```markdown
**Instruction in system prompt:**
- First analyze project structure through codebase_search
- Then study key files related to the task
- Consider documentation and existing patterns

**How it works:**
The model doesn't just execute commands, but makes decisions about:
- What search queries to use
- Which files to consider key
- How to interpret found information
```

**Example 2: Decision-making principles during refactoring**
```markdown
**Instruction in system prompt:**
- Default: safe extension without refactoring
- Refactoring only if code violates SOLID principles or creates technical debt
- Consider usage context (production vs development)

**How it works:**
The model evaluates each refactoring case by applying these principles:
- Analyzes current code state
- Compares with criteria from system prompt
- Makes decision based on principles, not rigid rules
```

**Example 3: Guiding through intermediate steps (Chain of Thought)**
```markdown
**Instruction in system prompt:**
- Break task into phases and steps
- After each step: STOP → update artifacts → provide summary
- Use "good enough" principles for decisions about continuing

**How it works:**
The model goes through a sequence of logical steps:
- Planning: breaking task into subtasks
- Execution: implementing each step with checking intermediate results
- Evaluation: applying "good enough" criteria for decision about continuing
```

**Practical conclusions:**

1. **System prompt should contain instructions, not algorithms:**
   - ✅ "How to gather context" instead of "Execute commands X, Y, Z"
   - ✅ "Decision-making principles" instead of "If condition A, then action B"

2. **Focus on intermediate steps:**
   - System prompt should explicitly indicate the need for intermediate checks
   - Define criteria for decision-making at each stage
   - Ensure process transparency for the user

3. **Using guard rails instead of rigid rules:**
   - Provide criteria and principles, not deterministic instructions
   - Allow the model to apply principles in the context of a specific situation
   - Use objective criteria instead of subjective assessments

**Sources:**
- [Chain of Thought Prompting](https://arxiv.org/abs/2201.11903) - Technique guiding model through sequence of logical steps
- [The Prompt Canvas: A Literature-Based Practitioner Guide](https://arxiv.org/abs/2412.05127) - Practical guide for creating effective prompts (2024)

---

<a id="agent-model-separation"></a>

### Separation of Responsibilities: Agent and Model
**⚠️ CRITICALLY IMPORTANT:** The model only knows the context provided by the agent. The agent manages tools, response processing, and the working contract. The model doesn't know about protocols, tool implementation, or internal agent operation.

**Key concept:**
- **Model (LLM):** Works exclusively with provided context. Knows only tool names and descriptions from the system prompt. Generates requests for tool usage in the format expected by the agent.
- **Agent:** Manages context (what to pass to the model), processes model responses (parsing tool calls), calls tools (tool call implementation), defines working contract (input/output data format).

**What the model knows:**
- ✅ Tool names (from system prompt)
- ✅ Tool descriptions (from system prompt)
- ✅ How to request tool usage (through special markers/format)
- ✅ Information from provided context

**What the model does NOT know:**
- ❌ How tools are implemented
- ❌ How agent processes responses
- ❌ Protocol concepts (MCP, RAG, etc.)
- ❌ How agent manages context
- ❌ Where context comes from

**What the agent controls:**
- ✅ Context population (what to pass to the model)
- ✅ Model response processing (parsing tool calls)
- ✅ Tool calls (tool call implementation)
- ✅ Protocol management (MCP servers, RAG, etc.)
- ✅ Working contract definition (input/output data format)

**Working contract:**
- Contract is defined by agent: system prompt format, tool descriptions, model response format, response processing format
- Model follows contract: uses tools according to descriptions, generates responses in expected format, doesn't know about contract implementation

**Practical conclusions for system prompts:**

1. **Tool instructions:**
   - ✅ Describe tools functionally (what they do)
   - ✅ Indicate alternative tool names
   - ✅ Explain when to use a tool
   - ❌ DO NOT mention specific implementations or protocols
   - ❌ DO NOT explain how the agent implements tools
   - ❌ DO NOT mention "Function Calling API" or other technical implementation details

2. **Context instructions:**
   - ✅ Explain that you work with provided context
   - ✅ Indicate what information to look for in context
   - ✅ Explain how to use information from context
   - ❌ DO NOT assume the model knows where context comes from
   - ❌ DO NOT mention protocols (MCP, RAG, Function Calling API) as concepts for the model
   - ❌ DO NOT use technical terms in instructions for the model

3. **Data handling instructions:**
   - ✅ Explain how to work with data already in context
   - ✅ Indicate what tools to use for obtaining data
   - ✅ Explain how to process obtained data
   - ❌ DO NOT explain how agent obtains data from protocols
   - ❌ DO NOT mention data retrieval protocols
   - ❌ DO NOT mention technical details (Function Calling API, tool schemas, etc.)

**Correct and incorrect formulation examples:**

**❌ INCORRECT:**
```markdown
**MCP servers:**
- Use MCP servers to get business context
- MCP protocol allows getting data from internal sources
- Model should know about MCP servers and use them
```

**✅ CORRECT:**
```markdown
**Tools for obtaining information:**
- Use resource retrieval tool if available
- Tool allows obtaining business context and architectural decisions
- Use tool when project artifact information is insufficient
```

**❌ INCORRECT:**
```markdown
**Context:**
- Agent manages MCP servers and passes data to context
- Model receives context through RAG mechanism
- Context is formed by agent from various sources
```

**✅ CORRECT:**
```markdown
**Context:**
- Work with provided context
- Look for information in context for decision-making
- Use information from context to perform tasks
```

**❌ INCORRECT (technical details in model instructions):**
```markdown
**Tools:**
- Tools are available through Function Calling API
- Model already knows parameter schemas from Function Calling API
- Use offset/limit parameters (available in Function Calling API)
```

**✅ CORRECT (direct instructions without technical details):**
```markdown
**Tools:**
- Tools are available in your environment
- Parameter information is available for each tool - use it when needed
- Use offset/limit parameters to read large files in chunks
```

**⚠️ IMPORTANT:** Difference between description for developers and instructions for model:
- **For developers (in knowledge base):** Can mention "Function Calling API" as technical information
- **For model (in system prompt):** DO NOT mention technical details, only direct instructions

#### Tool Description Formats in Prompts

**Purpose:** Describe universal formats for describing tools in system prompts  
**When to use:** When creating system prompts with tools

**Tool description format options:**

**1. Functional description (recommended for universality):**

The most universal approach - describe tools functionally, without binding to specific APIs.

```text
✅ Good:
**Available Tools:**
- **read_file** - Reads file content. Use for inspecting code or documents.
- **write_file** - Creates or overwrites files. Use for creating new content.
- **search** - Searches codebase semantically. Use for finding relevant code.
- **run_command** - Executes terminal commands. Use for running scripts or tests.

**When to use each tool:**
- Need to understand existing code? → read_file
- Need to find something in codebase? → search
- Need to create or modify files? → write_file
- Need to run tests or scripts? → run_command
```

**2. Description with parameters (for precision):**

When it's important to specify tool parameters.

```text
✅ Good:
**Tools:**

**read_file(path)**
- Reads and returns file content
- Parameters: path (string) - file path to read
- Use when: need to inspect existing files

**write_file(path, content)**
- Creates or overwrites file with content
- Parameters: 
  - path (string) - target file path
  - content (string) - file content to write
- Use when: need to create or modify files
```

**3. Description with usage examples:**

For complex tools, it's useful to show examples.

```text
✅ Good:
**search_codebase**
- Semantic search in the codebase
- Use when: need to find code by meaning, not exact text

Examples:
- "How does authentication work?" → finds auth-related code
- "Where is user validation?" → finds validation logic
- "Database connection setup" → finds DB configuration
```

**What NOT to include in tool descriptions:**

```text
❌ Bad:
- Mentions of specific APIs (Function Calling API, MCP Protocol)
- Technical implementation details
- JSON/TypeScript schemas (unless explicitly required)
- Information about how agent implements tools
```

**Tool description recommendations:**
- ✅ Describe WHAT the tool does
- ✅ Indicate WHEN to use it
- ✅ Provide examples for complex cases
- ✅ Use simple natural language
- ❌ Don't include technical implementation details
- ❌ Don't mention specific protocols or APIs

**Sources:**
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - Protocol for standardizing context exchange
- [Retrieval-Augmented Generation (RAG)](https://arxiv.org/abs/2005.11401) - Original RAG work (2020)
- [Function Calling / Tool Use](https://platform.openai.com/docs/guides/function-calling) - OpenAI Function Calling Guide
- [Awesome AI System Prompts](https://github.com/dontriskit/awesome-ai-system-prompts) - Examples of tool descriptions in real prompts

**Related sections:**
- [Nature of System Prompt](#system-prompt-nature) - Instructions for decision-making, not a program
- [System Prompt Universality Principle](#universality-principle) - Universality without mentioning specific technologies
- [Agent Loop Patterns](#agent-loop-patterns) - Tool usage patterns
- [Best Practices](#best-practices) - Recommendations for creating effective prompts

---

### System Prompt Structure

**Recommended structure:**

```text
1. **Role and Context**
   - Who you are (agent role)
   - Why frequent stops are needed (philosophy)
   - Available tools

2. **Workflow and Procedures**
   - Main workflow
   - Step-by-step procedures
   - Rules and constraints

3. **Output Management**
   - Output data types
   - Creation/update rules
   - Document relationships

4. **Quality Criteria**
   - Validation checklists
   - Success criteria
   - Examples of correct behavior

5. **Quick Reference**
   - Key rules
   - Common patterns
   - Cheat sheet
```

### Writing Principles

#### 1. Clarity and Specificity

**✅ Good:**

```text
After completing each step:
1. Update step status to COMPLETED
2. Document changes with: date, phase/step, changes, result
3. Update context: remove completed actions, update next steps
4. STOP and wait for confirmation
```

**❌ Bad:**

```text
After step completion, update things and stop if needed.
```

#### 2. Structure

**✅ Good:**

- Use clear sections with headings
- Number steps and procedures
- Use lists for enumerations
- Group related information

**❌ Bad:**

- Continuous text without structure
- Mixing different topics
- Lack of navigation

#### 3. Examples and Templates

**✅ Good:**

**Example of CORRECT behavior:**
```text

Task completed:

- Updated status: Task → COMPLETED
- Documented changes with clear description
- Updated context with new information
**STOP** - Waiting for confirmation before proceeding to next task

```

**Example of INCORRECT behavior:**
```text

❌ Completing task and immediately starting next task without STOP
```

**❌ Bad:**

```text
Do it correctly.
```

#### 4. Terminology Uniformity

**✅ Good:**

- Use a unified glossary of terms
- Standardize document and structure names
- Consistent status terminology

**❌ Bad:**

- "document" and "file" used for the same concept without uniformity (see [Glossary of Terms](#glossary-of-terms) for correct usage)
- "step" and "task" used interchangeably (see [Glossary of Terms](#glossary-of-terms) for correct usage)
- Different names for the same concept

#### 5. Objective Conditions

**✅ Good:**

```text
If template file exists → Copy instructions section AS-IS
If template file does NOT exist → Create instructions based on description
```

**❌ Bad:**

```text
If you think template is good → use it
If task seems complex → use Full Workflow (without clear criteria)
```

---

<a id="system-prompt-length"></a>

### System Prompt Length: Principles and Recommendations
**Purpose:** Define principles for working with system prompt length and optimality assessment criteria  
**When to use:** When creating or evaluating system prompts, when making decisions about instruction detail level  
**Related sections:** [System Prompt Structure](#system-prompt-structure), [Writing Principles](#writing-principles), [Output Size Optimization](#output-size-optimization)

**Sources:**
- [The Prompt Canvas: A Literature-Based Practitioner Guide](https://arxiv.org/abs/2412.05127) - Practical guide for creating effective prompts (2024)

---

**⚠️ CRITICALLY IMPORTANT:** System prompt length itself is not a problem. The problem is **lack of structure** in a long prompt.

**Key principles:**

1. **Structure matters more than length:**
   - ✅ A long structured prompt (with clear sections, navigation, hierarchy) is effective
   - ❌ A short unstructured prompt may be less effective than a long structured one
   - ❌ A long unstructured prompt creates navigation and comprehension problems

2. **Balance between completeness and brevity:**
   - System prompt should contain **all necessary information** for task execution
   - Redundant information (duplication, irrelevant details) should be removed
   - Insufficient information leads to uncertainty and errors

3. **Length assessment criteria:**
   - ✅ Prompt contains all necessary instructions for the task
   - ✅ Prompt is structured (clear sections, navigation, hierarchy)
   - ✅ Prompt doesn't contain duplication (see [Instruction Duplication](#duplication))
   - ✅ Prompt uses links to external sources (templates, knowledge base) instead of full copying
   - ❌ Prompt contains redundant information unrelated to the task
   - ❌ Prompt is unstructured (continuous text, no navigation)

**Practical recommendations:**

#### When a prompt can be long

✅ **Acceptably long prompt if:**
- Prompt is well-structured (clear sections, headings, navigation)
- Each section contains necessary information without duplication
- Prompt uses links to external sources (templates, knowledge base) instead of full copying
- Prompt follows recommended structure (Role, Workflow, Output Management, Quality, Quick Reference)
- Prompt contains examples and templates necessary for task execution

**Examples of effective long prompts:**
- Prompts for complex agents with many procedures and workflows
- Prompts with detailed instructions for working with structured data
- Prompts with examples of correct and incorrect behavior

#### When a prompt should be shorter

❌ **Shorten prompt if:**
- Contains instruction duplication (see [Instruction Duplication](#duplication))
- Contains full template copying instead of links to them
- Contains redundant information unrelated to the task
- Is unstructured (continuous text without sections)
- Contains information that should be in templates or knowledge base

**Length optimization strategies:**

1. **Using links instead of copying:**
   ```text
   ✅ Good:
   - Use links to external sources (templates, knowledge base, documentation)
   - Indicate that formatting is defined by external sources
   - External sources are the single source of truth for rules
   
   ❌ Bad:
   - Full copying of all rules from external sources into prompt
   - Duplicating information that already exists in templates or documentation
   ```

2. **Structuring instead of shortening:**
   ```text
   ✅ Good:
   - Clear sections with headings
   - Quick Reference section for quick access
   - Information hierarchy (general → details)
   
   ❌ Bad:
   - Removing important information for the sake of length reduction
   - Continuous text without structure
   ```

3. **Removing duplication:**
   - Use principles from section [Instruction Duplication](#duplication)
   - Avoid repeating the same information in different sections

**Evaluation metrics:**

- **Structure:** Presence of clear sections, headings, navigation
- **Completeness:** Does prompt contain all necessary information for the task
- **No duplication:** Is there repetition of the same information
- **Use of links:** Are links to external sources used instead of copying
- **Effectiveness:** Does prompt work effectively in practice

**Important:**
- ❌ DO NOT use specific numbers (tokens, lines, KB) as evaluation criteria
- ✅ Use structural and functional criteria (structure, completeness, no duplication)
- ✅ Evaluate prompt effectiveness in practice, not by its length

**Connection with other sections:**
- [System Prompt Structure](#system-prompt-structure) - Recommended structure for long prompts
- [Instruction Duplication](#duplication) - When duplication is justified and when it's not
- [Using Templates](#template-usage) - Using links instead of copying
- [Output Size Optimization](#output-size-optimization) - Output size control (not prompt)

---

<a id="common-mistakes"></a>

## 🔴 Top-10 Common Mistakes in System Prompts

**Purpose:** Describes the most common mistakes when writing system prompts and ways to avoid them  
**When to use:** When checking prompt quality or when learning to write prompts  
**Related sections:** [Style Guide](#style-guide), [Best Practices](#best-practices), [Anti-Patterns](#anti-patterns)

**Sources:**
- [OpenAI Best Practices](https://help.openai.com/en/articles/6654000-best-best-practices-for-prompt-engineering-with-openai-api) - Official OpenAI recommendations
- [Anthropic Claude Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) - Anthropic guide
- [A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT](https://arxiv.org/abs/2302.11382) - Prompt pattern catalog (2023)

---

### 1. Ambiguous Formulations ❌

**Problem:**

- Using vague or ambiguous expressions
- Informal phrases and jargon
- Lack of specificity

**Examples of bad formulations:**

```text
❌ "Make it better"
❌ "Do the right thing"
❌ "Handle errors properly"
❌ "If uncertainty arises" (subjective)
```

**Examples of good formulations:**

```text
✅ "Add input validation: check if email format is valid using regex pattern"
✅ "Handle FileNotFoundException: log error with context and return user-friendly message"
✅ "If file does not exist → create empty file with default structure"
```

**Recommendations:**

- Use specific actions and criteria
- Avoid subjective assessments
- Specify exact conditions and alternatives

---

### 2. Lack of Context ❌

**Problem:**

- Insufficient information about the task
- Ignoring project structure
- Lack of information about technologies and dependencies

**What to include:**

- Project structure and architecture
- Used technologies and frameworks
- Related files and dependencies
- Business logic and requirements
- Constraints and constants

**Recommendations:**

- Always provide relevant context
- Open related files for Copilot
- Close irrelevant files
- Specify used libraries and versions

---

### 3. Complex or Multi-Task Requests ❌

**Problem:**

- Attempting to solve multiple tasks in one prompt
- Too large and complex instructions
- Lack of task breakdown

**Examples of bad prompts:**

```text
❌ "Refactor the entire module, add tests, update documentation, and fix all bugs"
❌ "Create authentication system with OAuth, JWT, password reset, and email verification"
```

**Examples of good prompts:**

```text
✅ "Step 1: Extract authentication logic into separate service class"
✅ "Step 2: Add unit tests for authentication service"
✅ "Step 3: Update API documentation for authentication endpoints"
```

**Recommendations:**

- Break complex tasks into simple steps
- Solve tasks sequentially
- Each step should be specific and measurable

---

### 4. Lack of Examples ❌

**Problem:**

- No input data examples
- No expected result examples
- No output format examples

**What to include:**

- Input data examples
- Expected output data examples
- Format examples (JSON, table, list)
- Edge case examples

**Recommendations:**

- Always provide examples for complex tasks
- Show expected result format
- Include edge case examples

---

### 5. Ignoring Coding Best Practices ❌

**Problem:**

- Inconsistent code style
- Unreadable code without comments
- Lack of error handling

**Recommendations:**

- Follow consistent coding style
- Use descriptive variable and function names
- Comment complex code sections
- Include error handling in prompts

---

### 6. Inconsistency in Formulations ❌

**Problem:**

- Different formulations for the same task
- Inconsistent terminology
- Different instruction styles

**Recommendations:**

- Use uniform formulations
- Create a glossary of terms
- Standardize instruction format
- Use templates for repetitive tasks

---

### 7. Lack of Error Handling ❌

**Problem:**

- No validation instructions
- No exception handling
- No security checks
- Ignoring tool limitations when creating files
- Lack of alternative strategies for large files

**Critical tool limitation:**

**Important:** In some development environments, when a tool call error occurs (e.g., `write` returns an error), the entire chat session terminates, the agent stops working. This means that error handling after the fact does NOT work. Focus on error prevention and alternative strategies BEFORE creating the file.

**Recommendations:**

- Always include error handling instructions
- Specify how to validate results
- Include security checks
- Test generated code
- **For file operations:** Use multi-level creation strategy and success verification (see [Best Practices: Working with Tools and Creating Files](#file-creation-best-practices))

**More details:** Full description of critical tool limitations, file creation strategies, success verification, and state preservation see in section [Best Practices: Working with Tools and Creating Files](#file-creation-best-practices).

---

### 8. Ignoring Security ❌

**Problem:**

- Generating code with potential vulnerabilities
- Lack of security checks
- Ignoring security best practices
- Vulnerability to prompt injection attacks
- Risk of confidential data leakage
- Lack of jailbreaking protection

**Recommendations:**

- Include security requirements in prompts
- Use static analysis tools
- Check code for vulnerabilities
- Follow secure coding principles
- Protect prompts from prompt injection (see [Prompt Security](#security))
- Don't include secrets in prompts (use environment variables)
- Validate and sanitize user input
- Use moderation API to check input/output

**More details:** See section [Prompt Security](#security) for detailed information about attack protection.

---

### 9. Incorrect Chat History Management ❌

**Problem:**

- Keeping irrelevant requests
- Outdated context in history
- Mixing different tasks

**Recommendations:**

- Remove irrelevant requests
- Start new conversations for new tasks
- Clear history when context changes
- Group related tasks

---

### 10. Lack of Iterative Approach ❌

**Problem:**

- Expecting perfect result from first request
- Refusal to refine and adjust
- Unwillingness to experiment

**Recommendations:**

- Experiment with formulations
- Refine requests for better results
- Use iterative approach
- Improve prompts based on results

---

---

<a id="best-practices"></a>

## 🎯 Best Practices for System Prompts

**Purpose:** Provides proven recommendations for creating effective system prompts  
**When to use:** When creating or improving system prompts to apply best practices  
**Related sections:** [Style Guide](#style-guide), [Common Mistakes](#common-mistakes), [Anti-Patterns](#anti-patterns)

### 🤖 Instructions for you

**How to use this section:**
- When creating a prompt → use as checklist for quality verification
- When working with tools → follow multi-level file creation strategy
- When filling lists → use sequential filling with verification after each element
- When verifying success → apply procedures from "Success Verification" section

---

### 1. Using Natural Language

**Purpose:** Ensure prompt understandability and accessibility for models  
**When to use:** When creating any prompts, especially for complex tasks

- Formulate requests in natural language
- Avoid slang and jargon
- Use professional terminology

### 2. Providing Context

**Purpose:** Provide model with sufficient context for task execution  
**When to use:** When creating prompts for tasks requiring understanding of project context or environment

- Specify programming language
- Describe project structure
- Mention used libraries
- Include relevant files

### 3. Breaking Down Complex Tasks

**Purpose:** Simplify complex task execution through decomposition  
**When to use:** When working with complex or multi-step tasks

- Divide large tasks into smaller ones
- Solve tasks sequentially
- Each step should be specific

### 4. Using Examples

**Purpose:** Demonstrate expected behavior and output format  
**When to use:** When creating prompts for tasks where specific formats or behavior patterns matter

- Provide input data examples
- Show expected results
- Include output format examples

### 5. Defining Output Format

**Purpose:** Ensure predictable and structured model output format  
**When to use:** When creating prompts where specific output format matters for further processing or integration

- Specify format (text, table, JSON, code)
- Indicate data structure
- Show format examples
- Use structured output for integrations (see [Structured Output](#structured-output))

### 6. Following Coding Style

**Purpose:** Ensure consistency and readability of generated code  
**When to use:** When creating prompts for code generation or working with code

- Follow consistent style
- Use descriptive names
- Comment complex sections
- Follow language best practices

### 7. Iterative Approach

**Purpose:** Gradually improve prompt quality through iterations and refinements  
**When to use:** When creating and optimizing prompts to achieve better results

- Experiment with formulations
- Refine requests
- Improve based on results

### 8. Security Verification

**Purpose:** Ensure security of generated code and prevent vulnerabilities  
**When to use:** When creating prompts for code generation, especially for critical systems

- Include security requirements
- Check code for vulnerabilities
- Use analysis tools

### 9. Working with Tools and Creating Files

**Purpose:** Ensure reliable file creation and modification considering tool limitations  
**When to use:** When creating system prompts that use tools for file creation/modification

<a id="file-creation-best-practices"></a>

#### Critical Tool Limitation

**Important:** In some development environments, when a tool call error occurs (e.g., `write` returns an error), the entire chat session terminates, the agent stops working. This means:

- ❌ **Error handling after the fact does NOT work** - agent cannot execute error handling instructions
- ❌ **Retry mechanism won't work** - agent won't be able to retry
- ❌ **Alternative strategies AFTER error don't work** - agent has already stopped
- ✅ **Success verification CAN work** - if file was created, can verify through `read_file`
- ✅ **Alternative strategies BEFORE error CAN work** - use different approach instead of problematic one
- ✅ **Saving content to context works** - user can create file manually

**Conclusion:** Problem cannot be solved through error handling after the fact. Focus on error prevention and alternative strategies BEFORE creating file.

#### Multi-Level File Creation Strategy

**Principle:** Use strategies in priority order, starting with most reliable.

**Priority 1: Copy template via terminal (if template provided)**

**When to use:** If user provided file template.

**Procedure:**
1. **FIRST STEP:** Check if template was provided by user
2. **If template provided:**
   - Try copying via terminal: `run_terminal_cmd("cp [template_path] [target_file]")`
   - If successful → file created, supplement via `search_replace`
   - If terminal not available/doesn't work → go to Priority 2
3. **If template NOT provided** → go to Priority 3

**Priority 2: Copy via read_file + write (if template provided and small)**

**When to use:** If Priority 1 didn't work AND template provided AND template read via `read_file` AND content length ≤ threshold (e.g., ≤ 10,000 characters OR ≤ 200 lines).

**Priority 3: Minimal file + incremental addition (default for large files)**

**When to use:** If template NOT provided OR previous priorities not applicable OR content length > 10,000 characters OR > 200 lines.

**Procedure:**
1. **Before creating:** Save full content to context (MANDATORY for critical files)
2. **Evaluate content size (after reading via `read_file`):**
   - If > 10,000 characters OR > 200 lines → use this strategy BY DEFAULT
   - If no template → use this strategy
3. **Create minimal file:**
   - Header/metadata
   - Basic structure (sections, headers)
   - Empty sections or placeholders
4. **Supplement in parts (sequentially):**
   - Part size: 50-100 lines (one logical section)
   - Each part via `search_replace`
   - **Success verification after each part** via `read_file`
   - If part failed → retry only that part
5. **Final verification:**
   - All sections added
   - File integrity verified

#### Success Verification

**Principle:** After creating/modifying file, ALWAYS verify operation success.

**Procedure:**
1. Use `read_file` to verify file existence
2. Verify file is not empty
3. Verify file contains expected content (minimum: file exists and not empty)
4. If verification failed → file not created/updated, but agent continues (can notify user)
5. If file exists but content incomplete → use file modification tool to supplement

**When to verify (ALWAYS):**
- After creating important documents (plans, logs, question lists, context files)
- After creating/modifying source code
- After each file update
- After each part during incremental addition
- After each list element during sequential filling

#### State Preservation

**Principle:** Before creating/updating critical files, save content to context for recovery possibility.

**Procedure:**
1. **Before creating/updating critical files** (plans, large documents):
   - Save full content/changes to context (context file or other context)
   - This is MANDATORY for critical files
2. **This allows:**
   - Recover work if file wasn't created/updated
   - User can create/update file manually using content from context

---

<a id="when-to-stop"></a>

## 🛑 When to Stop: Avoiding Over-optimization

**Purpose:** Defines "good enough" criteria and helps avoid endless improvement cycles  
**When to use:** When analyzing system prompts, when it seems something could be improved, or when deciding if changes are needed  
**Related sections:** [Best Practices](#best-practices), [Guard Rails for Vibe Coding](#guard-rails-for-vibe-coding-on-large-projects), [Sufficient Quality Gateway](#sufficient-quality-gateway), [Conclusions and Recommendations](#ai-generated-prompts)

**Context:** Solving the problem of constantly finding "new improvements" with each analysis. Especially important for models prone to overthinking.

### 🤖 Instructions for you

**How to use this section:**
- Before starting analysis → determine usage context and priorities
- During analysis → use priority system (🔴 🟡 🟢 ⚪) to evaluate improvements
- When deciding → check "good enough" criteria (85-90%+, 100% not required)
- When in doubt → use guard rails from section [Guard Rails for Vibe Coding](#guard-rails-for-vibe-coding-on-large-projects)

---

### Problem: Endless Improvement Cycle

**Symptoms:**
- With each new analysis, "new improvements" are found
- Improvements are often not critical or already good enough
- No clear criteria for when to stop
- Over-optimization instead of practical use

**Cause:**
- AI agents tend to find improvement opportunities
- Some models prone to overthinking and deep analysis
- Lack of clear "good enough" criteria (guard rails)
- Mixing critical and non-critical improvements
- Ignoring usage context

**Solution:**
- Clear guard rails with objective stopping criteria
- Priority system (🔴 🟡 🟢 ⚪) for distinguishing critical and non-critical improvements
- Focus on functionality, not perfection
- Using objective criteria instead of subjective assessments

---

### "Good Enough" Criteria

#### 1. Functional Sufficiency

**Prompt is considered sufficient if:**

✅ **All critical functions work:**
- Prompt performs its main task
- No blocking issues
- Main usage scenarios covered

✅ **Best practices compliance (85-90%+):**
- Structure follows Style Guide
- No critical anti-patterns
- Main best practices applied

✅ **No critical problems:**
- No subjective conditions (that require fixing)
- No multi-level nested conditions
- No ambiguous formulations

**❌ NOT required:**
- 100% compliance with all best practices
- Perfect implementation of all techniques
- Covering all edge cases

#### 2. Improvement Prioritization

**Priority system:**

**🔴 Critical (fix immediately):**
- Blocking issues (prompt doesn't work)
- Critical anti-patterns (subjective conditions that break logic)
- Contradictions in instructions
- Missing critical functionality

**🟡 Important (fix soon):**
- Significant quality improvements (adding examples for complex procedures)
- Improvements that significantly enhance understanding
- Fixes that prevent common errors

**🟢 Non-critical (optional, low priority):**
- Small readability improvements
- Adding examples for edge cases
- "Nice to have" improvements
- Improvements that don't affect functionality

**⚪ Not required (ignore):**
- Improvements that don't affect quality
- Over-optimization for hypothetical cases
- Changes for the sake of changes
- Improvements that contradict system philosophy

---

### "Good Enough" Checklist

**Prompt is ready for use if:**

**Functionality:**
- [ ] Prompt performs its main task
- [ ] No blocking issues
- [ ] Main usage scenarios work

**Quality:**
- [ ] Best practices compliance: 85-90%+
- [ ] No critical anti-patterns
- [ ] Structure follows Style Guide
- [ ] No subjective conditions (that require fixing)

**Critical problems:**
- [ ] No contradictions in instructions
- [ ] No multi-level nested conditions
- [ ] No ambiguous formulations
- [ ] All critical functions present

**Context:**
- [ ] Prompt suitable for target use case
- [ ] Risks considered for usage context
- [ ] No over-optimization for hypothetical cases

**If all items are met → Prompt is ready. Stop.**

---

<a id="guard-rails-for-vibe-coding-on-large-projects"></a>

## 🎨 Guard Rails for Vibe Coding on Large Projects

**Purpose:** Define principles and guard rails for system prompts optimized for vibe coding on large projects  
**When to use:** When creating/improving system prompts for working with code, preventing cyclical changes  
**Related sections:** [Production Code Quality](#production-code-quality-and-refactoring-criteria), [When to Stop](#when-to-stop), [Sufficient Quality Gateway](#sufficient-quality-gateway)

**📌 Note:** Core "good enough" principles, priority system (🔴 🟡 🟢 ⚪), and stopping criteria are described in section [When to Stop](#when-to-stop). This section focuses on applying these principles to code work (vibe coding) and preventing cyclical changes.

**Context:** Preventing cyclical changes, balance between ideal and practical solution, justification for the model

---

### "Good Enough" Principle

**Principle:**
- Working solution matters more than perfect one
- 80% of result from 20% of effort
- Focus on practical use, not perfection

**For model:**
```
✅ CORRECT: Implement functionality that works for main use cases
❌ INCORRECT: Try to make perfect solution for all possible edge cases

✅ CORRECT: Code works, understandable, follows project standards
❌ INCORRECT: Endless improvements for the sake of perfection
```

---

### "Pragmatic vs Perfect" Principle

**Principle:**
- Pragmatic solution solves the problem now
- Perfect solution may be excessive
- Focus on current requirements, not hypothetical ones

**For model:**
```
✅ CORRECT: Implement simple solution that works
❌ INCORRECT: Create excessive abstraction "for the future"

✅ CORRECT: Use existing project patterns
❌ INCORRECT: Create new patterns for "perfection"
```

---

### Guard Rails: Preventing Cyclical Changes

#### Improvement Stopping Criteria

**Stopping criteria:**
```
✅ STOP if:
- Code works for main use cases
- Code follows project standards (85-90%+)
- No critical problems
- Code is understandable and maintainable

❌ DO NOT STOP only if:
- There are critical problems (🔴)
- Code doesn't work
- There are blocking issues
```

**For models prone to overthinking:**
- Use objective criteria (works/doesn't work, has/doesn't have problems)
- Avoid subjective assessments ("can be improved", "not perfect")
- Focus on functionality, not perfection
- Guard rails prevent tendency toward overthinking and finding "new improvements" with each analysis
- Stopping criteria help avoid endless improvement cycle

#### "One Improvement at a Time" Rule

**Principle:**
- Make only one improvement at a time
- Check result after each improvement
- Stop when result is "good enough"

**For model:**
```
✅ CORRECT: Make one improvement → check → if good enough → stop
❌ INCORRECT: Make many improvements at once without checking
```

---

<a id="sufficient-quality-gateway"></a>

## ✅ Sufficient Quality Gateway

**⚠️ CRITICALLY IMPORTANT:** **Sufficient Quality Gateway SHOULD be used by default always and everywhere** when working with knowledge base and when making decisions about adding information. This allows precise analysis of when to stop and avoid duplications only in context of this file.

**Purpose:** Systematic "good enough" check before critical workflow transitions, during planning, when making decisions, and when updating knowledge base  
**When to use:** 
- **By default always** when working with knowledge base
- Before transitioning to next stage (analysis → plan, plan → execution, code → next step)
- **During planning** when making decisions about plan structure, priorities, step detail
- **When making decisions** at any work stage (about need for changes, improvements, continuing work)
- **Mandatory** before adding any information to knowledge base  
**Related sections:** [When to Stop](#when-to-stop) (core principles and criteria), [Guard Rails for Vibe Coding](#guard-rails-for-vibe-coding-on-large-projects) (applying to code), [Production Code Quality](#production-code-quality-and-refactoring-criteria)

---

### Quality Indicators

**For Analysis (Context Analysis):**
- **Component Identification:** Main components identified (Binary: Yes/No, Target: Yes - main components, not all)
- **Dependency Understanding:** Key dependencies understood (Binary: Yes/No, Target: Yes - key dependencies, not all)
- **Structure Understanding:** Project structure studied (Binary: Yes/No, Target: Yes - sufficient, not exhaustive)
- **Task Breakdown:** Task broken into phases (Binary: Yes/No, Target: Yes - clear phases, not over-detailed)
- **Steps Definition:** Steps defined for phases (Binary: Yes/No, Target: Yes - actionable steps, not over-optimized)
- **Analysis Sufficiency:** Analysis sufficient for planning (Binary: Yes/No, Target: Yes - sufficient, not exhaustive)

**For Plan (Plan Quality):**
- **Phase Definition:** Phases defined with clear goals (Binary: Yes/No, Target: Yes - clear phases, not over-detailed)
- **Step Completeness:** Steps have completion criteria (Binary: Yes/No, Target: Yes - actionable steps, not over-optimized)
- **Blocker Identification:** Blockers identified (if any) (Binary: Yes/No, Target: Yes - blockers documented, if exist)
- **Scenario Coverage:** Plan covers main scenarios (Binary: Yes/No, Target: Yes - main scenarios, not all possible cases)
- **Plan Sufficiency:** Plan sufficient for execution (Binary: Yes/No, Target: Yes - sufficient, not exhaustive)

**For Code (Code Implementation):**
- **Functional Sufficiency:** Main use cases work (Binary: Yes/No, Target: Yes)
- **Static Analysis:** Critical errors count (Count: number, Target: 0)
- **Code Quality:** Best practices compliance (Percentage, Target: 85-90%+)
- **Critical Issues:** Critical issues count (Count: number, Target: 0)

---

### Priority System

**Priority system for evaluating problems and improvements:**

- **🔴 Critical** → Must fix/complete before proceeding
  - Blocking issues
  - Critical understanding gaps
  - Critical errors

- **🟡 Important** → Can document for later, but not blocking
  - Important details
  - Significant quality improvements
  - Important enhancements

- **🟢 Nice-to-have** → Ignore, not blocking
  - Non-critical details
  - Small improvements
  - "Nice to have" enhancements

- **⚪ Not required** → Ignore
  - Improvements for improvements' sake
  - Over-optimization for hypothetical cases
  - Not required

---

### Decision Logic

**For analysis:**
- If all criteria met → Proceed to plan creation
- If critical gaps (🔴) → Complete analysis, re-verify
- If only important details (🟡) → Document, but proceed
- If only nice-to-have (🟢) → Ignore, proceed

**For plan:**
- **During planning:** When making decisions about structure, priorities, detail → apply "good enough" criteria (85-90%+, 100% not required)
- If all criteria met → Proceed to execution
- If critical gaps (🔴) → Complete plan, re-verify
- If only important details (🟡) → Document, but proceed
- If only nice-to-have (🟢) → Ignore, proceed

**For code:**
- If all criteria met → Proceed to next step/phase
- If critical issues (🔴) → Fix before proceeding
- If only important improvements (🟡) → Document, but proceed
- If only non-critical (🟢) → Ignore, proceed

---

<a id="production-code-quality-and-refactoring-criteria"></a>

## 💻 Production Code Quality and Refactoring Criteria

**Purpose:** Define code quality criteria and when to refactor  
**When to use:** When working with existing code, making refactoring decisions, evaluating code quality  
**Related sections:** [Best Practices](#best-practices), [When to Stop](#when-to-stop)

**Context:** Working with existing code requires balance between quality and stability. Default: safe extension without refactoring.

---

### Principle: Safe Extension by Default

**Key rule for stable code:**

✅ **By default:** Safe extension without refactoring  
✅ **Refactoring:** Only with clear signs of necessity  
✅ **Balance:** Working solution matters more than perfect architecture

**Rationale:**
- Stable code should remain stable
- Refactoring may introduce bugs
- Working solution matters more than perfect architecture
- Safe extension reduces risks

---

### When to Refactor

#### 🔴 Critical Signs (refactoring necessary)

**Refactor if:**
- Code doesn't work or works incorrectly
- Code blocks adding new functionality
- Code contains critical security vulnerabilities
- Code violates critical principles (SOLID, DRY) and affects functionality
- Technical debt blocks development

#### 🟡 Important Signs (refactoring desirable, but not critical)

**Refactor if:**
- Code is hard to understand and maintain
- Code contains duplication that complicates changes
- Code violates principles but doesn't block functionality
- Technical debt accumulates but not critical

#### 🟢 Non-critical Signs (refactoring optional)

**Refactor optionally if:**
- Code can be improved but works
- Code not perfect but functional
- Small principle violations not affecting functionality

#### ⚪ Refactoring NOT required

**DO NOT refactor if:**
- Code works and is understandable
- Refactoring for refactoring's sake
- "Can be improved" without specific necessity
- Principle violations not affecting functionality

---

### Universal Principles (SOLID, DRY, KISS, YAGNI)

**SOLID Principles:**
- **S - Single Responsibility Principle (SRP):** Class should have only one reason to change
- **O - Open/Closed Principle (OCP):** Open for extension, closed for modification - Critical for safe extension
- **L - Liskov Substitution Principle (LSP):** Subclass objects should replace base class objects
- **I - Interface Segregation Principle (ISP):** Clients shouldn't depend on interfaces they don't use
- **D - Dependency Inversion Principle (DIP):** Dependencies should be on abstractions, not concrete implementations

**DRY (Don't Repeat Yourself):**
- Each piece of knowledge should have single, unambiguous, authoritative representation in the system
- ✅ Eliminate duplication if it complicates changes
- ❌ DON'T eliminate duplication if it doesn't affect functionality
- ❌ DON'T create excessive abstraction for DRY's sake

**KISS (Keep It Simple, Stupid):**
- Simplicity should be a key design goal
- ✅ Prefer simple solution over complex
- ✅ Avoid excessive abstraction
- ✅ Code should be understandable without documentation

**YAGNI (You Aren't Gonna Need It):**
- Don't add functionality until it's needed
- ✅ Add functionality only when needed
- ✅ Don't create abstractions "for the future"
- ✅ Focus on current requirements

---

## 📚 Sources

### Official Documentation

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Anthropic Claude Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [The Prompt Canvas: A Literature-Based Practitioner Guide](https://arxiv.org/abs/2412.05127)

### Software Development Principles

- [Good Enough Software](https://www.joelonsoftware.com/2000/05/14/strategy-letter-iii/)
- [Analysis Paralysis](https://en.wikipedia.org/wiki/Analysis_paralysis)
- [Pareto Principle (80/20 Rule)](https://en.wikipedia.org/wiki/Pareto_principle)
- [YAGNI Principle](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it)

---

## End of Knowledge Base

This document is actively maintained and updated based on practical experience and new research in the field of prompt engineering.


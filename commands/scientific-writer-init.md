---
description: Set up the current project for evidence-first scientific writing with Medskill Panda (Vietnamese, English or bilingual; Word, LaTeX or Markdown) by installing CLAUDE.md and AGENTS.md.
---

# Medskill Panda Project Setup

When the user runs `/medskill-panda:scientific-writer-init`, do the following:

## ⚠️ CRITICAL RULE: NEVER READ THE TEMPLATE FILE

**Throughout this entire process, you must NEVER use the read_file tool on a template file. The template files are very long and reading them wastes time and tokens. Only use terminal commands (`cp`, `cat`, `mv`) to handle them.**

## Instruction Files Installed

Medskill Panda configures **two** project instruction files so both Claude Code and other agent clients pick it up:

| Project file | Template |
|--------------|----------|
| `CLAUDE.md` | `CLAUDE.scientific-writer.md` |
| `AGENTS.md` | `AGENTS.scientific-writer.md` |

The two templates hold identical instructions; only the generated header differs. Steps 1 and 3 apply to **each** of these files independently.

## Step 1: Check for Existing Instruction Files

1. Check whether `CLAUDE.md` and/or `AGENTS.md` exist in the current working directory.

2. For each file that already exists:
   - Ask the user whether to:
     - a) **Back up** the existing file as `<FILE>.bak` and replace it with the Medskill Panda configuration, or
     - b) **Merge** the Medskill Panda settings into the existing file (append to end), or
     - c) **Skip** this file.
   - If both files exist, ask once and apply the same choice to both unless the user says otherwise.

3. If the user wants to cancel the whole operation, stop here.

4. Wait for user response before proceeding.

## Step 2: Locate the Template File Paths

**CRITICAL: Do NOT use the read_file tool. Do NOT read the template contents. Only locate the file paths.**

Find the paths to the Medskill Panda templates. Use one of these methods:

1. **Use glob_file_search** to find `CLAUDE.scientific-writer.md` and `AGENTS.scientific-writer.md` in the templates directory
2. **Use list_dir** to check if the files exist in known locations
3. **Directly try these paths** (in order):
   - `~/.claude/plugins/*/medskill-panda/templates/` (installed plugin)
   - `<path-to-medskill-panda-checkout>/templates/` (local development)

Once you have the paths, immediately proceed to Step 3. **Do NOT read or verify the file contents.**

If only `CLAUDE.scientific-writer.md` is present (an older install), use it for both `CLAUDE.md` and `AGENTS.md`.

## Step 3: Create or Update Each Instruction File

**All options below must use terminal commands only. Do NOT read the template file contents.**

Repeat for each pair of `{target}` (`CLAUDE.md`, `AGENTS.md`) and its `{template_path}`, using the user's choice from Step 1 (or create new if no existing file):

### Option A: Replace (with backup)
Use terminal commands to:
1. Rename the existing file:
   ```bash
   mv {target} {target}.bak
   ```
2. Copy the template file into place:
   ```bash
   cp {template_path} {target}
   ```
3. Print: "✅ Backed up existing {target} to {target}.bak and created new Medskill Panda configuration"

### Option B: Merge
Use terminal commands to:
1. Append a separator to the existing file:
   ```bash
   echo -e "\n\n---\n\n# Medskill Panda Configuration (Added by Plugin)\n" >> {target}
   ```
2. Append the template file contents directly (without reading):
   ```bash
   cat {template_path} >> {target}
   ```
3. Print: "✅ Merged Medskill Panda configuration into existing {target}"

### Option C: Create New (Default)
If the file does not exist, use terminal command to:
1. Copy the template file into place:
   ```bash
   cp {template_path} {target}
   ```
2. Print: "✅ Created {target} with Medskill Panda configuration"

## Step 4: Summarize What Was Installed

After writing the file, provide a brief summary:

```
🎉 Medskill Panda has been initialized in this project!

📋 How it works:
- Evidence first: every number and reference traces to a source opened in this project
- You approve the brief and the outline before any drafting starts
- Vietnamese, English or bilingual writing; Word, LaTeX or Markdown, following your venue
- Free literature tools by default (PubMed, Europe PMC, OpenAlex, Crossref); unpublished
  text stays local unless you allow otherwise

📝 Document Types Supported:
- Original articles, case reports, systematic and narrative reviews
- Theses (luận văn, luận án) and research protocols (đề cương)
- Grant proposals, conference abstracts, posters and slides

🚀 Getting Started:
1. Your CLAUDE.md and AGENTS.md files are now configured at: {paths written}
2. Start with prompts like:
   - "Viết bài báo gốc về [đề tài] cho Tạp chí Y học Việt Nam"
   - "Draft a STROBE-compliant cohort paper in English for [journal]"
   - "Viết đề cương luận văn thạc sĩ về [đề tài], tóm tắt song ngữ"
3. Check a draft at any time with /medskill-panda:audit-manuscript <file>

💡 Tips:
- Put your data and results tables in data/ and the papers you already have in sources/
- You can edit CLAUDE.md or AGENTS.md to customize behavior (keep them in sync)

📚 Documentation: README.md of the medskill-panda plugin

Happy writing! 🔬📄
```

## Step 5: Final Reminders

Remind the user:
- The `CLAUDE.md` and `AGENTS.md` files can be opened and edited manually at any time
- The first reply to a writing request will be a short round of questions (document type,
  venue, language, format, data): answering them is what keeps the draft accurate

## Error Handling

If any errors occur during file creation:
- Report the specific error to the user
- Suggest manual steps (e.g., creating the file manually)
- Provide the template paths to try:
  - `~/.claude/plugins/*/medskill-panda/templates/{CLAUDE,AGENTS}.scientific-writer.md` (installed plugin)
  - `<path-to-medskill-panda-checkout>/templates/{CLAUDE,AGENTS}.scientific-writer.md` (local development)
- If the templates still can't be found, offer to create basic CLAUDE.md and AGENTS.md files with minimal scientific writing instructions


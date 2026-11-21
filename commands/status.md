---
description: Show where each talk in this project stands (stage, plan approval, open audit findings) and what to do next.
---

# Talk status

A talk folder is a directory holding both `STATUS.md` and `brief.md` (created by the
medical-deck skill). When the user runs `/medskill-panda:status [folder]`:

1. Find talk folders: the folder given as argument, otherwise every directory up to three
   levels below the current one that holds both files. Use `find` or Glob; do not read
   unrelated files.
2. For each talk folder, read `STATUS.md` and, if present, the first lines of `plan.md`
   (title, core message, budget) and the summary line of each file in `audit/`.
3. Reply with one compact table, one row per talk:

   | Talk | Stage now | Plan approved? | Output in `out/` | Open blocking findings | Next step |

   - *Stage now*: the first stage that is not `done`, with its name (for example
     `4 · Evidence (doing)`).
   - *Plan approved?*: yes only if the Plan row of `STATUS.md` says `done, approved`
     without any negation; otherwise say what it says.
   - *Next step*: one short imperative sentence naming the skill to load (for example
     "Approve plan.md, then evidence-research runs").
4. Do not change any file, and do not start the next stage: this command only reports. If
   no talk folder is found, say so and suggest starting a new talk with a slide request
   (medical-deck runs the interview first).

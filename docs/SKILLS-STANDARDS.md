Every skill should have this structure:

## Structure

```bash
my-skill-name/
├── CHANGELOG.md
├── EVAL.md
├── references/                 # Skill references if needed
├── scripts/                    # Scripts, preferebly in Python or Shell for super simple things (let's not explode languages complexity).
│   ├── python_script.py        # Python script for more complex things 
│   ├── python_script_test.py   # Test for the python scripts if possible
│   ├── shell_script.sh         # Shell script for super simple things
│   └── verify_setup.py         # Some verification that everything went well, eg after an installation.
└── SKILL.md
```

* A skill folder MUST have lowercase characters and hyphens, no underscores. Same for its name.

## SKILL.md

A skil FrontMatter should have at least these fields:

```markdown
---
name: name-with-dashes-no-spaces                                  # Mandatory. Use dashes, no spaces. Should coincide with folder name.
description: 🐉 A 1-2 lines description of what the skill does. 
             Let's not overdo it as i consumes static context.    # Mandatory. Needs to start with dragon emoji for extension branding.
metadata:                                           # SHOULD have it
  author: Name Surname (creator/maintainer)         # SHOULD have it. We'll get rid of this when we set up a proper skill ownership system.
  version: 0.0.1                                    # SHOULD have it. Use semantic versioning.
  status: draft|needs-review|published              # optional. Good to say "I'm working on it but its not good yet".
---
```

## CHANGELOG.md (optional)

Aligned to version number in `SKILL.md`

## EVAL.md

Still in phase of meta-evaluation. See internal bug 498524264.
The idea is to have an array of couple INPUT_PROMPT, EXPECTED_OUTPUT with LLM-as-judge.

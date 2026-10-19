---
name: project-scaffolder
description: Create a new module from the project's template, wired into the build.
---

# Project scaffolder

Use this when the user asks to add a new module, package, or service.

## Steps

1. Run `scripts/scaffold.py <name>` to write the module skeleton.
2. Confirm the files it reports. Do not overwrite an existing module.
3. Tell the user which files were created.

## Notes

- Templates live in `templates/`. Edit those, not the generated output.
- The scaffolder refuses to run if the target directory already exists.

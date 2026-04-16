# SRE Extension

## Before committing

* Use `CHANGELOG.md` for extension AND single skills,  with `keepachangelog` and Semantic Versioning.
* Ensure development happens in a non-main branch (see below)
* If skill `pre-publish-checker` is available to you, use it before committing.

## git best practices

* Use branching for code changes/commits in this repo.
* Use this branching standard: `feature/YYMMDD-$USER-<short-description>`. Keep user to max 6chars (eg `ricc` -> `ricc`, `madkarra` -> `madkarra`).
* Before creating a branch, confirm with user what you intend to do. User might believe its not worth it for a small/cosmetic change to bother a new branch
* Keep short description to max 15 chars.
* if bug is available at birth, eg b/12345 add bXXXXX to it like `feature/YYMMDD-$USER-b12345-<short-description>`
* Ensure CHANGELOG.md and extension version are bumped as needed.
* At each PUSH of the branch, notify user the thing is available online at the relevant feature branch page.


## Skills

Skills should match the standards in `docs/SKILLS-STANDARDS.md`.

## DOs and DONTs

* Ensure no Google-only information is in this extension!
* If you find them in the code, remove them and find a decent placeholder - if unavailable just remove. Less is more!
* REFUSE to commit exfiltration of Google restricted information!! 
* DO NOT `git reset --hard main`, ever. 
* Use `git mv` vs `mv` if files are checked in `git`.
* Some tests are to remind ourselves we need to take manual action. Do NOT assume a broken test is for you to fix. Always ask first.

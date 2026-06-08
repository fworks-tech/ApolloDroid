# Contributing to ApolloDroid

ApolloDroid is organized around small, reviewable changes. Please keep changes focused and aligned with the repository conventions.

## Branch naming

Use one branch per issue when possible:

`type/issue-number-short-description`

Examples:

- `feat/issue-12-add-timer-skill`
- `fix/issue-18-handle-mic-error`
- `docs/issue-24-update-roadmap`

Prefer one logical change per branch. If a task is too large for one review, split it into a sequence of small branches that each leave the repository in a working state.

## Commit messages

Use the project convention:

`type(scope): subject`

Allowed types:

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `ci`
- `chore`

Keep commits granular:

- one commit for a single logical refactor
- one commit for a documentation-only update
- one commit for each isolated behavior change when practical

## Pull requests

- Open a PR from your branch into `main`.
- Fill in the pull request template.
- Include tests, screenshots, or logs when they help reviewers.
- Keep unrelated changes out of the same PR.
- Add the issue link, milestone, labels, and requested reviewers in the PR template.
- Use the granular commits section to explain the intent of each commit.

## Issue workflow

- Use the bug report template for defects.
- Use the feature request template for new capabilities.
- Use the task template for implementation, refactoring, or documentation work.
- Use the review issue template when you need structured review feedback on a change or issue.

## Validation

- Run the relevant checks for the files you changed.
- If you changed code, validate the touched slice before expanding scope.
- If you changed docs, verify links and references are accurate.
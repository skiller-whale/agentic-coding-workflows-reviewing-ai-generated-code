---
name: reviewable-change
description: Use for any change to this codebase that is more than a one-line fix. Plans the work as a sequence of small commits that are each easy to review, then makes them.
---

# Reviewable change

Work so that a human can review each commit on its own, quickly.

## 1. Plan the commits

Before changing any code, write a plan in `.plans/<branch name>.md`.
Start it with the request, quoted exactly as you were given it, with any later clarifications, so the reviewer can check the change against what was asked for.
Then list the commits you will make, in order.
For each commit:

- one sentence saying what it does (if you need "and", it's two commits);
- a type: `mech` for changes that should not change behaviour (renames, moves, reformatting), `feat` for new behaviour, `fix` for bug fixes, `test` for test-only changes;
- any decision you are making that the request didn't specify, so the reviewer can check it.

Mechanical changes come first, in their own commits, so the behaviour changes are small.

Commit the plan on its own, e.g. `docs: plan discount codes`, then carry on without waiting for approval.

## 2. Make each commit

- Make `mech` changes with a tool (a codemod, or a precise search and replace), not by hand, and say how in the commit message.
  A `mech` commit must not change any test assertions.
- Keep each `feat` or `fix` commit small: its tests, and the code they test, together.
- Run `uv run pytest` before every commit. Every commit must pass.
- Commit messages start with the type, e.g. `feat: reject expired discount codes`.

A hook checks every commit. If it blocks one, fix the commit rather than working round the hook.

## 3. Finish

When all the commits are done, update the plan if it changed, and add a summary to the end of it: what the change does, and the decisions you made that the reviewer should check.
Commit it on its own, e.g. `docs: summarise discount codes`.
End your reply with the same summary.

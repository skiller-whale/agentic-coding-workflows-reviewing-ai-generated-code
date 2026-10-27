---
name: reviewable-change
description: Use for any change to this codebase that is more than a one-line fix. Plans the work as a sequence of small commits that are each easy to review, then makes them.
---

# Reviewable change

Work so that a human can review each commit on its own, quickly.

## 1. Plan

Before changing any code, write a plan in `.plans/<feature>.md`. Start it with the request, quoted exactly as you were given it. Then list the commits you will make, in order, each with one sentence saying what it does. If you need "and" to describe a commit, it's two commits.

Commit the plan on its own, e.g. `docs: plan discount codes`, then carry on without waiting for approval.

## 2. Make each commit

- Keep each commit small, with its tests and the code they test together.
- Start each commit message with its kind:
  - `docs` for documentation and plans;
  - `fix` for bugfixes;
  - `feat` for new behaviour (alongside its tests);
  - `refactor` for changes that don't change behaviour, made before the `feat` commits that need them (a `refactor` commit must not change any tests).
- Run `uv run pytest` before every commit. Every commit must pass.

## 3. Finish

Add a summary to the end of the plan: a few sentences on what the change does, then any decisions you made over and above the prompt that should be flagged in the review. Commit it on its own, e.g. `docs: summarise discount codes`. End your reply with the same summary.

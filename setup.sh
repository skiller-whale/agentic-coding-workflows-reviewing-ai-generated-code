#!/usr/bin/env bash
# Make a local branch for each folder of patches in _branches/, off the current branch.
#
#   _branches/<branch>/*.patch  ->  branch <branch>, one commit per patch
#
# Patches are made with `git format-patch`, and applied with `git am`, so each commit
# keeps its author, date and message (the message is the pull request description).
# Commit dates come from the patches, so commit hashes are the same on every machine.
#
# Safe to re-run: branches that already exist are left alone, so it never touches a
# learner's own work.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

export GIT_COMMITTER_NAME="Skiller Whale" GIT_COMMITTER_EMAIL="setup@skillerwhale.com"

base=$(git symbolic-ref --short HEAD)
for dir in _branches/*/; do
    [ -d "$dir" ] || continue
    branch=$(basename "$dir")
    if git show-ref -q --verify "refs/heads/$branch"; then
        continue
    fi
    git checkout -q -b "$branch" "$base"
    if ! git am -q --committer-date-is-author-date "$dir"*.patch; then
        git am --abort
        git checkout -q "$base"
        git branch -q -D "$branch"
        echo "The patches in $dir don't apply to $base, so $branch wasn't created." >&2
        exit 1
    fi
    git checkout -q "$base"
    echo "Created $branch"
done

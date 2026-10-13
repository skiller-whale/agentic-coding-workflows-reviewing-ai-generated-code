"""PreToolUse hook: check a `git commit` before it runs.

Blocks (exit 2, reason on stderr) unless:
- the commit message starts with a type (mech, feat, fix, test, docs, refactor, chore);
- the tests pass;
- a feat/fix commit changes at most MAX_LINES non-test lines.
"""

import json
import re
import subprocess
import sys

MAX_LINES = 250
TYPES = ("mech", "feat", "fix", "test", "docs", "refactor", "chore")
# The start of the message: `-m "...` (or `-am`), `--message=...`, a `$(cat <<'EOF'` heredoc,
# or `-F - <<'EOF'`.
HEREDOC = r"""<<-?\s*['"]?\w+['"]?\s*\n"""
TYPE_PATTERN = re.compile(
    r"""(?:(?:-[a-zA-Z]*m|--message)[=\s]*["']?(?:\$\(cat\s*"""
    + HEREDOC
    + r""")?|(?:-[a-zA-Z]*F|--file)[=\s]*-\s*"""
    + HEREDOC
    + r""")\s*("""
    + "|".join(TYPES)
    + r""")(\([^)]*\))?!?:"""
)


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def main():
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    if not re.search(r"\bgit\b[^|;&]*\bcommit\b", command):
        return

    match = TYPE_PATTERN.search(command)
    if not match:
        block(f"Commit messages must start with a type: one of {', '.join(TYPES)}.")
    commit_type = match.group(1)

    # `git commit -a` stages at commit time, so look at everything since HEAD.
    stage_all = re.search(r"\s-[a-zA-Z]*a", command) is not None
    diff_args = ["HEAD"] if stage_all else ["--cached"]
    numstat = subprocess.run(
        ["git", "diff", "--numstat", *diff_args], capture_output=True, text=True
    ).stdout

    if commit_type in ("feat", "fix"):
        changed = 0
        for line in numstat.splitlines():
            added, removed, path = line.split("\t", 2)
            if path.startswith("tests/") or added == "-":
                continue
            changed += int(added) + int(removed)
        if changed > MAX_LINES:
            block(
                f"This {commit_type} commit changes {changed} non-test lines "
                f"(the limit is {MAX_LINES}). Split it into smaller commits."
            )

    tests = subprocess.run(["uv", "run", "pytest", "-q", "-x"], capture_output=True, text=True)
    if tests.returncode != 0:
        block("The tests fail, so this can't be committed:\n" + tests.stdout[-2000:])


if __name__ == "__main__":
    main()

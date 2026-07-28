#!/usr/bin/env bash
set -euo pipefail

# Link all Engineering Power skills into local agent harness directories:
#   - ~/.agents/skills  — Codex and Agent Skills-compatible harnesses
#   - ~/.claude/skills  — Claude Code
#   - ~/.cursor/skills  — Cursor
#
# Each entry is a symlink into this repo, so a `git pull` keeps installed
# skills up to date. Re-run after adding, removing, or renaming a skill.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
DESTS=("$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.cursor/skills")

# Collect canonical skill directories (any folder with a SKILL.md, excluding deprecated)
names=()
srcs=()
while IFS= read -r -d '' skill_md; do
    skill_dir="$(dirname "$skill_md")"
    name="$(basename "$skill_dir")"
    names+=("$name")
    srcs+=("$skill_dir")
done < <(find "$REPO/skills" -name "SKILL.md" -not -path "*/deprecated/*" -print0)

if [ ${#names[@]} -eq 0 ]; then
    echo "error: no skills found in $REPO/skills" >&2
    exit 1
fi

echo "Found ${#names[@]} skills to link."

for DEST in "${DESTS[@]}"; do
    # Safety: don't write symlinks back into the repo
    if [ -L "$DEST" ]; then
        resolved="$(readlink -f "$DEST" 2>/dev/null || echo "$DEST")"
        case "$resolved" in
            "$REPO"|"$REPO"/*)
                echo "error: $DEST is a symlink into this repo ($resolved)." >&2
                echo "Remove it (rm \"$DEST\") and re-run." >&2
                exit 1
                ;;
        esac
    fi

    mkdir -p "$DEST"

    for i in "${!names[@]}"; do
        name="${names[$i]}"
        src="${srcs[$i]}"
        target="$DEST/$name"

        # Remove existing (file or old symlink), preserve non-EP directories
        if [ -L "$target" ]; then
            rm -f "$target"
        elif [ -e "$target" ]; then
            # Only remove if it looks like an Engineering Power skill
            if [ -f "$target/SKILL.md" ]; then
                rm -rf "$target"
            else
                echo "skip: $target exists and is not a symlink (preserved)" >&2
                continue
            fi
        fi

        ln -sfn "$src" "$target"
    done

    echo "Linked ${#names[@]} skills into $DEST"
done

echo "Done. Skills will update on git pull."

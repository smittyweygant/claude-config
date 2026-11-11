#!/usr/bin/env bash
# Creates (or updates) the standard labels in a GitHub repo.
# Usage: labels.sh [owner/name]   — defaults to the repo in the current directory.
# Add area:* labels by hand; they belong to each project.
set -euo pipefail

repo_args=()
[ -n "${1:-}" ] && repo_args=(--repo "$1")

label() {
  gh label create "$1" --color "$2" --description "$3" --force ${repo_args[@]+"${repo_args[@]}"}
}

label type:bug    d73a4a "Something is broken"
label type:docs   0075ca "Documentation only"
label type:story  1d76db "A feature, from the user's point of view"
label type:task   5319e7 "One piece of a story"
label type:chore  c5def5 "Upkeep: tooling, process, dependencies"
label p1          b60205 "Now"
label p2          d93f0b "Next"
label p3          fef2c0 "Someday"

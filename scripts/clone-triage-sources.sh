#!/usr/bin/env bash

set -Eeuo pipefail

destination="${1:-.triage-sources}"
manifest="triage/source-repositories.json"

command -v gh >/dev/null
command -v jq >/dev/null
test -f "$manifest"

mkdir -p "$destination"

while IFS=$'\t' read -r slug directory; do
  target="$destination/$directory"

  if [[ -d "$target/.git" ]]; then
    echo "Source already available: $slug"
    continue
  fi

  echo "Cloning diagnostic source: $slug"
  gh repo clone "$slug" "$target" -- --depth 1
done < <(jq -r '.repositories[] | [.slug, .directory] | @tsv' "$manifest")

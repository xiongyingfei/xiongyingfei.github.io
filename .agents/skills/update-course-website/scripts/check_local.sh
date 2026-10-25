#!/usr/bin/env bash
# Build and validate locally; never push or deploy.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
site_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)"
build_root="$(mktemp -d /tmp/sa-site-check.XXXXXX)"
printf 'Build output: %s/_site\n' "$build_root"
cd -- "$site_root"
jekyll build --destination "$build_root/_site"
mkdir -p "$build_root/support/data"
cp .site-support/data/publishing.yaml "$build_root/support/data/publishing.yaml"
python3 -B .site-support/finalize_pages.py --source . --site "$build_root/_site" --support "$build_root/support"
python3 -B .site-support/check_site.py --dist "$build_root/_site"

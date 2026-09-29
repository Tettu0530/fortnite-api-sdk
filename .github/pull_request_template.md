## Summary

<!-- Please describe what this pull request changes and why. -->

## Related issues

<!-- e.g. Closes #123 -->

## Checklist

Please confirm the following before requesting a review. All of these are enforced by the required `ci-ok` check.

- [ ] `uv sync --locked --all-extras --dev` succeeds (and `uv.lock` is updated if dependencies changed)
- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format --check .` passes
- [ ] `uv run mypy` passes
- [ ] `uv run pytest` passes and coverage meets the configured threshold (currently 100%)
- [ ] `uv run python scripts/generate.py && git diff --exit-code` shows no changes (generated files were not edited by hand)
- [ ] `uv run python scripts/check_spec_coverage.py` reports no gaps
- [ ] `uv run pytest -m live` was run locally with `FN_API_KEY` if API behavior changed (optional)
- [ ] README / examples / docs were updated where relevant

## Notes for reviewers

<!-- Anything that deserves special attention, such as breaking changes or follow-up work. -->

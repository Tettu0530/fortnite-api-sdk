# Testing and Development Guide

This guide explains how to set up a development environment for `fortnite-api-sdk`, run every
check that continuous integration (CI) runs, run the live API tests, regenerate the SDK from a new
OpenAPI spec, and publish a release. Every command below is run from the repository root.

## Contents

- [Prerequisites](#prerequisites)
- [Setting up the environment](#setting-up-the-environment)
- [The checks](#the-checks)
- [Running the live API tests](#running-the-live-api-tests)
- [Regenerating the SDK from a new spec](#regenerating-the-sdk-from-a-new-spec)
- [How CI maps to these commands](#how-ci-maps-to-these-commands)
- [Repository secrets and branch protection](#repository-secrets-and-branch-protection)
- [Release flow](#release-flow)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** 0.5 or later. It manages the Python interpreter, the virtual
  environment and the lock file (`uv.lock`). You can install it with
  `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS / Linux) or
  `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"` (Windows).
- **Python 3.10 – 3.14.** You do not need to install Python yourself: uv downloads the version in
  `.python-version` (3.13) when required. To test against another version, run
  `uv python install 3.10` and pass `--python 3.10` to `uv sync` / `uv run`.
- **git**, for the "generated code is committed" check.
- Optional: the [GitHub CLI](https://cli.github.com/) (`gh`) for configuring secrets and releases.

## Setting up the environment

```bash
git clone https://github.com/Tettu0530/fortnite-api-sdk.git
cd fortnite-api-sdk
uv sync --locked --all-extras --dev
```

`uv sync` creates `.venv/`, installs the package in editable mode, and installs the development
tools from the `dev` dependency group in `pyproject.toml` (pytest, pytest-asyncio, pytest-cov, ruff
and mypy). `--locked` makes the command fail instead of silently updating `uv.lock`; if you change
dependencies in `pyproject.toml`, run `uv lock` and commit the updated `uv.lock`.

Prefix every tool with `uv run` (for example `uv run pytest`) so that it runs inside the project
environment. You do not need to activate the virtual environment.

## The checks

CI runs the following commands. Please run them locally before opening a pull request.

| Command | What it checks |
| --- | --- |
| `uv sync --locked --all-extras --dev` | `uv.lock` is up to date with `pyproject.toml`, and the environment can be installed. |
| `uv run ruff check .` | Lint rules (pycodestyle, pyflakes, isort, bugbear, pyupgrade, simplify, pylint, pytest-style, async and more; see `[tool.ruff.lint]`). |
| `uv run ruff format --check .` | Code formatting. Run `uv run ruff format .` to apply it. |
| `uv run mypy` | Static types. `src/fortnite_api` is checked in `strict` mode (with the Pydantic plugin); `tests/` and `scripts/` are checked with relaxed rules. |
| `uv run pytest` | The offline unit tests, with branch coverage. Live tests are excluded. |
| `uv run pytest -m live` | The live API smoke tests (requires `FN_API_KEY`; see below). |
| `uv run python scripts/generate.py && git diff --exit-code` | The generated code in `src/fortnite_api` matches `openapi/swagger.json` and the generator, i.e. nobody edited generated files by hand or forgot to regenerate. |
| `uv run python scripts/check_spec_coverage.py` | Every spec operation is served by exactly one sync and one async method, with all parameters, bodies, deprecations and response types. |
| `uv run python scripts/check_spec_drift.py` | The live spec published by the API still matches `openapi/swagger.json`. |

A convenient way to run all the offline checks in one go:

```bash
uv sync --locked --all-extras --dev \
  && uv run ruff check . \
  && uv run ruff format --check . \
  && uv run mypy \
  && uv run pytest \
  && uv run python scripts/generate.py && git diff --exit-code \
  && uv run python scripts/check_spec_coverage.py
```

### Unit tests and coverage

`uv run pytest` uses the options in `[tool.pytest.ini_options]`:

- `-m "not live"` deselects the live tests, so no network access or API key is needed.
- Coverage is measured for the `fortnite_api` package with branch coverage
  (`--cov=fortnite_api --cov-branch`). A per-line report is printed in the terminal and
  `coverage.xml` is written for CI.
- The build fails if total coverage drops below `fail_under` in `[tool.coverage.report]`
  (currently **100%**). New code should come with tests; the generated resources are exercised
  automatically by `tests/test_spec_tools.py`, which calls every SDK method once.
- `filterwarnings = ["error"]` turns every warning into a test failure, so deprecations and
  resource leaks are noticed early. Tests that expect a warning use `pytest.warns(...)`.
- `--strict-markers` rejects unknown markers; the only custom marker is `live`.

Useful variations:

```bash
uv run pytest tests/test_transport.py --no-cov   # a single file (skip the coverage threshold)
uv run pytest -k deprecated --no-cov             # tests whose name matches an expression
uv run pytest --cov-report=html                  # additionally write htmlcov/index.html
uv run --python 3.10 pytest                      # run against another Python version
```

Please add `--no-cov` whenever you run only part of the suite, because a partial run cannot reach
the coverage threshold.

### Spec coverage check

`scripts/check_spec_coverage.py` drives every public method of `FortniteAPI` and `AsyncFortniteAPI`
through an `httpx.MockTransport` (no network access) and compares each recorded request with
`openapi/swagger.json`. It exits with status 1 and lists every gap, for example:

```text
GAPS: 2
    GET /api/v1/brand-new: mapped to 0 methods []
    shop.get_current: query param newParam not exposed
```

SDK methods that intentionally call endpoints missing from the spec (currently the multi-file
`parsing.parse_multiple*` methods) are listed in `KNOWN_EXTRAS` in the script.

### Spec drift check

`scripts/check_spec_drift.py` downloads `https://prod.api-fortnite.com/swagger/v1/swagger.json`
(standard library only) and prints a Markdown summary of added, removed and changed operations and
schemas. The exit status is `0` when the specs are identical, `1` when they differ, and `2` when the
live spec could not be downloaded or parsed.

```bash
uv run python scripts/check_spec_drift.py                         # print the summary
uv run python scripts/check_spec_drift.py --output drift.md       # also write it to a file
uv run python scripts/check_spec_drift.py --save openapi/swagger.json   # save the live spec
```

## Running the live API tests

`tests/test_live.py` contains smoke tests that call the real API and check that responses parse
into the typed models (shop, calendar, cosmetics, weapons, news, map, playlists, battle pass,
sprites, quest definitions, AES keys, tournaments, power rankings, account lookup, and an async
parity test). They assert types and shapes rather than exact values, so normal data changes do not
break them. They are marked `live` and are skipped when no API key is configured.

1. **Get an API key.** Create a free account at [api-fortnite.com](https://api-fortnite.com) and
   copy your API key from the dashboard.
2. **Run the tests:**

   ```bash
   export FN_API_KEY="your-api-key"          # PowerShell: $env:FN_API_KEY = "your-api-key"
   uv run pytest -m live
   ```

   The coverage threshold is not enforced for `-m live` runs.

### Tests that need a user token

A few endpoints require the `x-fortnite-token` header, which is a Fortnite OAuth access token for a
specific Epic account. These tests are skipped unless both variables below are set:

| Variable | Purpose |
| --- | --- |
| `FN_API_KEY` | Your api-fortnite.com API key (required for all live tests). |
| `FN_FORTNITE_TOKEN` | A user access token, sent as `x-fortnite-token`. |
| `FN_ACCOUNT_ID` | The Epic account ID that the token belongs to. |

You can obtain a token with the SDK's OAuth helpers, for example the device-code flow:

```python
from fortnite_api import FortniteAPI

with FortniteAPI(api_key="your-api-key") as client:
    flow = client.oauth.get_token()
    print(flow)  # open the URL in the response and sign in with your Epic account
    input("Press Enter after signing in...")
    auth = client.oauth.complete(body={"flowId": flow["flowId"]})
    print(auth)  # contains the access token and the account ID
```

Please treat the token like a password: never commit it, paste it into issues, or print it in CI
logs. Tokens expire; use `client.oauth.refresh_token(...)` or repeat the flow when they do.

## Regenerating the SDK from a new spec

The resource classes, models and client in `src/fortnite_api` (everything except `_transport.py`,
`errors.py`, `interpret.py`, `protocol.py`, `retry.py` and `__init__.py`) are generated by `scripts/generate.py` from `openapi/swagger.json`.
Please do not edit generated files by hand: change the generator instead and regenerate.

1. **Download the new spec** (or let the drift check do it):

   ```bash
   uv run python scripts/check_spec_drift.py --save openapi/swagger.json
   ```

   The summary printed by the command tells you which operations and schemas changed.

2. **Update the endpoint table** in `scripts/generate.py` (`RESOURCES`) for any new or removed
   operations. Query parameters, request bodies, response types and deprecations are read from the
   spec automatically; the table only maps operations to method names and holds overrides.

3. **Regenerate.** The generator formats its output with ruff, so the result is deterministic and
   already passes `ruff format --check`:

   ```bash
   uv run python scripts/generate.py
   ```

4. **Verify the result:**

   ```bash
   uv run python scripts/check_spec_coverage.py   # must report "GAPS: 0"
   uv run ruff check . && uv run mypy && uv run pytest
   ```

5. **Update the documentation.** Add new methods to `README.md` (and the migration notes if a method
   was renamed or removed), then bump the version if you are preparing a release.

## How CI maps to these commands

The `CI` workflow (`.github/workflows/ci.yml`) runs on every pull request and on pushes to `main`:

| Job | Commands |
| --- | --- |
| `lint` | `uv sync --locked --all-extras --dev`, `uv run ruff check .`, `uv run ruff format --check .` |
| `typecheck` | `uv run mypy` |
| `test` | `uv run pytest` on Linux, macOS and Windows with Python 3.10 – 3.14; uploads `coverage.xml` |
| `test (lowest direct deps)` | `uv run pytest` with the oldest supported versions of `httpx` and `pydantic` |
| `codegen` | `uv run python scripts/generate.py`, then fails if `git diff` is not empty; `uv run python scripts/check_spec_coverage.py` |
| `build` | `uv build` with the hash-pinned backend from `build-constraints.txt`, `twine check` from the locked `dist` group, and an install smoke test of the wheel and sdist |
| `docs-examples` | Byte-compiles `examples/` and the Python snippets in `README.md` |
| `workflow-lint` | Lints the workflow files |
| `ci-ok` | Succeeds only if every job above succeeded |

`ci-ok` is the single required status check for branch protection, so adding or renaming jobs does
not require changing the protection rules.

Other workflows:

- **Live API tests** (`live.yml`): runs `uv run pytest -m live` nightly, on pushes to `main`, and
  on demand. It runs in the `live` environment, is skipped when the `FN_API_KEY` secret is not configured and is not a required
  check, because the external API can be temporarily unavailable.
- **Spec drift** (`spec-drift.yml`): runs `scripts/check_spec_drift.py` daily and opens, updates or
  closes an issue labelled `spec-drift` with the Markdown summary.
- **CodeQL** and **Dependency review**: security analysis of the code and of dependency changes in
  pull requests.
- **Publish to PyPI** (`publish.yml`): see [Release flow](#release-flow).

## Repository secrets and branch protection

### Secrets for the live tests

The live tests in CI read their secrets from the `live` **environment**, not from repository-level
secrets. The environment only accepts deployments from `main`, so a workflow running on any other
branch cannot read them. Secrets are also never exposed to workflows triggered by pull requests
from forks.

| Environment secret | Required | Purpose |
| --- | --- | --- |
| `FN_API_KEY` | Yes | The api-fortnite.com API key. Without it the `live` job only prints a notice. |
| `FN_FORTNITE_TOKEN` | No | A user access token that enables the user-token tests. Tokens expire, so refresh it when those tests start failing with 401. |
| `FN_ACCOUNT_ID` | No | The Epic account ID the token belongs to (needed together with `FN_FORTNITE_TOKEN`). |

A maintainer can add them with:

```bash
gh secret set FN_API_KEY --env live --repo Tettu0530/fortnite-api-sdk
gh secret set FN_FORTNITE_TOKEN --env live --repo Tettu0530/fortnite-api-sdk   # optional
gh secret set FN_ACCOUNT_ID --env live --repo Tettu0530/fortnite-api-sdk       # optional
# paste each value when prompted
```

or in the web UI under **Settings → Environments → live → Environment secrets**. Running
`live.yml` manually (`workflow_dispatch`) from a branch other than `main` fails at the environment
check by design; run the live tests locally instead (see
[Running the live API tests](#running-the-live-api-tests)).

### Branch protection and merge settings

`main` is protected with the following rules:

- A pull request is required before merging (direct pushes are rejected).
- The `ci-ok` status check must pass, and the branch must be up to date with `main` (strict).
- All review conversations must be resolved.
- Linear history is required; force-pushes and deletion of `main` are blocked.
- The rules also apply to administrators.

The repository only allows **Squash and merge** (merge commits and rebase merging are disabled), and
head branches are deleted automatically after merging. To inspect the current settings:

```bash
gh api repos/Tettu0530/fortnite-api-sdk/branches/main/protection
gh api repos/Tettu0530/fortnite-api-sdk --jq '{allow_squash_merge, allow_merge_commit, allow_rebase_merge, delete_branch_on_merge}'
```

## Release flow

1. Make sure `main` is green (`ci-ok` passed) and the live tests pass.
2. Bump the version in **both** `pyproject.toml` (`[project] version`) and
   `src/fortnite_api/__init__.py` (`__version__`), run `uv lock`, and update the README
   migration notes and the release notes. Open a pull request with these changes and merge it once CI passes.
3. Create a GitHub release whose tag is the version with a `v` prefix, for example:

   ```bash
   gh release create v0.2.0 --title "v0.2.0" --notes-file RELEASE_NOTES.md
   ```

4. Publishing the release triggers `publish.yml`, which checks that the tag matches both version
   strings, runs the full CI workflow again, builds the distributions and uploads them to PyPI via
   trusted publishing (the `pypi` environment). No PyPI token is stored in the repository.
5. Verify the new version on [PyPI](https://pypi.org/project/fortnite-api-sdk/) and, optionally,
   install it in a clean environment: `uv run --with fortnite-api-sdk==0.2.0 --no-project python -c "import fortnite_api; print(fortnite_api.__version__)"`.

## Troubleshooting

- **`uv sync --locked` fails with "The lockfile needs to be updated".** Run `uv lock` and commit
  `uv.lock`.
- **`git diff --exit-code` fails after `generate.py`.** Commit the regenerated files. If the diff
  shows only formatting changes, make sure you are using the ruff version pinned in `uv.lock`
  (always run the generator with `uv run`).
- **"Required test coverage of 100% not reached".** Add tests for the new code, or pass `--no-cov`
  when you intentionally run only part of the suite.
- **A test fails with an unexpected warning.** Warnings are errors; fix the cause, or, for a known
  third-party warning, add a narrowly scoped `ignore` entry to `filterwarnings` in `pyproject.toml`.
- **Live tests fail with `[401] Invalid or inactive API key`.** Check the value of `FN_API_KEY`.

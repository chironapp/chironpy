# Agent Instructions

This file provides guidance for AI coding agents (Claude, Codex, etc.) working in this repository.

## Project overview

`chironpy` is a Python library for loading, normalising, and analysing endurance sports activity data (FIT, GPX, TCX, Strava). The core class is `WorkoutData` — a `pandas.DataFrame` subclass in `chironpy/models/workout.py`.

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before starting work. It covers environment setup, testing, linting, example data conventions, and the full release workflow.

---

## Development workflow

```bash
# Install
poetry install

# Run tests
poetry run pytest tests/

# Lint
poetry run black .
```

All tests must pass and code must be `black`-formatted before any commit.

---

## Documentation requirements

### Every user-visible change must update two files:

**1. `docs/api_reference.md`**

Keep this file accurate and complete for the `WorkoutData` public API:

- Add an entry for every new public method or property.
- Update entries when signatures, defaults, or behaviour change.
- Delete entries for removed methods.
- Include a parameter table (for multi-param methods) and a concise usage example.

**2. `docs/changelog.md`**

Record every feature, behaviour change, deprecation, removal, bug fix, or security fix:

- Always add new entries under `## [Unreleased]`.
- If `## [Unreleased]` does not exist, create it immediately above the most recent versioned entry (e.g. `## [0.28.2] - ...`), with the appropriate sub-headings (`### Added`, `### Changed`, `### Fixed`, etc.).
- Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format already used in the file.
- Do **not** add entries for internal refactors, test-only changes, or dev tooling updates.

---

## Key files and locations

| Path                          | Purpose                                                             |
| ----------------------------- | ------------------------------------------------------------------- |
| `chironpy/models/workout.py`  | `WorkoutData` class — all model methods live here                   |
| `chironpy/constants.py`       | Standard column name enums (`DataTypeEnum`, `DataTypeEnumExtended`) |
| `chironpy/examples/data/`     | Bundled example workout files                                       |
| `chironpy/examples/index.yml` | Registry of all example files — update when adding new ones         |
| `docs/api_reference.md`       | Public API documentation                                            |
| `docs/changelog.md`           | User-facing changelog                                               |
| `tests/`                      | pytest test suite                                                   |

---

## Checklist before finishing any task

- [ ] New/changed public methods documented in `docs/api_reference.md`
- [ ] `docs/changelog.md` updated under `[Unreleased]` for every user-visible change
- [ ] Tests added or updated for new behaviour
- [ ] `poetry run pytest tests/` passes
- [ ] Code formatted with `black`

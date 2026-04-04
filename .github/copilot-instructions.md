# GitHub Copilot Instructions

## Project overview

`chironpy` is a Python library for loading, normalising, and analysing endurance sports activity data (FIT, GPX, TCX, Strava). The core class is `WorkoutData` — a `pandas.DataFrame` subclass that enforces a standard column schema and provides higher-level methods for metrics, interval analysis, and merging multi-file sessions.

Before making changes, read [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the full development workflow, environment setup, testing, linting, and release process.

---

## Key conventions

- `WorkoutData` lives in `chironpy/models/workout.py`. Add new methods there; do not scatter model logic across other modules.
- Standard column names are defined in `chironpy/constants.py` (`DataTypeEnum`, `DataTypeEnumExtended`). Use those names — do not invent new column aliases.
- New example data files go in `chironpy/examples/data/` and **must** be registered in `chironpy/examples/index.yml`.
- Tests live in `tests/`. Match the existing structure: one file per module, `tests/test_<module>.py`. Use pytest; follow the `make_<thing>()` helper pattern for synthetic data.
- Use `poetry run pytest tests/` to run the test suite. All tests must pass before committing.
- Format code with `black` (`make lint` or `poetry run black .`).

---

## Documentation

**Keep documentation in sync with every code change.**

### API reference — `docs/api_reference.md`

- Add an entry for every new public method or property on `WorkoutData`.
- Update existing entries when signatures, parameters, or behaviour change.
- Include a parameter table (when there are multiple params) and a short usage example.
- Remove entries for methods that are deleted.

### Changelog — `docs/changelog.md`

- Record every feature addition, behaviour change, deprecation, removal, bug fix, or security fix.
- Always add entries under `## [Unreleased]`. If that section does not exist, create it at the top of the changelog (above the most recent versioned entry) with the heading and appropriate sub-headings (`### Added`, `### Changed`, `### Fixed`, etc.).
- Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format already used in the file.
- Do **not** add entries for internal refactors, test changes, or tooling updates that have no user-visible impact.

---

## Checklist before finishing any task

- [ ] New/changed public methods are documented in `docs/api_reference.md`
- [ ] `docs/changelog.md` has an entry in `[Unreleased]` for any user-visible change
- [ ] Tests added or updated for new behaviour
- [ ] `poetry run pytest tests/` passes
- [ ] Code formatted with `black`

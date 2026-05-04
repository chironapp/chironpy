# Contributing

Thanks for checking out chironpy!

## Types of contributions we are looking for

Contributing to documentation:

- Notify us of errors in the documentation or provide fixes for them.
- Suggest or provide additions to the documentation.

Contributing to code:

- Notify us of bugs in our code or provide fixes for them.
- Suggest or provide new features.

## Ground rules & expectations

- Be kind and thoughtful in your conversations around this project.
- Be considerate that the maintainers of this project do their work on a voluntary basis: do not expect commercial support when you did not pay for it.
- If you open a pull request, please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
- When adding content, please consider if it is widely valuable.

## How to contribute

Start by searching through the [issues](https://github.com/chironapp/chironpy/issues) and [pull requests](https://github.com/chironapp/chironpy/pulls) to see whether someone else has raised a similar idea or question.

- **If your contribution is minor,** such as a typo fix, open a pull request.
- **If your contribution is major,** such as a new feature or guide, start by opening an issue first.

---

## Environment Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Clone and install

```bash
git clone https://github.com/chironapp/chironpy.git
cd chironpy
uv sync --group dev --group docs
```

`uv sync` installs the package in editable mode along with all dev and docs dependencies (pytest, JupyterLab, ruff, mkdocs, etc.).

Verify the install:

```bash
uv run python -c "import chironpy; print('ok')"
```

---

## Running Tests

```bash
uv run pytest tests/
```

---

## Prototyping and Exploring

The `lab/` directory is the workspace for development scripts and notebooks. It contains:

- `lab/getting_started.ipynb` — starter notebook covering the core APIs
- `lab/data/` — put your own `.fit`, `.tcx`, `.gpx`, or Strava JSON files here for prototyping

Launch JupyterLab:

```bash
uv run jupyter lab lab/
```

The kernel will have `chironpy` available directly — no path manipulation needed.

To run a script from the project root:

```bash
uv run python lab/my_script.py
```

### Bundled example data

The `chironpy/examples/data/` directory contains example workout files included with the package. Access them via:

```python
import chironpy

example = chironpy.examples(path="4078723797.fit")
data = chironpy.read_file(example.path, resample=True, interpolate=True)
```

See `lab/getting_started.ipynb` for a full walkthrough.

### Polished examples

The `examples/` directory contains scripts demonstrating complete usage patterns — treat these as reference implementations, not scratch space.

---

## Linting

```bash
uv run ruff format chironpy/ tests/ examples/
uv run ruff check chironpy/ tests/ examples/
```

## Requirements for merging code

- New features should be generic and not specific to one user or use-case.
- New features should be properly unit tested. Do not forget to test your [unhappy paths](https://en.wikipedia.org/wiki/Happy_path) too.
- All tests should pass.
- The code should pass the ruff format and lint checks.
- New features should include documentation with at least a basic example.
- New features that include models or algorithms should cite the source (e.g. a scientific article) in the documentation.

---

## Building Docs

```bash
uv run mkdocs serve
```

Documentation source files are in the `docs/` directory. Markdown and Jupyter notebook (`.ipynb`) files are both rendered as pages. To add a new page, add the file and include it in the `nav` section of `mkdocs.yml`.

---

## Example data

Example workout files are stored in `chironpy/examples/data/`. Every new file added there must also be registered in `chironpy/examples/index.yml`. See the [example data docs](https://chironpy.chironapp.com/features/example_data/) for usage.

---

## FIT profile

The `Profile.xlsx` from the [Garmin FIT SDK](https://developer.garmin.com/fit/download/) is stored in the repo as `chironpy/io/fit_profile.json`. To update it when Garmin releases a new SDK version:

```python
from chironpy.io import fit
fit._import_fit_profile("path/to/new/Profile.xlsx")
```

---

## Continuous integration

- Tests and linting run on every push and pull request.
- On every push to `master`, the documentation site is automatically redeployed.
- On every new GitHub Release, the package is published to PyPI and the docs are redeployed.

---

## Releasing

### 1. Run the tests

```bash
uv run pytest tests/
```

### 2. Bump the version

Update the `version` field in `pyproject.toml` manually, then regenerate the lock file:

```bash
uv lock
```

### 3. Update the changelog

Add a new entry to `docs/changelog.md` following the existing format.

### 4. Commit and push

```bash
git add pyproject.toml uv.lock docs/changelog.md
git commit -m "bump version to <version>"
git push origin master
```

Pushing to `master` automatically triggers the **Publish Documentation** workflow, which redeploys the docs site via `mkdocs gh-deploy`.

### 5. Create a GitHub Release

Go to [Releases](https://github.com/chironapp/chironpy/releases) → **Draft a new release** → tag it `v<version>` → publish it.

Publishing the release triggers the **Publish** workflow, which builds the package and pushes it to PyPI using the `PYPI_TOKEN` repository secret.

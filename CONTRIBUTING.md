# Contributing

## Environment Setup

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

### Clone and install

```bash
git clone https://github.com/chironapp/chironpy.git
cd chironpy
poetry install
```

`poetry install` installs the package in editable mode along with all dev dependencies (pytest, JupyterLab, linting tools, etc.). No separate `pip install -e .` step is needed.

Verify the install:

```bash
poetry run python -c "import chironpy; print('ok')"
```

---

## Running Tests

Run the test suite locally:

```bash
poetry run pytest tests/
# or
make pytest
```

Run tests in a clean Docker environment (matches CI):

```bash
make test
```

---

## Prototyping and Exploring

The `lab/` directory is the workspace for development scripts and notebooks. It contains:

- `lab/getting_started.ipynb` — starter notebook covering the core APIs
- `lab/data/` — put your own `.fit`, `.tcx`, `.gpx`, or Strava JSON files here for prototyping

Launch JupyterLab:

```bash
poetry run jupyter lab lab/
# or
make lab
```

The kernel will have `chironpy` available directly — no path manipulation needed.

To run a script from the project root:

```bash
poetry run python lab/my_script.py
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
make lint
# or
poetry run black .
```

---

## Building Docs

```bash
make docs
```

---

## Releasing

### 1. Run the tests

Before releasing, confirm the test suite passes locally:

```bash
poetry run pytest tests/
# or
make pytest
```

To run tests in a clean Docker environment matching CI:

```bash
make test
```

### 2. Bump the version

Use Poetry to update the version in `pyproject.toml`:

```bash
poetry version patch   # or: minor, major
```

### 3. Update the changelog

Add a new entry to `docs/changelog.md` following the existing format.

### 4. Commit and push

```bash
git add pyproject.toml docs/changelog.md
git commit -m "bump version to $(poetry version -s)"
git push origin master
```

Pushing to `master` automatically triggers the **Publish Documentation** workflow, which redeploys the docs site via `mkdocs gh-deploy`.

### 5. Create a GitHub Release

Go to [Releases](https://github.com/chironapp/chironpy/releases) → **Draft a new release** → tag it `v<version>` → publish it.

Publishing the release triggers the **Publish** workflow, which builds the package and pushes it to PyPI using the `PYPI_TOKEN` repository secret.

# newpackage

`newpackage` is a CLI tool for scaffolding opinionated Python packages with a `src/` layout, MIT license, and sensible defaults for modern Python packaging.

* Creates a project with the same structure as `shortgit` (or other reference packages)
* MIT License included automatically with year and author
* Initializes a GitHub repo via `shortgit init` (without pushing)
* Designed for reproducible, distributable Python packages (pip- and mamba-installable)

---

## Prerequisites

* Python 3.9+
* `git` installed and on `PATH`
* GitHub CLI `gh` installed and authenticated: `gh auth login`
* `shortgit` installed (for repo bootstrapping)

---

## Installation

```bash
pip install .
```

(Optional for development):

```bash
pip install -e .
```

---

## Quick Start

```bash
# Scaffold a new package called mypackage, authored by Mihai Ion
newpackage mypackage --author "Mihai Ion"
```

This will create:

* `src/mypackage/` (empty, ready for your code)
* `pyproject.toml` with package metadata
* `README.md` with starter info
* `LICENSE` with MIT text
* `.gitignore` for Python and data files
* `.git/` and remote GitHub repo (public)

---

## Command Reference

```bash
newpackage <project_name> [OPTIONS]
```

### Positional arguments:

* **project\_name**: Name of the new package (used for folder, PyPI name, and src subfolder)

### Key options:

* **--author**: Author name for LICENSE and `pyproject.toml` 
* **--description**: Short package description 
* **--private**: Make the GitHub repo private instead of public 

Run `newpackage --help` for full set of options.
---

## Example

```bash
# Public repo
newpackage coolutils --author "Jane Doe"

# Private repo with description
newpackage secretlib --author "Jane Doe" --description "Private utilities" --private
```

---

## Notes

* By default, the new package will call `shortgit init` on creation, but will **not** push.
* MIT license year is auto-detected from the system date.
* Designed to avoid silent overwrites; will fail if the project folder already exists.

---

## License

MIT

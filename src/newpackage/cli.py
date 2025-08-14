import subprocess, shutil, datetime, re
from pathlib import Path
from typing import Optional
from enum import Enum
import typer

app = typer.Typer(add_completion=False)

# ---------------- utils ----------------

def run(cmd, cwd: Optional[Path] = None) -> str:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}"
        )
    return p.stdout.strip()


def ensure_tool(name: str, url: str):
    if shutil.which(name) is None:
        raise RuntimeError(f"'{name}' not found on PATH. Install it: {url}")


def normalize_import_name(name: str) -> str:
    s = name.strip().lower().replace('-', '_')
    s = re.sub(r"[^0-9a-z_]+", "_", s)
    if not s or s[0].isdigit():
        s = f"pkg_{s}"
    return s


class Visibility(str, Enum):
    public = "public"
    private = "private"
    internal = "internal"


# ---------------- file templates ----------------

MIT_TEMPLATE = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

GITIGNORE_TEMPLATE = """# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/

# Build artifacts
build/
dist/

# IDE
.idea/
.vscode/

# Data directories
**/data/**

# Common data files
*.parquet
*.pq
*.feather
*.pkl
*.pickle
*.csv
*.tsv
*.txt
*.jsonl
*.json
*.dta
*.sas7bdat
*.xpt
*.sav
*.zsav
*.rds
*.RData
*.xlsx
*.xls
*.xlsm
*.xlsb
*.h5
*.hdf5
*.npz
*.npy
"""

README_TEMPLATE = """# {project_name}

{project_name} — scaffolded by **newpackage**.

**Author:** {author}  
**License:** MIT (c) {year} {author}

## Layout
```
{project_name}/
  ├─ pyproject.toml
  ├─ README.md
  ├─ LICENSE
  ├─ .gitignore
  └─ src/
     └─ {import_name}/
        └─ __init__.py
```

## Development install
```bash
pip install -e .
```

## Notes
- MIT license included.
- `src` layout with explicit package map in `pyproject.toml`.
- A console script entry point is pre-wired to `{import_name}.cli:main` and exposes the `{import_name}` command. Create `src/{import_name}/cli.py` with a `main()` to activate it.
"""


def pyproject_toml(project_name: str, import_name: str, version: str, py_min: str, author: str) -> str:
    return f"""[build-system]
requires = ["hatchling>=1.21"]
build-backend = "hatchling.build"

[project]
name = "{project_name}"
version = "{version}"
description = "A new Python package scaffolded by newpackage."
readme = "README.md"
requires-python = ">={py_min}"
license = {{file = "LICENSE"}}
authors = [{{name = "{author}"}}]
dependencies = []

[project.scripts]
{import_name} = "{import_name}.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/{import_name}"]
"""


# ---------------- command ----------------

@app.command()
def create(
    package_name: str = typer.Argument(..., help="Project/package (distribution) name. Also the folder to create."),
    author: str = typer.Option("Author Name", "--author", "-a", help="Author name for LICENSE, README, and pyproject (required)"),
    import_name: Optional[str] = typer.Option(None, "--import-name", "-i", help="Import/package folder name (default: derived from package_name)"),
    version: str = typer.Option("0.1.0", "--version", "-v", help="Initial version"),
    py_min: str = typer.Option("3.9", "--python", "-p", help="Minimum Python version"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="GitHub repo description for shortgit init"),
    org: Optional[str] = typer.Option(None, "--org", help="GitHub org/owner for shortgit init"),
    visibility: Visibility = typer.Option(Visibility.public, "--visibility", help="Visibility for shortgit init"),
    branch: str = typer.Option("main", "--branch", "-b", help="Default branch for shortgit init"),
    no_init: bool = typer.Option(False, "--no-init", help="Only scaffold files; do not run shortgit init"),
):
    """Scaffold a new package in the current directory and optionally run `shortgit init` in it (no push)."""

    # Tool checks
    ensure_tool("git", "https://git-scm.com/downloads")
    if not no_init:
        ensure_tool("gh", "https://cli.github.com/")
        ensure_tool("shortgit", "https://github.com/ionmihai/shortgit")

    project_dir = Path(package_name).resolve()
    pkg = normalize_import_name(import_name or package_name)
    if project_dir.exists() and any(project_dir.iterdir()):
        raise RuntimeError(f"Target directory '{project_dir}' exists and is not empty.")

    # Create folders
    (project_dir / f"src/{pkg}").mkdir(parents=True, exist_ok=True)

    # Compute year once
    year = datetime.datetime.now().year

    # Write files
    (project_dir / "LICENSE").write_text(MIT_TEMPLATE.format(year=year, author=author), encoding="utf-8")
    (project_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE, encoding="utf-8")
    (project_dir / "README.md").write_text(
        README_TEMPLATE.format(project_name=package_name, import_name=pkg, author=author, year=year),
        encoding="utf-8",
    )
    (project_dir / f"src/{pkg}/__init__.py").write_text("__all__ = []\n", encoding="utf-8")
    (project_dir / "pyproject.toml").write_text(
        pyproject_toml(package_name, pkg, version, py_min, author),
        encoding="utf-8",
    )

    typer.echo(f"Scaffolded {package_name} at {project_dir}")

    # Optionally run shortgit init in the new folder (no push)
    if not no_init:
        args = [
            "shortgit",
            "init",
            str(project_dir),
            "--name",
            package_name,
            "--visibility",
            visibility.value,
            "--branch",
            branch,
        ]
        if description:
            args += ["--description", description]
        if org:
            args += ["--org", org]
        try:
            run(args)
            typer.echo("shortgit init completed.")
        except Exception as e:
            typer.echo(f"shortgit init failed: {e}")
            raise


def main(): app()
if __name__ == "__main__": main()

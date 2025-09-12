import subprocess 
import shutil
import datetime
import re
from pathlib import Path
from typing import Optional
from enum import Enum
import typer

HERE = Path(__file__).parent
TEMPLATE_DIR = HERE / "_templates"

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

def render_template(name: str, **params) -> str:
    text = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
    return text.format(**params)

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
    (project_dir / "external").mkdir(parents=True, exist_ok=True)           #Documentation files from the vendor, will be gitignored
    (project_dir / "data").mkdir(parents=True, exist_ok=True)           #For testing, will be gitignored
    (project_dir / "notebooks/dev").mkdir(parents=True, exist_ok=True)  #For dev experiments, will be gitignored
    (project_dir / "notebooks/test").mkdir(parents=True, exist_ok=True)  #For testing, will be gitignored
    (project_dir / "notebooks/docs").mkdir(parents=True, exist_ok=True)  #For reporting on functionality, will NOT be gitignored

    # Compute year once
    year = datetime.datetime.now().year
    ctx = dict(
        project_name=package_name,
        import_name=pkg,
        author=author,
        year=year,
        version=version,
        py_min=py_min,
    )

    # Create files
    (project_dir / "LICENSE").write_text(render_template("LICENSE_MIT.txt", **ctx), encoding="utf-8")
    (project_dir / ".gitignore").write_text(render_template("GITIGNORE.txt", **ctx), encoding="utf-8")
    (project_dir / "README.md").write_text(render_template("README.txt", **ctx), encoding="utf-8")
    (project_dir / "pyproject.toml").write_text(render_template("PYPROJECT.txt", **ctx), encoding="utf-8")
    (project_dir / f"src/{pkg}/__init__.py").write_text("__all__ = []\n", encoding="utf-8")
    
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

def main(): 
    app()

if __name__ == "__main__": 
    main()

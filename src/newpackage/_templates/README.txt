# {project_name}

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
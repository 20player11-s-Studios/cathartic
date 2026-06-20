# Contributing

Thanks for your interest in Cathartic!

## Getting Started

1. Fork the repo
2. Create a feature branch: `git switch -c feat/my-thing`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Make your changes
5. Run tests: `pytest`
6. Push and open a pull request

## Guidelines

- Keep the code readable and commented where needed
- Add or update tests for new functionality
- Match the existing code style (single-word vars, early returns, no `else`)
- Open an issue first for significant changes

## Structure

```
cathartic/
  core/          Scanner, Registry, types, actions
  scanners/      Individual scanner implementations
  utils/         Platform helpers, hasher, walker, size formatting
  menu.py        TUI (questionary/rich)
  cli.py         CLI (click)
  gui.py         GUI (tkinter)
build/AppDir/    AppImage packaging
```

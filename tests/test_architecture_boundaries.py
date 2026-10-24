"""Enforces AD-1: the domain layer stays free of infrastructure/framework imports.

A future builder could otherwise import `sqlite3`, `python-telegram-bot`, or any
other infrastructure dependency directly into `domain/`, silently violating the
Architecture Spine's dependency-direction rule. This test walks the source of
every module under `domain/` and fails if it imports anything from
`infrastructure`, `interfaces`, or a known third-party runtime dependency.
"""

from __future__ import annotations

import ast
from pathlib import Path

DOMAIN_ROOT = Path(__file__).resolve().parents[1] / "src" / "cio_info_agent" / "domain"

FORBIDDEN_TOP_LEVEL_MODULES = {
    "sqlite3",
    "telegram",
    "apscheduler",
    "feedparser",
}
FORBIDDEN_INTERNAL_PACKAGES = {
    "cio_info_agent.infrastructure",
    "cio_info_agent.interfaces",
}


def _iter_domain_python_files() -> list[Path]:
    return sorted(DOMAIN_ROOT.rglob("*.py"))


def _imported_module_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _is_forbidden(module_name: str) -> bool:
    top_level = module_name.split(".")[0]
    if top_level in FORBIDDEN_TOP_LEVEL_MODULES:
        return True
    return any(
        module_name == forbidden or module_name.startswith(f"{forbidden}.")
        for forbidden in FORBIDDEN_INTERNAL_PACKAGES
    )


def test_domain_layer_has_no_infrastructure_or_interface_imports() -> None:
    violations: list[str] = []
    for path in _iter_domain_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for module_name in _imported_module_names(tree):
            if _is_forbidden(module_name):
                violations.append(f"{path.relative_to(DOMAIN_ROOT.parents[2])}: imports '{module_name}'")

    assert not violations, "Domain layer must stay free of infrastructure imports (AD-1):\n" + "\n".join(
        violations
    )


def test_domain_root_exists_and_is_scanned() -> None:
    # Guards against a silently empty glob (e.g. a renamed/misplaced domain
    # package) making the test above pass for the wrong reason.
    assert DOMAIN_ROOT.is_dir()
    assert _iter_domain_python_files(), "Expected at least the package __init__.py"

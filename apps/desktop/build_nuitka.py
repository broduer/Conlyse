from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SUPPORTED_UI_PLUGINS = ("pyside6",)
DEFAULT_UI_PLUGIN = SUPPORTED_UI_PLUGINS[0]
DEFAULT_OUTPUT_DIR = "build"

# Nuitka has first-class --noinclude-*-mode flags for setuptools, pytest,
# unittest, and pydoc (see NOINCLUDE_FLAGS below) — only list packages here
# that lack a dedicated flag.
NOFOLLOW_IMPORTS = (
    "doctest",
)

# Use Nuitka's dedicated exclusion modes instead of --nofollow-import-to for
# these well-known dev-only packages; they handle transitive aliases too.
NOINCLUDE_FLAGS = (
    "--noinclude-setuptools-mode=nofollow",
    "--noinclude-pytest-mode=nofollow",
    "--noinclude-unittest-mode=nofollow",
)


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    entrypoint = repo_root / "src" / "conlyse" / "__main__.py"

    if not entrypoint.exists():
        raise SystemExit(f"Entrypoint not found: {entrypoint}")

    assets_dir = repo_root / "assets"
    ui_plugin = str(os.environ.get("NUITKA_UI_PLUGIN") or DEFAULT_UI_PLUGIN).lower()
    output_dir_value = os.environ.get("NUITKA_OUTPUT_DIR") or (repo_root / DEFAULT_OUTPUT_DIR)
    output_dir = Path(output_dir_value).resolve()

    shader_dir = repo_root / "src" / "conlyse" / "pages" / "map_page" / "renderers"/ "shaders"
    if not shader_dir.exists():
        raise SystemExit(f"Shader directory not found: {shader_dir}")

    if ui_plugin not in SUPPORTED_UI_PLUGINS:
        raise SystemExit(
            f"Unsupported UI plugin '{ui_plugin}'. Supported plugins: "
            f"{', '.join(sorted(SUPPORTED_UI_PLUGINS))}."
        )

    jobs = os.environ.get("NUITKA_JOBS") or os.cpu_count() or 1

    platform_flags = ["--msvc=latest"] if sys.platform == "win32" else ["--clang"]
    if sys.platform == "win32":
        platform_flags.append("--windows-console-mode=disable")

    data_flags = []
    if assets_dir.exists():
        data_flags.append(f"--include-data-dir={assets_dir}=assets")
    if shader_dir.exists():
        data_flags.append(
            f"--include-data-dir={shader_dir}=conlyse/pages/map_page/renderers/shaders"
        )

    command = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        f"--enable-plugin={ui_plugin}",
        "--lto=no",
        "--python-flag=no_site",
        "--python-flag=no_docstrings",
        "--python-flag=no_warnings",
        f"--output-dir={output_dir}",
        "--assume-yes-for-downloads",
        f"--jobs={jobs}",
        *[f"--nofollow-import-to={m}" for m in NOFOLLOW_IMPORTS],
        *NOINCLUDE_FLAGS,
        *platform_flags,
        *data_flags,
        str(entrypoint),
    ]

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise SystemExit(
            "Failed to execute Nuitka. Ensure the Nuitka module is installed in this "
            "Python environment (for example via 'python -m pip install nuitka')."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Nuitka build failed with exit code {exc.returncode}.") from exc


if __name__ == "__main__":
    main()

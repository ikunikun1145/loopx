from pathlib import PurePosixPath, PureWindowsPath

import pytest

from loopx.canary.path_display import repository_relative_posix


@pytest.mark.parametrize(
    ("path", "root", "expected"),
    [
        (
            PurePosixPath("/checkout/examples/canary/check.py"),
            PurePosixPath("/checkout"),
            "examples/canary/check.py",
        ),
        (
            PureWindowsPath(r"C:\checkout\examples\canary\check.py"),
            PureWindowsPath(r"C:\checkout"),
            "examples/canary/check.py",
        ),
    ],
)
def test_repository_relative_paths_use_posix_spelling(path, root, expected):
    assert repository_relative_posix(path, root) == expected


def test_external_path_keeps_the_callers_fallback():
    path = PureWindowsPath(r"D:\outside\check.py")
    root = PureWindowsPath(r"C:\checkout")

    assert repository_relative_posix(path, root, fallback="original-argv") == "original-argv"


def test_canary_command_and_plan_renderers_are_host_independent(monkeypatch):
    from loopx.canary import planner, premerge, runner

    class WindowsPath(PureWindowsPath):
        def resolve(self):
            return self

    root = WindowsPath(r"C:\checkout")
    python = r"C:\Python\python.exe"

    monkeypatch.setattr(runner, "Path", WindowsPath)
    monkeypatch.setattr(runner, "REPO_ROOT", root)
    monkeypatch.setattr(runner.sys, "executable", python)
    normalized = runner.normalize_canary_command(
        "python3 examples/canary/check.py", repo_root=root
    )
    assert normalized["script"] == "examples/canary/check.py"
    assert normalized["display_argv"] == ["python3", "examples/canary/check.py"]

    monkeypatch.setattr(premerge, "Path", WindowsPath)
    monkeypatch.setattr(premerge.sys, "executable", python)
    assert premerge._display_argv(
        [python, r"C:\checkout\loopx\canary\runner.py"], repo_root=root
    ) == ["python3", "loopx/canary/runner.py"]

    monkeypatch.setattr(planner, "REPO_ROOT", root)
    assert planner._display_path(
        WindowsPath(r"C:\checkout\docs\concepts\catalog.md")
    ) == "docs/concepts/catalog.md"

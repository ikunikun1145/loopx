from __future__ import annotations

from pathlib import PurePath


def repository_relative_posix(
    path: PurePath,
    repository_root: PurePath,
    *,
    fallback: str | None = None,
) -> str:
    """Render repository-relative evidence paths with a host-independent spelling."""
    try:
        return path.relative_to(repository_root).as_posix()
    except ValueError:
        return str(path) if fallback is None else fallback

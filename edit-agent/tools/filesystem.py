"""
tools/filesystem.py

Filesystem tools available to the agent.
Each function corresponds to a tool defined in tools/schema.py.

All paths are relative to the project root.
Path traversal outside the project root is blocked for safety.
"""

import os


# The root directory the agent is allowed to work inside.
# Every path gets resolved and checked against this.
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _safe_path(path: str) -> str:
    """
    Resolve a relative path and verify it stays inside PROJECT_ROOT.

    This blocks path traversal attacks — for example an instruction like
    read_file("../../etc/passwd") would escape the project folder without this check.

    Args:
        path: A relative path provided by the model.

    Returns:
        The resolved absolute path if it is safe.

    Raises:
        PermissionError: If the path escapes PROJECT_ROOT.
    """
    resolved = os.path.abspath(os.path.join(PROJECT_ROOT, path))

    if not resolved.startswith(PROJECT_ROOT):
        raise PermissionError(
            f"Access denied: '{path}' resolves outside the project root."
        )

    return resolved


def read_file(path: str) -> str:
    """
    Read and return the contents of a file.

    Args:
        path: Relative path to the file.

    Returns:
        The file contents as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the path escapes the project root.
    """
    safe = _safe_path(path)

    if not os.path.isfile(safe):
        raise FileNotFoundError(f"File not found: '{path}'")

    with open(safe, "r", encoding="utf-8") as f:
        return f.read()


def list_dir(path: str = ".") -> str:
    """
    List the files and folders inside a directory.

    Args:
        path: Relative path to the directory. Defaults to project root.

    Returns:
        A formatted string listing all entries in the directory.

    Raises:
        FileNotFoundError: If the directory does not exist.
        PermissionError: If the path escapes the project root.
    """
    safe = _safe_path(path)

    if not os.path.isdir(safe):
        raise FileNotFoundError(f"Directory not found: '{path}'")

    entries = os.listdir(safe)

    if not entries:
        return f"Directory '{path}' is empty."

    # Separate folders and files, sort each alphabetically
    folders = sorted([e for e in entries if os.path.isdir(os.path.join(safe, e))])
    files = sorted([e for e in entries if os.path.isfile(os.path.join(safe, e))])

    lines = [f"Contents of '{path}':"]
    for folder in folders:
        lines.append(f"  [dir]  {folder}/")
    for file in files:
        lines.append(f"  [file] {file}")

    return "\n".join(lines)


def write_file(path: str, content: str) -> str:
    """
    Propose a file edit and write it only if the user approves.

    Shows a diff of the proposed changes and waits for explicit
    approval before writing anything to disk.

    Args:
        path:    Relative path to the file to write.
        content: The full content the agent wants to write.

    Returns:
        A message describing what happened (approved or rejected).

    Raises:
        PermissionError: If the path escapes the project root.
    """
    # _safe_path still runs first — safety check always happens
    # regardless of whether the edit gets approved
    safe = _safe_path(path)

    # Import here to avoid circular imports
    # (approval imports from filesystem, filesystem imports from approval)
    from agent.approval import request_approval_or_skip

    approved, message = request_approval_or_skip(path, content)

    if approved:
        # User said yes — now actually write the file
        os.makedirs(os.path.dirname(safe), exist_ok=True)
        with open(safe, "w", encoding="utf-8") as f:
            f.write(content)

    return message
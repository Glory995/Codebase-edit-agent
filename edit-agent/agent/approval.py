"""
agent/approval.py

Human-in-the-loop approval for file edits.

Before any file is modified, the proposed change is shown as a diff
and the user must explicitly approve it. This makes the agent safe
to run on real codebases — nothing is written without consent.
"""

from tools.diff import generate_diff, has_changes


def request_approval(path: str, original: str, proposed: str) -> bool:
    """
    Show the diff between original and proposed content and ask for approval.

    Args:
        path:     The file path being edited (shown in the prompt).
        original: The current content of the file.
        proposed: The new content the agent wants to write.

    Returns:
        True if the user approved the edit.
        False if the user rejected it.
    """

    # First check if there are actually any changes
    # No point asking for approval if nothing changed
    if not has_changes(original, proposed):
        print(f"  [approval] No changes detected in '{path}' — skipping.")
        return False

    # Show the diff so the user knows exactly what will change
    diff = generate_diff(original, proposed, path)

    print()
    print("=" * 55)
    print(f"  Proposed edit to: {path}")
    print("=" * 55)
    print(diff)
    print("=" * 55)

    # Ask for approval in a loop until we get a clear y or n
    # This keeps asking if the user types something unexpected
    while True:
        answer = input("  Apply this edit? (y/n): ").strip().lower()

        if answer == "y":
            print(f"  ✓ Edit approved — writing to '{path}'")
            return True

        if answer == "n":
            print(f"  ✗ Edit rejected — '{path}' unchanged.")
            return False

        # Anything else — ask again
        print("  Please type 'y' to approve or 'n' to reject.")


def request_approval_or_skip(path: str, proposed: str) -> tuple[bool, str]:
    """
    Read the current file content (if it exists), show the diff, and ask for approval.

    This is the version called by the agent loop — it handles the case
    where the file doesn't exist yet (a brand new file being created).

    Args:
        path:     The file path being written to.
        proposed: The content the agent wants to write.

    Returns:
        A tuple of (approved: bool, message: str)
        The message is fed back to the agent so it knows what happened.
    """
    import os
    from tools.filesystem import PROJECT_ROOT

    # Build the full path to check if the file already exists
    full_path = os.path.join(PROJECT_ROOT, path)

    if os.path.isfile(full_path):
        # File exists — read it and show a diff
        with open(full_path, "r", encoding="utf-8") as f:
            original = f.read()
    else:
        # Brand new file — original is empty, whole content is "added"
        original = ""
        print(f"\n  [new file] '{path}' does not exist yet and will be created.")

    approved = request_approval(path, original, proposed)

    if approved:
        return True, f"Edit approved and written to '{path}'."
    else:
        return False, f"Edit rejected by user. '{path}' was not modified."

"""Small file boundaries shared by setup and provider workers."""
import hashlib
import json
import os
from pathlib import Path


def atomic_settings(path: Path, data: dict) -> None:
    """Replace local preferences only after a complete, private write.

    Exclusive creation also acts as a fail-fast single-writer guard. Never
    remove a temporary file we did not create (another setup may own it).
    """
    temporary = path.with_name(path.name + '.tmp')
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ValueError('Temporary local settings exist; reconcile them before setup.') from None
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(data, output, indent=2)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def check_evidence_path(path: Path, feature: Path) -> None:
    """Apply the same sensitive-file policy to explicit context and tool reads."""
    if not path.resolve().is_relative_to(feature.resolve()) or not path.is_file():
        raise ValueError('Evidence must be a file inside the selected feature.')
    parts = path.relative_to(feature).parts
    private_directories = {'.git', '.aws', '.codex', '.claude', '.gemini', '.ssh'}
    private_names = {'auth.json', 'credentials', 'credentials.json',
                     'workspace.local.json', 'workspace.local.json.tmp'}
    if (any(part.lower() in private_directories or part.lower().startswith('.env') for part in parts)
            or path.suffix.lower() in {'.key', '.pem'} or path.name.lower() in private_names):
        raise ValueError('Evidence cannot access credential/configuration files.')


def read_utf8(path: Path, max_bytes: int) -> tuple[str, str]:
    """Bound allocation before decoding; hash exactly the bytes sent to a model."""
    with path.open('rb') as source:
        data = source.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError('Evidence context budget exceeded. Select fewer/smaller files.')
    return data.decode('utf-8'), hashlib.sha256(data).hexdigest()

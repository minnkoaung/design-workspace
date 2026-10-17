"""Native Codex authentication, catalog and explicit read-only execution."""
import json
import shutil
import subprocess
from .common import probe, worker, json_report


def binary():
    found = shutil.which('codex')
    if not found:
        raise ValueError('Codex CLI not found on PATH. Setup: https://developers.openai.com/codex/cli/ . Install separately, retry, or select Claude Code/OpenRouter.')
    return found


def authenticate(root, interactive=False):
    executable = binary()
    status = probe([executable, 'login', 'status'], root)
    if status.returncode:
        if not interactive or input('Codex is not signed in or status is unavailable. Launch native sign-in now? [y/N]: ').lower().strip() not in {'y', 'yes'}:
            raise ValueError('Codex authentication is unavailable. Retry native login or choose another provider.')
        route = input('Codex sign-in: 1. Browser  2. Device code  0. Cancel [default 1]: ').strip() or '1'
        if route not in {'1', '2'}:
            raise ValueError('Codex sign-in canceled; previous settings preserved.')
        try:
            result = subprocess.run([executable, 'login'] + (['--device-auth'] if route == '2' else []), cwd=root, timeout=300)
        except subprocess.TimeoutExpired:
            raise ValueError('Codex sign-in timed out; existing provider settings were preserved.') from None
        if result.returncode or probe([executable, 'login', 'status'], root).returncode:
            raise ValueError('Codex sign-in did not complete. Retry or choose another provider.')
    return {'authentication': 'native-cli-status-validated', 'live_test': 'not_run'}


def catalog(root, routing=None):
    import model_router
    return model_router.discover(root)


def preflight(root, routing):
    authenticate(root)
    return catalog(root, routing)


def run(root, routing, selection, prompt, images, folder, attempt, timeout):
    import model_router
    result_path = folder / f'attempt-{attempt}-result.json'
    argv = [binary(), 'exec', '--json', '--ephemeral', '--sandbox', 'read-only', '--skip-git-repo-check',
            '--cd', str(root), '--model', selection['model'], '--output-schema', str(folder / 'schema.json'),
            '--output-last-message', str(result_path)]
    if selection.get('effort'):
        argv += ['-c', 'model_reasoning_effort=' + json.dumps(selection['effort'])]
    for image in images:
        argv += ['--image', str(image)]
    argv += ['-']
    events = worker(argv, prompt, root, folder, attempt, timeout)
    usage, actual = None, None
    for line in events.read_text(encoding='utf-8').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get('type') == 'turn.completed':
            usage = event.get('usage')
        if isinstance(event.get('model'), str):
            actual = event['model']
    return {'response': json_report(json.loads(result_path.read_text(encoding='utf-8'))), 'usage': usage,
            'actual_model': actual, 'tool_reads': [], 'isolation': 'read-only filesystem; external tool access remains CLI-policy dependent'}

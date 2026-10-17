"""Claude Code adapter: native auth, explicit models and tools-disabled report workers."""
import json
import shutil
import subprocess
from .common import probe, worker, json_report


def binary():
    found = shutil.which('claude')
    if not found:
        raise ValueError('Claude Code not found on PATH. Setup: https://code.claude.com/docs/en/quickstart . Install separately, retry, or choose another provider.')
    return found


def capabilities(root):
    result = probe([binary(), '--help'], root)
    needed = ('--print', '--model', '--output-format', '--json-schema', '--tools', '--strict-mcp-config',
              '--mcp-config', '--settings', '--no-session-persistence', '--permission-mode')
    if result.returncode or any(flag not in result.stdout for flag in needed):
        raise ValueError('Installed Claude Code lacks verified required worker controls. Update it separately or choose another provider.')
    return result.stdout


def authenticate(root, interactive=False):
    executable = binary()
    result = probe([executable, 'auth', 'status', '--json'], root)
    if result.returncode:
        if not interactive:
            raise ValueError('Claude Code authentication is unavailable. Run provider setup or choose another provider.')
        print('Claude sign-in: 1. Claude subscription  2. Anthropic Console/API billing  0. Cancel')
        choice = input('Login route [1/2/0]: ').strip()
        if choice not in {'1', '2'}:
            raise ValueError('Claude sign-in canceled; previous settings preserved.')
        argv = [executable, 'auth', 'login'] + (['--console'] if choice == '2' else [])
        try:
            result = subprocess.run(argv, cwd=root, timeout=300)
        except subprocess.TimeoutExpired:
            raise ValueError('Claude sign-in timed out; previous settings preserved.') from None
        if result.returncode or probe([executable, 'auth', 'status', '--json'], root).returncode:
            raise ValueError('Claude sign-in did not complete. Retry or choose another provider.')
    capabilities(root)
    return {'authentication': 'native-cli-status-validated', 'live_test': 'not_run'}


def catalog(root, routing=None):
    if routing and routing.get('catalog'):
        return routing['catalog']
    raise ValueError('Claude account catalog discovery is not established. Use provider setup to enter your own model aliases/IDs.')


def preflight(root, routing):
    authenticate(root)
    return catalog(root, routing)


def run(root, routing, selection, prompt, images, folder, attempt, timeout):
    if images:
        raise ValueError('Claude image transport is not verified in this adapter; visual-review is unavailable for this provider.')
    help_text = capabilities(root)
    if selection.get('effort') and '--effort' not in help_text:
        raise ValueError('This Claude Code version has no verified effort flag. Reconfigure with provider default effort.')
    argv = [binary(), '--print', '--model', selection['model'], '--output-format', 'json',
            '--json-schema', (folder / 'schema.json').read_text(), '--no-session-persistence',
            '--tools', '', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--settings', '{"disableAllHooks":true}', '--permission-mode', 'plan']
    if selection.get('effort'):
        argv += ['--effort', selection['effort']]
    events = worker(argv, prompt, root, folder, attempt, timeout)
    value = json.loads(events.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Claude returned malformed worker output; no automatic retry.')
    if value.get('is_error') or value.get('subtype', 'success') != 'success':
        raise ValueError('Claude returned an unsuccessful result. Inspect local output; no automatic retry.')
    report = value.get('structured_output') or value.get('result')
    response = json_report(report)
    (folder / f'attempt-{attempt}-result.json').write_text(json.dumps(response), encoding='utf-8')
    models = value.get('modelUsage')
    return {'response': response, 'usage': value.get('usage'), 'model_usage': models,
            'actual_model': next(iter(models)) if isinstance(models, dict) and len(models) == 1 else None,
            'reported_cost': value.get('total_cost_usd'), 'tool_reads': [],
            'isolation': 'built-in tools disabled; empty strict MCP config; non-managed hooks disabled; managed organization hooks/policy may still apply'}

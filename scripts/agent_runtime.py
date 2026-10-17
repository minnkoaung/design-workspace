"""Provider-first setup and local per-provider routing. No automatic inference on import."""
import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import model_router as router
from providers import NAMES, get
from providers import credentials


def atomic_settings(root, data):
    from local_io import atomic_settings as write_settings
    write_settings(router.safe_path(root, 'workspace.local.json'), data)


def save_provider(root, routing):
    data = router.read_local(root)
    runtime = copy.deepcopy(data.get('agent_runtime', {'version': 2, 'providers': {}}))
    if not isinstance(runtime, dict) or runtime.get('version') != 2 or not isinstance(runtime.get('providers'), dict):
        raise ValueError('Unsupported runtime settings version; previous settings preserved.')
    legacy = data.get('model_routing')
    if isinstance(legacy, dict) and legacy.get('provider') == 'codex':
        runtime['providers'].setdefault('codex', copy.deepcopy(legacy))
    runtime['providers'][routing['provider']] = routing
    runtime['default_provider'] = routing['provider']
    data['agent_runtime'] = runtime
    # Legacy key remains byte-equivalent as JSON data; no destructive migration.
    atomic_settings(root, data)


def installed():
    return {'codex': bool(shutil.which('codex')), 'claude-code': bool(shutil.which('claude')),
            'openrouter': True}


def list_providers(root):
    available = installed()
    print('AI execution providers:')
    print('1. Codex CLI   — ' + ('installed; auth not checked' if available['codex'] else 'not installed'))
    print('2. Claude Code — ' + ('installed; auth not checked' if available['claude-code'] else 'not installed'))
    print('3. OpenRouter  — API setup available; credential/account readiness not checked')


def choose_models(catalog, provider):
    mode = input('Routing mode [economy/balanced/quality; default balanced]: ').strip().lower() or 'balanced'
    while mode not in router.ROUTES:
        mode = input('Choose economy, balanced or quality: ').strip().lower()
    tiers = {}
    if provider != 'claude-code':
        router.display_catalog(catalog)
    else:
        print('Claude catalog discovery is not verified. Enter your model aliases/IDs; access is checked on the first real task.')
    for tier in router.TIERS:
        while True:
            choice = input(f'{tier.title()} tier model (exact ID' + (' or number' if provider != 'claude-code' else '') + '): ').strip()
            model = next((m for m in catalog['models'] if m['model'] == choice), None)
            if provider == 'claude-code' and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/@+-]*', choice):
                model = {'model': choice, 'name': choice, 'efforts': [], 'default_effort': None, 'modalities': ['text'], 'default': False}
                if not any(m['model'] == choice for m in catalog['models']):
                    catalog['models'].append(model)
            if model is None and choice.isdigit() and 1 <= int(choice) <= len(catalog['models']):
                model = catalog['models'][int(choice) - 1]
            if model:
                break
            print('Choose a valid listed model or supported explicit ID.')
        effort = model.get('default_effort')
        if model.get('efforts'):
            default = effort if effort in model['efforts'] else model['efforts'][0]
            while True:
                effort = input(f"Effort [{'/'.join(model['efforts'])}; default {default}]: ").strip() or default
                if effort in model['efforts']:
                    break
                print('Choose a supported effort.')
        # Claude effort defaults to its native setting; no guessed per-model effort matrix.
        tiers[tier] = {'model': model['model'], 'effort': effort}
    retry = input('Allow at most one higher-tier escalation when explicitly requested? [y/N]: ').strip().lower()
    return {'version': 2, 'provider': provider, 'mode': mode, 'tiers': tiers,
            'max_attempts': 2 if retry in {'y', 'yes'} else 1, 'max_context_chars': 30000,
            'timeout_seconds': 600, 'catalog': catalog}


def setup(root, provider=None):
    if provider is None:
        list_providers(root)
        print('0. Exit')
        choice = input('Choose execution provider [1/2/3/0]: ').strip().lower()
        provider = {'1': 'codex', '2': 'claude-code', '3': 'openrouter'}.get(choice, choice)
        if provider in {'0', 'exit', 'q'}:
            return None
    adapter = get(provider)
    # Preserve any existing session key if a reconfiguration is canceled.
    previous_session = credentials._SESSION.get(str(root))
    try:
        if provider == 'openrouter':
            credential = credentials.choose(root)
            preliminary = {'provider': provider, 'credential': credential}
            verification = adapter.authenticate(root, preliminary)
            catalog = adapter.catalog(root, preliminary)
        else:
            verification = adapter.authenticate(root, interactive=True)
            catalog = adapter.catalog(root) if provider == 'codex' else {
                'source': 'explicit-user-models', 'discovered_at': router.now(), 'models': [],
                'access_note': 'Claude aliases/IDs are user configured; account/effort access is not inferred.'}
        routing = choose_models(catalog, provider)
        if provider == 'openrouter':
            routing['credential'] = credential
        routing['verification'] = {**verification, 'checked_at': router.now()}
        print('Optional live test consumes model allowance/credits. It sends only a small synthetic prompt.')
        if input('Run a live test now? [y/N]: ').strip().lower() in {'y', 'yes'}:
            with tempfile.TemporaryDirectory(prefix='provider-live-test-') as temporary:
                folder = Path(temporary)
                (folder / 'schema.json').write_text(json.dumps(router.SCHEMA))
                selection = router.select(routing, 'extract')
                result = adapter.run(root, routing, selection,
                                     'Return a report: status complete, report Connection test succeeded, reason synthetic connection test.',
                                     [], folder, 1, 60)
                if result['response']['status'] != 'complete':
                    raise ValueError('Live test requested escalation; configuration not saved.')
            routing['verification']['live_test'] = 'passed'
        save_provider(root, routing)
        print(f'Saved {provider} routing locally. No API key, provider login files or project approvals were copied.')
        return routing
    except BaseException:
        if previous_session is None:
            credentials.clear(root)
        else:
            credentials._SESSION[str(root)] = previous_session
        raise


def ensure_provider(root):
    """init cannot enter New/Resume without a configured execution provider."""
    try:
        routing = router.configuration(root)
    except ValueError:
        routing = None
    if routing:
        print(f"Saved execution provider: {routing['provider']}")
        try:
            catalog = get(routing['provider']).preflight(root, routing)
            for tier in router.TIERS:
                router.fresh_check(routing['tiers'][tier], catalog, [])
            print('Provider authentication checked; model configuration ready. Successful generation is not inferred.')
            return routing
        except (ValueError, OSError) as exc:
            print(f'Provider not ready: {exc}')
    while True:
        try:
            result = setup(root)
            if result is None:
                return None
            return result
        except (ValueError, OSError) as exc:
            print(f'Setup did not finish: {exc}\nChoose another provider, retry setup, or exit. Previous settings preserved.')


def models(root, action, provider=None):
    if action == 'setup':
        setup(root, provider)
        return 0
    routing = router.configuration(root, provider)
    if action == 'status':
        print(json.dumps(routing, indent=2))
        return 0
    adapter = get(routing['provider'])
    adapter.authenticate(root, routing) if routing['provider'] == 'openrouter' else adapter.authenticate(root)
    router.display_catalog(adapter.catalog(root, routing))
    return 0

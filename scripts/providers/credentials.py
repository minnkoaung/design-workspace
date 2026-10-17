"""Environment or process-memory credentials only. Never serialize a secret."""
import getpass
import os
import sys
import warnings

_SESSION = {}


def hidden_key():
    if not sys.stdin.isatty():
        raise ValueError('Hidden key input requires a terminal. Supply OPENROUTER_API_KEY through your environment instead.')
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        try:
            value = getpass.getpass('OpenRouter API key (hidden; session only): ').strip()
        except getpass.GetPassWarning:
            raise ValueError('Secure terminal input is unavailable. Use OPENROUTER_API_KEY; visible input is refused.') from None
    if not value or not value.isascii() or any(c.isspace() for c in value):
        raise ValueError('API key must be nonempty and contain no whitespace.')
    return value


def choose(root):
    print('Use your own OpenRouter API key: https://openrouter.ai/keys . No account password is requested.')
    print('OpenRouter credentials: 1. OPENROUTER_API_KEY environment variable  2. Hidden session-only input  0. Cancel')
    print('Environment key: ' + ('present' if os.environ.get('OPENROUTER_API_KEY') else 'not present'))
    print('Secure persistent key storage is not implemented; keys are never written to settings.')
    choice = input('Credential source [1/2/0]: ').strip()
    if choice == '1':
        if not os.environ.get('OPENROUTER_API_KEY'):
            raise ValueError('OPENROUTER_API_KEY is missing. Set it in your environment or choose hidden terminal input.')
        return {'source': 'environment', 'name': 'OPENROUTER_API_KEY'}
    if choice == '2':
        _SESSION[str(root)] = hidden_key()
        return {'source': 'session'}
    raise ValueError('Credential setup canceled; previous settings preserved.')


def resolve(root, routing, interactive=False):
    reference = routing.get('credential', {})
    if reference == {'source': 'environment', 'name': 'OPENROUTER_API_KEY'}:
        value = os.environ.get('OPENROUTER_API_KEY')
    elif reference == {'source': 'session'}:
        value = _SESSION.get(str(root))
        if not value and interactive:
            value = hidden_key()
            _SESSION[str(root)] = value
    else:
        raise ValueError('Unsupported credential reference. Run OpenRouter provider setup again.')
    if not value:
        raise ValueError('OpenRouter credential unavailable in this process. Use OPENROUTER_API_KEY or repeat session-key setup.')
    if not value.isascii() or any(c.isspace() for c in value):
        raise ValueError('OpenRouter credential contains invalid whitespace.')
    return value


def clear(root):
    _SESSION.pop(str(root), None)


def redact(value, key):
    if isinstance(value, str):
        return value.replace(key, '[REDACTED]')
    if isinstance(value, dict):
        return {str(k).replace(key, '[REDACTED]'): redact(v, key) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, key) for v in value]
    return value

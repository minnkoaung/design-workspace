"""Execution adapters. Importing this package never authenticates or starts inference."""
NAMES = ('codex', 'claude-code', 'openrouter')


def get(provider):
    if provider == 'codex':
        from . import codex
        return codex
    if provider == 'claude-code':
        from . import claude_code
        return claude_code
    if provider == 'openrouter':
        from . import openrouter
        return openrouter
    raise ValueError('Choose codex, claude-code or openrouter.')

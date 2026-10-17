"""Three-provider contract tests. All accounts, keys and responses are synthetic."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import agent_runtime as runtime
import model_router as router
import workspace
from providers import claude_code, codex, credentials, openrouter
from providers.common import worker, json_report
from local_io import atomic_settings
from provider_fixtures import CATALOG

REPORT = {'status': 'complete', 'report': 'Synthetic provider report.', 'reason': 'Fixture evidence.'}
SECRET = 'fixture-key-never-persist-123'
MODEL = {'id': 'fixture/model', 'name': 'Fixture model', 'architecture': {'input_modalities': ['text', 'image']},
         'supported_parameters': ['tools', 'response_format']}


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='provider-contract-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run = self.root / 'features/alpha'
        self.run.mkdir(parents=True)
        (self.run / 'status.md').write_text('Stage0; unapproved.\n')
        (self.run / 'decisions.md').write_text('No approvals.\n')
        (self.run / 'evidence.md').write_text('Approved source text fixture.\n')
        self.settings = {'version': 2, 'provider': 'claude-code', 'mode': 'balanced',
                         'tiers': {tier: {'model': 'fixture-model', 'effort': None} for tier in router.TIERS},
                         'max_attempts': 1, 'max_context_chars': 30000, 'timeout_seconds': 10,
                         'catalog': {'models': [{'model': 'fixture-model', 'efforts': [], 'modalities': ['text']}], 'source': 'fixture', 'access_note': 'fixture'}}
        self.addCleanup(credentials.clear, self.root)

    def folder(self):
        folder = self.run / 'history/agent-runs/fixture'
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'schema.json').write_text(json.dumps(router.SCHEMA))
        return folder

    def openrouter_settings(self):
        catalog = {'models': [{'model': MODEL['id'], 'efforts': [], 'modalities': ['text', 'image'],
                              'parameters': MODEL['supported_parameters']}], 'source': 'fixture', 'access_note': 'fixture'}
        return {**self.settings, 'provider': 'openrouter', 'credential': {'source': 'environment', 'name': 'OPENROUTER_API_KEY'},
                'catalog': catalog, '_feature_path': str(self.run),
                'tiers': {tier: {'model': MODEL['id'], 'effort': None} for tier in router.TIERS}}

    def test_settings_write_is_private_and_preserves_another_writer(self):
        path = self.root / 'workspace.local.json'
        atomic_settings(path, {'complete': True})
        if os.name != 'nt':
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        temporary = path.with_name(path.name + '.tmp')
        temporary.write_text('another writer')
        with self.assertRaisesRegex(ValueError, 'Temporary local settings'):
            atomic_settings(path, {'complete': False})
        self.assertEqual(temporary.read_text(), 'another writer')
        self.assertEqual(json.loads(path.read_text()), {'complete': True})

    def test_malformed_routing_is_rejected_as_configuration_error(self):
        for field, value in [('tiers', []), ('tiers', {'light': None}),
                             ('mode', []), ('provider', []), ('version', []),
                             ('max_attempts', True), ('timeout_seconds', False)]:
            with self.subTest(field=field, value=value):
                settings = {**self.settings, field: value}
                (self.root / 'workspace.local.json').write_text(json.dumps({'model_routing': settings}))
                with self.assertRaises(ValueError):
                    router.configuration(self.root)

    def test_explicit_context_and_tool_reads_share_sensitive_file_policy(self):
        for name in ['.env.production', 'private.KEY', '.ssh/id_rsa', 'auth.json']:
            path = self.run / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic private material')
            relative = path.relative_to(self.root).as_posix()
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, 'credential/configuration'):
                    router.build_prompt(self.root, self.run, 'extract', [relative], 30000)
                with self.assertRaisesRegex(ValueError, 'credential/configuration'):
                    openrouter.read_tool(self.root, self.run, {'path': relative}, 30000)

    def test_report_schema_rejects_extra_fields_and_wrong_status_types(self):
        for value in [{**REPORT, 'unexpected': True}, {**REPORT, 'status': []}]:
            with self.assertRaisesRegex(ValueError, 'report-schema'):
                json_report(value)

    def test_tool_response_rejects_malformed_calls_without_attribute_errors(self):
        for calls in ['invalid', [None], [{'function': None}],
                      [{'id': 'x', 'function': {'name': 'read_feature_file', 'arguments': {}}}]]:
            response = {'choices': [{'message': {'tool_calls': calls}}]}
            with self.subTest(calls=calls), patch.dict(os.environ, {'OPENROUTER_API_KEY': SECRET}), patch.object(openrouter, 'api', return_value=response):
                with self.assertRaises(ValueError):
                    openrouter.run(self.root, self.openrouter_settings(), {'model': MODEL['id']},
                                   'prompt', [], self.folder(), 1, 10)

    def test_profile_migration_switch_and_explicit_override_preserve_legacy(self):
        legacy = {**self.settings, 'version': 1, 'provider': 'codex'}
        (self.root / 'workspace.local.json').write_text(json.dumps({'model_routing': legacy, 'unrelated': 'keep'}))
        runtime.save_provider(self.root, self.settings)
        self.assertEqual(router.configuration(self.root)['provider'], 'claude-code')
        self.assertEqual(router.configuration(self.root, 'codex'), legacy)
        data = router.read_local(self.root)
        self.assertEqual(data['model_routing'], legacy)
        self.assertEqual(data['unrelated'], 'keep')
        self.assertFalse((self.root / 'workspace.local.json.tmp').exists())

    def test_canceled_setup_keeps_settings_and_session_key(self):
        runtime.save_provider(self.root, self.settings)
        before = (self.root / 'workspace.local.json').read_bytes()
        credentials._SESSION[str(self.root)] = 'previous-fixture-key'
        with patch('builtins.input', side_effect=['2']), patch.object(credentials, 'hidden_key', return_value=SECRET), patch.object(openrouter, 'api', side_effect=ValueError('network unavailable')):
            with self.assertRaisesRegex(ValueError, 'network unavailable'):
                runtime.setup(self.root, 'openrouter')
        self.assertEqual((self.root / 'workspace.local.json').read_bytes(), before)
        self.assertEqual(credentials._SESSION[str(self.root)], 'previous-fixture-key')

    def test_openrouter_only_setup_hidden_key_no_secret_saved_or_displayed(self):
        output = io.StringIO()
        answers = ['2', '', '1', '1', '1', 'n', 'n']
        def response(key, endpoint, *args, **kwargs):
            self.assertEqual(key, SECRET)
            return {'data': {}} if endpoint == '/key' else {'data': [MODEL]}
        with patch('shutil.which', return_value=None), patch('builtins.input', side_effect=answers), patch.object(credentials, 'hidden_key', return_value=SECRET), patch.object(openrouter, 'api', side_effect=response), contextlib.redirect_stdout(output):
            value = runtime.setup(self.root, 'openrouter')
        self.assertEqual(value['provider'], 'openrouter')
        self.assertEqual(value['verification']['live_test'], 'not_run')
        self.assertNotIn(SECRET, (self.root / 'workspace.local.json').read_text())
        self.assertNotIn(SECRET, output.getvalue())
        self.assertEqual(credentials.resolve(self.root, value), SECRET)
        credentials.clear(self.root)
        with self.assertRaisesRegex(ValueError, 'unavailable in this process'):
            credentials.resolve(self.root, value)

    def test_no_tty_never_falls_back_to_visible_key_input(self):
        with patch('sys.stdin.isatty', return_value=False), patch('getpass.getpass', side_effect=AssertionError('must not echo')):
            with self.assertRaisesRegex(ValueError, 'requires a terminal'):
                credentials.hidden_key()

    def test_api_error_categories_never_echo_key_or_response(self):
        for status, message in [(401, 'invalid or revoked'), (402, 'insufficient credits'), (403, 'restricted'), (429, 'rate limited'), (500, 'service error'), (302, 'redirect refused')]:
            error = urllib.error.HTTPError(openrouter.BASE_URL, status, SECRET, {}, io.BytesIO(SECRET.encode()))
            with self.subTest(status=status), patch('urllib.request.build_opener') as builder:
                builder.return_value.open.side_effect = error
                with self.assertRaisesRegex(ValueError, message) as caught:
                    openrouter.api(SECRET, '/key')
                self.assertNotIn(SECRET, str(caught.exception))
        with patch('urllib.request.build_opener') as builder:
            builder.return_value.open.side_effect = urllib.error.URLError(SECRET)
            with self.assertRaisesRegex(ValueError, 'status is unknown') as caught:
                openrouter.api(SECRET, '/key')
            self.assertNotIn(SECRET, str(caught.exception))

    def test_api_fixed_host_no_redirect_and_header_only_key(self):
        with patch('urllib.request.build_opener') as builder:
            builder.return_value.open.return_value = io.BytesIO(json.dumps({'data': {}, 'unexpected_echo': SECRET}).encode())
            result = openrouter.api(SECRET, '/key')
            request = builder.return_value.open.call_args.args[0]
            self.assertNotIn(SECRET, request.full_url)
            self.assertEqual(request.get_header('Authorization'), 'Bearer ' + SECRET)
            self.assertEqual(result['unexpected_echo'], '[REDACTED]')
        self.assertIsNone(openrouter.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example'))
        with self.assertRaisesRegex(ValueError, 'Unapproved'):
            openrouter.api(SECRET, 'https://other.example')

    def test_openrouter_execution_without_either_cli_preserves_feature(self):
        settings = self.openrouter_settings()
        runtime.save_provider(self.root, settings)
        before = (self.run / 'status.md').read_bytes()
        def response(key, endpoint, payload=None, timeout=20):
            if endpoint == '/key': return {'data': {}}
            if endpoint == '/models': return {'data': [MODEL]}
            self.assertEqual(payload['model'], MODEL['id'])
            return {'model': MODEL['id'], 'choices': [{'message': {'content': json.dumps(REPORT)}}],
                    'usage': {'prompt_tokens': 100, 'completion_tokens': 20}}
        with patch('shutil.which', return_value=None), patch.dict(os.environ, {'OPENROUTER_API_KEY': SECRET}), patch.object(openrouter, 'api', side_effect=response):
            self.assertEqual(router.execute(self.root, self.run, 'extract', [], [], dry_run=False), 0)
        self.assertEqual(before, (self.run / 'status.md').read_bytes())
        records = list((self.run / 'history/agent-runs').glob('*/run.json'))
        record = json.loads(records[0].read_text())
        self.assertEqual(record['provider'], 'openrouter')
        self.assertEqual(record['attempts'][0]['usage'][0]['prompt_tokens'], 100)
        for path in records[0].parent.iterdir():
            self.assertNotIn(SECRET, path.read_text())

    def test_openrouter_tool_loop_reads_only_feature_and_enforces_limit(self):
        folder = self.folder()
        call = {'id': 'read1', 'type': 'function', 'function': {'name': 'read_feature_file', 'arguments': json.dumps({'path': 'features/alpha/evidence.md'})}}
        responses = [{'model': MODEL['id'], 'choices': [{'message': {'tool_calls': [call], 'content': None}}]},
                     {'model': MODEL['id'], 'choices': [{'message': {'content': json.dumps(REPORT)}}]}]
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': SECRET}), patch.object(openrouter, 'api', side_effect=responses):
            result = openrouter.run(self.root, self.openrouter_settings(), {'model': MODEL['id']}, 'source prompt', [], folder, 1, 10)
        self.assertEqual(result['tool_reads'][0]['path'], 'features/alpha/evidence.md')
        with self.assertRaisesRegex(ValueError, 'inside the selected feature'):
            (self.root / 'outside.md').write_text('not authorized')
            openrouter.read_tool(self.root, self.run, {'path': 'outside.md'}, 1000)
        with self.assertRaisesRegex(ValueError, 'budget exceeded'):
            openrouter.read_tool(self.root, self.run, {'path': 'features/alpha/evidence.md'}, 2)
        (self.run / '.env.production').write_text('fixture-only secret configuration')
        with self.assertRaisesRegex(ValueError, 'credential/configuration'):
            openrouter.read_tool(self.root, self.run, {'path': 'features/alpha/.env.production'}, 1000)
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': SECRET}), patch.object(openrouter, 'api', return_value=responses[0]):
            with self.assertRaisesRegex(ValueError, 'limit exceeded'):
                openrouter.run(self.root, self.openrouter_settings(), {'model': MODEL['id']}, 'source prompt', [], folder, 2, 10)

    def test_claude_native_login_route_is_explicit_and_no_codex_needed(self):
        results = [subprocess.CompletedProcess([], 1, '', ''), subprocess.CompletedProcess([], 0, '{}', ''), subprocess.CompletedProcess([], 0, ' '.join(['--print','--model','--output-format','--json-schema','--tools','--strict-mcp-config','--mcp-config','--settings','--no-session-persistence','--permission-mode']), '')]
        with patch('shutil.which', side_effect=lambda name: '/fixture/claude' if name == 'claude' else None), patch.object(claude_code, 'probe', side_effect=results), patch('builtins.input', return_value='2'), patch.object(claude_code.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as login:
            claude_code.authenticate(self.root, interactive=True)
            self.assertEqual(login.call_args.args[0], ['/fixture/claude', 'auth', 'login', '--console'])

    def test_codex_device_login_is_explicit_native_handoff(self):
        statuses = [subprocess.CompletedProcess([], 1), subprocess.CompletedProcess([], 0)]
        with patch.object(codex, 'binary', return_value='/fixture/codex'), patch.object(codex, 'probe', side_effect=statuses), patch('builtins.input', side_effect=['y', '2']), patch.object(codex.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as login:
            codex.authenticate(self.root, interactive=True)
            self.assertEqual(login.call_args.args[0], ['/fixture/codex', 'login', '--device-auth'])

    def test_claude_worker_controls_usage_and_malformed_result(self):
        folder = self.folder()
        event = {'subtype': 'success', 'is_error': False, 'structured_output': REPORT, 'usage': {'input_tokens': 80},
                 'modelUsage': {'fixture-resolved-model': {'inputTokens': 80}}}
        events = folder / 'fixture-events.json'
        events.write_text(json.dumps(event))
        with patch.object(claude_code, 'binary', return_value='/fixture/claude'), patch.object(claude_code, 'capabilities', return_value='--effort'), patch.object(claude_code, 'worker', return_value=events) as worker:
            value = claude_code.run(self.root, self.settings, {'model': 'fixture-model'}, 'prompt', [], folder, 1, 10)
            argv = worker.call_args.args[0]
            self.assertEqual(argv[argv.index('--tools') + 1], '')
            self.assertIn('--strict-mcp-config', argv)
            self.assertEqual(value['actual_model'], 'fixture-resolved-model')
            self.assertEqual(value['usage']['input_tokens'], 80)
            events.write_text(json.dumps({'is_error': True}))
            with self.assertRaisesRegex(ValueError, 'unsuccessful'):
                claude_code.run(self.root, self.settings, {'model': 'fixture-model'}, 'prompt', [], folder, 2, 10)
        with self.assertRaisesRegex(ValueError, 'image transport'):
            claude_code.run(self.root, self.settings, {'model': 'fixture-model'}, 'prompt', ['image'], folder, 1, 10)

    def test_provider_first_menu_exits_without_creating_project(self):
        output = io.StringIO()
        with patch('shutil.which', return_value=None), patch('builtins.input', side_effect=['0']), contextlib.redirect_stdout(output):
            workspace.command_init(self.root)
        self.assertIn('1. Codex CLI', output.getvalue())
        self.assertIn('2. Claude Code', output.getvalue())
        self.assertIn('3. OpenRouter', output.getvalue())
        self.assertNotIn('Manual workflow', output.getvalue())
        self.assertNotIn('1. New project / feature', output.getvalue())
        self.assertFalse((self.root / 'workspace.local.json').exists())

    def test_openrouter_only_init_setup_then_resume_has_no_manual_path(self):
        output = io.StringIO()
        answers = ['3', '1', '', '1', '1', '1', 'n', 'n', '2', '1']
        endpoints = []
        def response(key, endpoint, *args, **kwargs):
            endpoints.append(endpoint)
            return {'data': {}} if endpoint == '/key' else {'data': [MODEL]}
        before = (self.run / 'status.md').read_bytes()
        with patch('shutil.which', return_value=None), patch.dict(os.environ, {'OPENROUTER_API_KEY': SECRET}), patch('builtins.input', side_effect=answers), patch.object(openrouter, 'api', side_effect=response), contextlib.redirect_stdout(output):
            self.assertEqual(workspace.command_init(self.root), 0)
        text = output.getvalue()
        self.assertLess(text.index('Choose execution provider') if 'Choose execution provider' in text else text.index('AI execution providers'), text.index('1. New project / feature'))
        self.assertIn('Resume feature alpha', text)
        self.assertEqual(endpoints, ['/key', '/models'])
        self.assertNotIn(SECRET, text)
        self.assertNotIn('Manual workflow', text)
        self.assertEqual(before, (self.run / 'status.md').read_bytes())

    def test_readonly_plan_does_not_authenticate_or_consume_model(self):
        runtime.save_provider(self.root, self.settings)
        with patch.object(claude_code, 'preflight', side_effect=AssertionError('must not authenticate')), contextlib.redirect_stdout(io.StringIO()):
            router.execute(self.root, self.run, 'requirements', [], [], dry_run=True)
        self.assertFalse((self.run / 'history').exists())

    @unittest.skipIf(sys.platform == 'win32', 'POSIX process cleanup assertion')
    def test_worker_timeout_reaps_process_and_preserves_partial_output(self):
        folder = self.folder()
        program = 'import os,time; print(os.getpid(), flush=True); time.sleep(10)'
        with self.assertRaises(subprocess.TimeoutExpired):
            worker([sys.executable, '-c', program], '', self.root, folder, 1, 0.2)
        pid = int((folder / 'attempt-1-events.jsonl').read_text().strip())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    @unittest.skipIf(sys.platform == 'win32', 'POSIX fake CLI; Windows process behavior requires separate verification')
    def test_claude_only_real_subprocess_setup_and_report(self):
        binary = self.root / 'fixture-bin/claude'
        binary.parent.mkdir()
        binary.write_text('''#!/usr/bin/env python3
import json,sys
args=sys.argv
if '--help' in args:
 print('--print --model --output-format --json-schema --tools --strict-mcp-config --mcp-config --settings --no-session-persistence --permission-mode --effort')
elif 'auth' in args:
 print('{"loggedIn":true}')
elif '--print' in args:
 assert args[args.index('--tools')+1] == ''
 assert '--strict-mcp-config' in args
 assert 'source_evidence' in sys.stdin.read()
 print(json.dumps({'subtype':'success','is_error':False,'structured_output':{'status':'complete','report':'Claude fixture completed.','reason':'fixture'},'usage':{'input_tokens':51},'modelUsage':{'fixture-actual':{}}}))
else:
 sys.exit(8)
''')
        binary.chmod(0o755)
        answers = ['', 'fixture-light', 'fixture-standard', 'fixture-strong', 'n', 'n']
        with patch('shutil.which', side_effect=lambda name: str(binary) if name == 'claude' else None), patch('builtins.input', side_effect=answers):
            runtime.setup(self.root, 'claude-code')
        with patch('shutil.which', side_effect=lambda name: str(binary) if name == 'claude' else None):
            self.assertEqual(router.execute(self.root, self.run, 'extract', ['features/alpha/evidence.md'], [], dry_run=False), 0)
        record = json.loads(next((self.run / 'history/agent-runs').glob('*/run.json')).read_text())
        self.assertEqual(record['provider'], 'claude-code')
        self.assertEqual(record['attempts'][0]['actual_model'], 'fixture-actual')
        self.assertEqual(record['attempts'][0]['usage']['input_tokens'], 51)

    def test_openrouter_images_are_attached_as_actual_image_data(self):
        folder = self.folder()
        image = self.run / 'screen.png'
        image.write_bytes(b'fixture-image-bytes')
        result = {'choices': [{'message': {'content': json.dumps(REPORT)}}]}
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': SECRET}), patch.object(openrouter, 'api', return_value=result) as api:
            openrouter.run(self.root, self.openrouter_settings(), {'model': MODEL['id']}, 'source', [image], folder, 1, 10)
        content = api.call_args.args[2]['messages'][1]['content']
        self.assertEqual(content[1]['type'], 'image_url')
        self.assertTrue(content[1]['image_url']['url'].startswith('data:image/png;base64,'))

    def test_claude_malformed_auth_and_capabilities_fail_without_login(self):
        with patch.object(claude_code, 'binary', return_value='/fixture/claude'), patch.object(claude_code, 'probe', return_value=subprocess.CompletedProcess([], 1, '', '')):
            with self.assertRaisesRegex(ValueError, 'authentication'):
                claude_code.authenticate(self.root, interactive=False)
        with patch.object(claude_code, 'binary', return_value='/fixture/claude'), patch.object(claude_code, 'probe', return_value=subprocess.CompletedProcess([], 0, '--print', '')):
            with self.assertRaisesRegex(ValueError, 'required worker controls'):
                claude_code.capabilities(self.root)


if __name__ == '__main__':
    unittest.main()

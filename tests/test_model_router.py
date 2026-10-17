import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import contextlib
import io
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import model_router as router
import workspace

from provider_fixtures import CATALOG, FAKE

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='routing-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run = self.root / 'features/alpha'
        self.run.mkdir(parents=True)
        (self.run / 'status.md').write_text('Stage 0; no approvals.\n')
        (self.run / 'decisions.md').write_text('No approvals.\n')
        (self.run / 'brief.md').write_text('Build a customer portal.\n')
        (self.root / 'workspace.local.json').write_text(json.dumps({'other_preference': 'preserved'}))
        self.settings = {'version': 1, 'provider': 'codex', 'mode': 'balanced',
                         'tiers': {tier: {'model': model['model'], 'effort': model['default_effort']} for tier, model in zip(router.TIERS, CATALOG['models'])},
                         'max_attempts': 1, 'max_context_chars': 30000, 'timeout_seconds': 30, 'catalog': CATALOG}
        router.save_local(self.root, self.settings)

    def test_routing_modes_and_settings_are_local(self):
        routing = router.configuration(self.root)
        self.assertEqual(router.select(routing, 'extract')['model'], 'fixture-light')
        self.assertEqual(router.select(routing, 'requirements')['model'], 'fixture-standard')
        self.assertEqual(router.select(routing, 'review')['model'], 'fixture-strong')
        routing['mode'] = 'economy'
        self.assertEqual(router.select(routing, 'requirements')['model'], 'fixture-light')
        routing['mode'] = 'quality'
        self.assertEqual(router.select(routing, 'requirements')['model'], 'fixture-strong')
        self.assertEqual(router.read_local(self.root)['other_preference'], 'preserved')
        self.assertFalse((self.root / 'workspace.local.json.tmp').exists())

    def test_missing_provider_blocks_init_until_setup_or_exit(self):
        output = io.StringIO()
        with patch('shutil.which', return_value=None), patch('builtins.input', side_effect=['0']), contextlib.redirect_stdout(output):
            self.assertEqual(workspace.command_init(self.root), 0)
        text = output.getvalue()
        self.assertIn('OpenRouter', text)
        self.assertNotIn('1. New project / feature', text)
        self.assertNotIn('Manual workflow', text)

    def test_missing_codex_model_commands_and_run_fail_before_spawning(self):
        with patch('shutil.which', return_value=None), patch.object(router.subprocess, 'Popen', side_effect=AssertionError('must not spawn')):
            with self.assertRaisesRegex(ValueError, 'Codex CLI'):
                router.discover(self.root)
            with self.assertRaisesRegex(ValueError, 'Codex CLI'):
                router.execute(self.root, self.run, 'extract', [], [], dry_run=False)
        self.assertFalse((self.run / 'history').exists())

    def test_doctor_without_codex_still_passes_local_prerequisites(self):
        root = Path(__file__).resolve().parents[1]
        output = io.StringIO()
        with patch('shutil.which', return_value=None), contextlib.redirect_stdout(output):
            self.assertEqual(workspace.command_doctor(root), 0)
        self.assertIn('init requires one configured execution provider', output.getvalue())

    def test_setup_saves_user_mapping_not_catalog_order(self):
        answers = ['balanced', '3', 'high', '1', 'medium', '2', 'medium', 'yes']
        with patch.object(router, 'discover', return_value=CATALOG), patch('builtins.input', side_effect=answers):
            router.setup(self.root)
        saved = router.configuration(self.root)
        self.assertEqual(saved['tiers']['light']['model'], 'fixture-strong')
        self.assertEqual(saved['tiers']['standard']['model'], 'fixture-light')
        self.assertEqual(saved['max_attempts'], 2)

    def test_missing_config_and_capability_drift_fail_explicitly(self):
        (self.root / 'workspace.local.json').unlink()
        with self.assertRaisesRegex(ValueError, 'not configured'):
            router.configuration(self.root)
        with self.assertRaisesRegex(ValueError, 'image'):
            router.fresh_check(self.settings['tiers']['light'], CATALOG, ['image.png'])
        with self.assertRaisesRegex(ValueError, 'no longer'):
            router.fresh_check({'model': 'retired', 'effort': None}, CATALOG, [])
        with self.assertRaisesRegex(ValueError, 'reasoning effort'):
            router.fresh_check({'model': 'fixture-light', 'effort': 'unsupported'}, CATALOG, [])

    def test_context_is_bounded_and_cannot_escape_feature(self):
        with self.assertRaisesRegex(ValueError, 'inside the selected feature'):
            router.build_prompt(self.root, self.run, 'extract', ['workspace.local.json'], 30000)
        with self.assertRaisesRegex(ValueError, 'inside this checkout'):
            router.build_prompt(self.root, self.run, 'extract', ['../escape.md'], 30000)
        with self.assertRaisesRegex(ValueError, 'character limit'):
            router.build_prompt(self.root, self.run, 'extract', ['features/alpha/brief.md'], 10)
        with patch.object(router, 'discover', side_effect=AssertionError('plan must not discover or infer')):
            router.execute(self.root, self.run, 'extract', ['features/alpha/brief.md'], [], dry_run=True)
        self.assertFalse((self.run / 'history').exists())
        with self.assertRaisesRegex(ValueError, 'at least one'):
            router.execute(self.root, self.run, 'visual-review', [], [], dry_run=True)

    @unittest.skipIf(sys.platform == 'win32', 'POSIX fixture executable; pure routing tests are portable')
    def test_real_stdio_pagination_and_worker_usage(self):
        self.fake_worker('success')
        with patch.dict(os.environ, self.environment):
            catalog = router.discover(self.root)
            self.assertEqual([m['model'] for m in catalog['models']], [m['model'] for m in CATALOG['models']])
            before = (self.run / 'status.md').read_bytes()
            self.assertEqual(router.execute(self.root, self.run, 'extract', ['features/alpha/brief.md'], [], dry_run=False), 0)
            record = self.records()[0]
            self.assertEqual(record['attempts'][0]['usage']['input_tokens'], 100)
            self.assertIsNone(record['cost'])
            self.assertIsNone(record['attempts'][0]['actual_model'])
            self.assertEqual(record['status'], 'complete-report')
            self.assertEqual(before, (self.run / 'status.md').read_bytes())

    def fake_worker(self, behavior):
        binary = self.root / 'bin/codex'
        binary.parent.mkdir(exist_ok=True)
        binary.write_text(FAKE)
        binary.chmod(0o755)
        raw = [{'model': m['model'], 'supportedReasoningEfforts': [{'reasoningEffort': e} for e in m['efforts']],
                'defaultReasoningEffort': m['default_effort'], 'inputModalities': m['modalities']} for m in CATALOG['models']]
        self.environment = {'PATH': str(binary.parent) + os.pathsep + os.environ.get('PATH', ''),
                            'FIXTURE_MODELS': json.dumps(raw), 'FIXTURE_BEHAVIOR': behavior}

    def records(self):
        return [json.loads(p.read_text()) for p in (self.run / 'history/agent-runs').glob('*/run.json')]

    @unittest.skipIf(sys.platform == 'win32', 'POSIX fixture executable')
    def test_escalation_is_opt_in_and_bounded(self):
        self.fake_worker('escalate')
        with patch.dict(os.environ, self.environment):
            self.assertEqual(router.execute(self.root, self.run, 'extract', [], [], dry_run=False), 2)
            self.settings['max_attempts'] = 2
            router.save_local(self.root, self.settings)
            self.assertEqual(router.execute(self.root, self.run, 'extract', [], [], dry_run=False), 0)
        attempts = sorted(len(r['attempts']) for r in self.records())
        self.assertEqual(attempts, [1, 2])

    @unittest.skipIf(sys.platform == 'win32', 'POSIX fixture executable')
    def test_transport_and_invalid_output_do_not_retry(self):
        self.fake_worker('failure')
        self.settings['max_attempts'] = 2
        router.save_local(self.root, self.settings)
        with patch.dict(os.environ, self.environment):
            with self.assertRaisesRegex(ValueError, 'worker failed'):
                router.execute(self.root, self.run, 'extract', [], [], dry_run=False)
        self.environment['FIXTURE_BEHAVIOR'] = 'invalid'
        with patch.dict(os.environ, self.environment):
            with self.assertRaises(ValueError):
                router.execute(self.root, self.run, 'extract', [], [], dry_run=False)
        self.assertEqual([len(r['attempts']) for r in self.records()], [1, 1])
        self.assertTrue(all(r['status'] == 'failed' for r in self.records()))

    @unittest.skipIf(sys.platform == 'win32', 'Symlink fixture needs native privileges')
    def test_symlinked_preferences_and_context_rejected(self):
        (self.root / 'workspace.local.json').unlink()
        (self.root / 'workspace.local.json').symlink_to(self.run / 'brief.md')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            router.read_local(self.root)
        (self.run / 'alias.md').symlink_to(self.run / 'brief.md')
        with self.assertRaisesRegex(ValueError, '[Ss]ymlink'):
            router.build_prompt(self.root, self.run, 'extract', ['features/alpha/alias.md'], 30000)


if __name__ == '__main__':
    unittest.main()

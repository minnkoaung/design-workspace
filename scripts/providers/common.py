"""Shared subprocess helpers; no credentials or provider configuration are copied."""
import json
import os
import signal
import subprocess


def probe(argv, root, timeout=20):
    try:
        return subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ValueError('Provider readiness check timed out; status is unknown, not invalid authentication.') from None


def worker(argv, prompt, root, folder, attempt, timeout):
    events = folder / f'attempt-{attempt}-events.jsonl'
    errors = folder / f'attempt-{attempt}-stderr.txt'
    with events.open('w', encoding='utf-8') as out, errors.open('w', encoding='utf-8') as err:
        process = subprocess.Popen(argv, cwd=root, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                   text=True, start_new_session=os.name != 'nt')
        try:
            process.communicate(input=prompt, timeout=timeout)
        except BaseException:
            if process.poll() is None:
                if os.name != 'nt':
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    if os.name != 'nt':
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.wait()
            raise
    if process.returncode:
        raise ValueError('Provider worker failed; inspect its local event/error files. No automatic auth/network retry.')
    return events


def json_report(value):
    if isinstance(value, str):
        text = value.strip()
        if text.startswith('```json') and text.endswith('```'):
            text = text[7:-3].strip()
        value = json.loads(text)
    if (not isinstance(value, dict) or set(value) != {'status', 'report', 'reason'}
            or not isinstance(value.get('status'), str) or value.get('status') not in {'complete', 'needs-escalation'}
            or not isinstance(value.get('report'), str) or not value['report'].strip()
            or not isinstance(value.get('reason'), str)):
        raise ValueError('Worker output failed report-schema validation; no automatic retry.')
    if value['status'] == 'needs-escalation' and not value['reason'].strip():
        raise ValueError('Escalation requires an explicit reason; no automatic retry.')
    return value

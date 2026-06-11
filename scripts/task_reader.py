#!/usr/bin/env python3
"""
AEGIS Task Queue — Reader
Claude uses this at session start to pull pending tasks and work on them.

Usage:
    python3 task_reader.py next              # Get highest priority pending task
    python3 task_reader.py list [--project X] # List all pending tasks
    python3 task_reader.py claim --id 1       # Claim a task (mark in_progress)
    python3 task_reader.py complete --id 1 [--output "..."] [--handoff-file "..."]
    python3 task_reader.py block --id 1 [--reason "..."]
"""

import argparse
import csv
import io
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone

# Rate limiting: max 1 API call per 5 seconds to avoid Drive API quota
_last_api_call = 0
def rate_limit():
    global _last_api_call
    elapsed = time.time() - _last_api_call
    if elapsed < 5.0:
        time.sleep(5.0 - elapsed)
    _last_api_call = time.time()

FOLDER_MAP_PATH = '/opt/data/cache/gdrive_folder_map.json'
RCLONE_REMOTE = 'gdrive:'

def get_token():
    result = subprocess.run(['rclone', 'config', 'show', RCLONE_REMOTE],
                          capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'token =' in line:
            raw = line.split('=', 1)[1].strip()
            return json.loads(raw)['access_token']
    raise RuntimeError("No token found in rclone config")

def get_file_id():
    with open(FOLDER_MAP_PATH) as f:
        return json.load(f)['task_queue']

def download_csv(token, file_id):
    rate_limit()
    url = f'https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&supportsAllDrives=true'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    resp = urllib.request.urlopen(req, timeout=15)
    return resp.read().decode('utf-8')

def upload_csv(token, file_id, content):
    url = f'https://www.googleapis.com/upload/drive/v3/files/{file_id}?uploadType=media&supportsAllDrives=true'
    req = urllib.request.Request(
        url,
        data=content.encode('utf-8'),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'text/csv'},
        method='PATCH'
    )
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

def parse_csv(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)

def to_csv(rows):
    if not rows:
        return ''
    output = io.StringIO()
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()

def find_task(rows, task_id):
    for row in rows:
        if row['id'] == str(task_id):
            return row
    return None

def save_task(rows, task):
    for i, row in enumerate(rows):
        if row['id'] == task['id']:
            rows[i] = task

def get_next(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    pending = [r for r in rows if r.get('status') == 'pending']
    if not pending:
        print("NO_PENDING_TASKS")
        return
    pending.sort(key=lambda r: (int(r.get('priority', 99)), int(r.get('id', 999))))
    task = pending[0]
    print(json.dumps(task, indent=2))

def list_pending(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    pending = [r for r in rows if r.get('status') == 'pending']
    if args.project:
        pending = [r for r in pending if r.get('project', '').lower() == args.project.lower()]
    if not pending:
        print("No pending tasks.")
        return
    pending.sort(key=lambda r: (int(r.get('priority', 99)), int(r.get('id', 999))))
    for task in pending:
        p_label = {1: 'HIGH', 2: 'MED', 3: 'LOW'}.get(int(task.get('priority', 2)), '?')
        print(f"  [{task['id']}] ({p_label}) {task['project']}: {task['title']}")

def claim_task(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    task = find_task(rows, args.id)
    if not task:
        print(f"Task #{args.id} not found")
        sys.exit(1)
    if task['status'] != 'pending':
        print(f"Task #{args.id} is not pending (status: {task['status']})")
        sys.exit(1)
    task['status'] = 'in_progress'
    save_task(rows, task)
    upload_csv(token, file_id, to_csv(rows))
    print(f"Claimed task #{args.id}: {task['title']}")
    return task

def complete_task(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    task = find_task(rows, args.id)
    if not task:
        print(f"Task #{args.id} not found")
        sys.exit(1)
    task['status'] = 'done'
    task['completed_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if args.output:
        task['output_notes'] = args.output
    if args.handoff_file:
        task['handoff_file'] = args.handoff_file
    save_task(rows, task)
    upload_csv(token, file_id, to_csv(rows))
    print(f"Completed task #{args.id}: {task['title']}")

def block_task(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    task = find_task(rows, args.id)
    if not task:
        print(f"Task #{args.id} not found")
        sys.exit(1)
    task['status'] = 'blocked'
    if args.reason:
        task['output_notes'] = f"Blocked: {args.reason}"
    save_task(rows, task)
    upload_csv(token, file_id, to_csv(rows))
    print(f"Blocked task #{args.id}: {task['title']}")

def main():
    parser = argparse.ArgumentParser(description='AEGIS Task Queue Reader')
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('next', help='Get highest priority pending task')

    list_p = subparsers.add_parser('list', help='List pending tasks')
    list_p.add_argument('--project', help='Filter by project')

    claim_p = subparsers.add_parser('claim', help='Claim a task')
    claim_p.add_argument('--id', type=int, required=True)

    comp_p = subparsers.add_parser('complete', help='Mark task as done')
    comp_p.add_argument('--id', type=int, required=True)
    comp_p.add_argument('--output', help='Completion notes')
    comp_p.add_argument('--handoff-file', help='Path to handoff file')

    block_p = subparsers.add_parser('block', help='Mark task as blocked')
    block_p.add_argument('--id', type=int, required=True)
    block_p.add_argument('--reason', help='Blocker reason')

    args = parser.parse_args()

    cmds = {
        'next': get_next,
        'list': list_pending,
        'claim': claim_task,
        'complete': complete_task,
        'block': block_task,
    }
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

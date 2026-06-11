#!/usr/bin/env python3
"""
AEGIS Task Queue — Writer
Hermes uses this to add/update tasks in the Google Drive CSV task queue.

Usage:
    python3 task_writer.py add --project NoFomo --title "Build feature" --description "..." --priority 1
    python3 task_writer.py update --id 1 --status in_progress
    python3 task_writer.py update --id 1 --status done --output "Completed successfully"
    python3 task_writer.py list [--status pending]
    python3 task_writer.py get --id 1
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
            return json.loads(line.split('=', 1)[1].strip())['access_token']
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
    rate_limit()
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

def next_id(rows):
    if not rows:
        return 1
    return max(int(r['id']) for r in rows if r.get('id', '').strip()) + 1

def add_task(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    new_task = {
        'id': str(next_id(rows)),
        'project': args.project,
        'title': args.title,
        'description': args.description or '',
        'status': 'pending',
        'priority': str(args.priority),
        'assigned_to': args.assigned_to or 'claude',
        'drive_folder_id': '',
        'created_at': now,
        'completed_at': '',
        'output_notes': '',
        'handoff_file': '',
    }
    rows.append(new_task)
    upload_csv(token, file_id, to_csv(rows))
    print(f"Task #{new_task['id']} added: {args.title}")
    return new_task['id']

def update_task(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    found = False
    for row in rows:
        if row['id'] == str(args.id):
            found = True
            if args.status:
                row['status'] = args.status
                if args.status == 'done' and not row.get('completed_at'):
                    row['completed_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
                elif args.status != 'done':
                    row['completed_at'] = ''
            if args.output:
                row['output_notes'] = args.output
            if args.handoff_file:
                row['handoff_file'] = args.handoff_file
            if args.priority:
                row['priority'] = str(args.priority)
            if args.assigned_to:
                row['assigned_to'] = args.assigned_to
            break
    if not found:
        print(f"Task #{args.id} not found", file=sys.stderr)
        sys.exit(1)
    upload_csv(token, file_id, to_csv(rows))
    print(f"Task #{args.id} updated: status={args.status}")

def list_tasks(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    if args.status:
        rows = [r for r in rows if r.get('status') == args.status]
    if args.project:
        rows = [r for r in rows if r.get('project', '').lower() == args.project.lower()]
    if not rows:
        print("No tasks found.")
        return
    rows.sort(key=lambda r: (int(r.get('priority', 99)), int(r.get('id', 999))))
    print(f"{'ID':<4} {'Priority':<9} {'Status':<12} {'Project':<18} {'Title':<40} {'Assigned':<10}")
    print('-' * 95)
    for r in rows:
        p_label = {1: 'HIGH', 2: 'MED', 3: 'LOW'}.get(int(r.get('priority', 2)), r.get('priority'))
        print(f"{r['id']:<4} {p_label:<9} {r.get('status',''):<12} {r.get('project',''):<18} {r.get('title','')[:38]:<40} {r.get('assigned_to',''):<10}")

def get_task(args):
    token = get_token()
    file_id = get_file_id()
    csv_text = download_csv(token, file_id)
    rows = parse_csv(csv_text)
    for row in rows:
        if row['id'] == str(args.id):
            for k, v in row.items():
                print(f"{k}: {v}")
            return
    print(f"Task #{args.id} not found", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='AEGIS Task Queue Manager')
    subparsers = parser.add_subparsers(dest='command')

    add_p = subparsers.add_parser('add', help='Add a new task')
    add_p.add_argument('--project', required=True)
    add_p.add_argument('--title', required=True)
    add_p.add_argument('--description', default='')
    add_p.add_argument('--priority', type=int, default=2)
    add_p.add_argument('--assigned-to', default='claude')

    upd_p = subparsers.add_parser('update', help='Update a task')
    upd_p.add_argument('--id', type=int, required=True)
    upd_p.add_argument('--status', choices=['pending','in_progress','blocked','done','cancelled'])
    upd_p.add_argument('--output')
    upd_p.add_argument('--handoff-file')
    upd_p.add_argument('--priority', type=int)
    upd_p.add_argument('--assigned-to')

    list_p = subparsers.add_parser('list', help='List tasks')
    list_p.add_argument('--status')
    list_p.add_argument('--project')

    get_p = subparsers.add_parser('get', help='Get a single task')
    get_p.add_argument('--id', type=int, required=True)

    args = parser.parse_args()
    cmds = {'add': add_task, 'update': update_task, 'list': list_tasks, 'get': get_task}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

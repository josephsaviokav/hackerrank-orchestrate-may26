#!/usr/bin/env python
"""Display sample outputs from the triage agent."""

import csv

with open('support_tickets/output.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

print('=' * 80)
print('SAMPLE TRIAGE AGENT OUTPUTS (First 3 Cases)')
print('=' * 80)

for i, row in enumerate(rows[:3], 1):
    print(f'\n[CASE {i}]')
    print(f'Status: {row["status"].upper()}')
    print(f'Type: {row["request_type"]}')
    print(f'Area: {row["product_area"]}')
    print(f'Justification: {row["justification"][:70]}...')
    resp_preview = row["response"].replace('\n', ' ')[:80]
    print(f'Response: {resp_preview}...')
    print('-' * 80)

print(f'\n\nSummary Statistics:')
print(f'Total tickets: {len(rows)}')
replied = sum(1 for r in rows if r['status'] == 'replied')
escalated = sum(1 for r in rows if r['status'] == 'escalated')
print(f'Replied: {replied} ({replied*100//len(rows)}%)')
print(f'Escalated: {escalated} ({escalated*100//len(rows)}%)')

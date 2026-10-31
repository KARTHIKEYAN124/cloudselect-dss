import csv
import json
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'

def load_records(db_path=None):
    path = db_path or DATA / 'cloudselect.db'
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS alternatives (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        # CSV is the versioned source of truth; import atomically on startup.
        records = []
        with (DATA / 'cloud_alternatives.csv').open(encoding='utf-8', newline='') as f:
            for row in csv.DictReader(f):
                for k in ['vcpu', 'ram_gib', 'max_storage_gb']: row[k] = int(row[k])
                for k in ['hourly_eur', 'storage_eur_gb', 'egress_eur_gb']: row[k] = float(row[k])
                for k in ['supported_regions', 'security_capabilities']: row[k] = row[k].split('|') if row[k] else []
                row['scores'] = {}
                row['evidence'] = {}
                records.append(row)
        with (DATA / 'criterion_scores.csv').open(encoding='utf-8', newline='') as f:
            for score in csv.DictReader(f):
                record = next(r for r in records if r['id'] == score['alternative_id'])
                if score['criterion'] != 'cost': record['scores'][score['criterion']] = float(score['score'])
                record['evidence'][score['criterion']] = score['justification']
        db.execute('DELETE FROM alternatives')
        db.executemany('INSERT INTO alternatives VALUES (?, ?)', [(r['id'], json.dumps(r)) for r in records])
        return [json.loads(row[0]) for row in db.execute('SELECT payload FROM alternatives ORDER BY id')]

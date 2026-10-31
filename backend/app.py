import json
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from dss.engine import CRITERIA, evaluate, sensitivity
from dss.repository import DATA, load_records

def create_app(db_path=None):
    app = Flask(__name__, static_folder=None)
    app.config['MAX_CONTENT_LENGTH'] = 64 * 1024
    records = load_records(db_path)

    @app.errorhandler(ValueError)
    def invalid(error): return jsonify(error=str(error)), 400

    @app.get('/api/health')
    def health(): return jsonify(status='ok', alternatives=len(records))

    @app.get('/api/alternatives')
    def alternatives(): return jsonify(records)

    @app.get('/api/criteria')
    def criteria(): return jsonify(CRITERIA)

    @app.get('/api/scenarios')
    def scenarios(): return jsonify(json.loads((DATA / 'scenarios.json').read_text(encoding='utf-8')))

    @app.post('/api/evaluate')
    @app.post('/api/compare')
    def run(): return jsonify(evaluate(records, request.get_json()))

    @app.post('/api/sensitivity')
    def experiment(): return jsonify(sensitivity(records, request.get_json()))

    @app.get('/')
    @app.get('/<path:path>')
    def frontend(path='index.html'):
        if path.startswith('api/'): return jsonify(error='Unknown endpoint'), 404
        dist = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
        if not (dist / 'index.html').exists(): return jsonify(error='Build the frontend first: cd frontend && npm install && npm run build'), 503
        return send_from_directory(dist, path if (dist / path).is_file() else 'index.html')
    return app

if __name__ == '__main__':
    from waitress import serve
    serve(create_app(), host='127.0.0.1', port=5000)

# src/reporters.py — Экспорт результатов (compact)
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict

def save_results_to_csv(results: List[Dict], filename: str = None) -> str:
    if filename is None: filename = f"results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    results_dir = Path("results"); results_dir.mkdir(exist_ok=True); filepath = results_dir / filename
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        if not results: return str(filepath)
        fieldnames = ['timestamp', 'service_name', 'host', 'avg_ms', 'min_ms', 'max_ms', 'success', 'error']
        writer = csv.DictWriter(f, fieldnames=fieldnames); writer.writeheader()
        for r in results:
            writer.writerow({'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'service_name': r.get('name', ''), 'host': r.get('host', ''), 'avg_ms': f"{r.get('avg', 0):.2f}", 'min_ms': f"{r.get('min', 0):.2f}", 'max_ms': f"{r.get('max', 0):.2f}", 'success': r.get('success', False), 'error': r.get('error', '')})
    return str(filepath)
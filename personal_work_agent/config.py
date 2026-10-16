from pathlib import Path
BASE = Path(__file__).resolve().parent
WORKSPACE = BASE / 'workspace'
DB = BASE / 'data' / 'agent.db'
MODEL = 'qwen3:4b'

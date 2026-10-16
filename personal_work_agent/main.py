import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webconfig.settings")
import django
django.setup()
from agent.core import PersonalAgent
from memory.store import initialize
from config import MODEL, WORKSPACE

def main():
    initialize()
    WORKSPACE.mkdir(exist_ok=True)
    agent = PersonalAgent()
    print(f'PERSONAL WORK AGENT | {MODEL}\nTài liệu: {WORKSPACE}\nGõ exit để thoát')
    while True:
        question = input('\nBạn: ').strip()
        if question.lower() in ('exit', 'quit'): break
        if not question: continue
        try: print('\nAgent:', agent.chat(question))
        except Exception as exc: print('Lỗi:', exc)

if __name__ == '__main__': main()

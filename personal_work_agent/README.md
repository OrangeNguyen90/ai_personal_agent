# Personal Work Agent — PostgreSQL Local

## Cài đặt Windows
1. Cài PostgreSQL và tạo role `agent_user`, database `personal_agent_db` thuộc role này.
2. `python -m venv venv` và `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` thành `.env`, sửa `PGPASSWORD` và `DJANGO_SECRET_KEY`.
5. `python manage.py makemigrations dashboard` và `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `ollama pull qwen3:4b` (hoặc sửa MODEL trong config.py)
8. `python manage.py runserver 127.0.0.1:8000`

Chạy CLI riêng: `python main.py`.

Django tables, tasks, memories nằm chung database PostgreSQL. Workspace chứa file thực tế. Dữ liệu SQLite cũ KHÔNG tự chuyển; hãy sao lưu các file .db cũ trước khi thay thế project. Bản này dành cho một người dùng tin cậy trên localhost, chưa tách memory/task theo từng tài khoản.

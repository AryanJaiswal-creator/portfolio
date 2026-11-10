# Aryan — Full-stack developer portfolio

A responsive, cinematic portfolio built with Flask, SQLite, Jinja templates, HTML, CSS and vanilla JavaScript. Includes a working contact workflow and a private admin area.

## What's included
- Home, About, Projects, project case study and Contact pages
- Responsive navigation, scroll reveal effects and reduced-motion support
- Portrait-led hero using the photo supplied in this conversation
- Jaiswal Press case study based on the supplied source archive
- Contact form stored in SQLite
- Admin login, message inbox, read/unread toggle, delete, and editable profile details
- CSRF protection for admin POST actions and environment-based password hash

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set a unique secret and admin password hash. Generate a password hash:

```bash
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-strong-password'))"
```

Paste the result into `ADMIN_PASSWORD_HASH`. Then run:

```bash
python app.py
```

Open http://127.0.0.1:5000. Admin: http://127.0.0.1:5000/admin/login

## Before publishing
1. Replace the development `SECRET_KEY` and set a strong `ADMIN_PASSWORD_HASH` in your hosting environment.
2. Add your real public email, GitHub and LinkedIn URLs from the Admin dashboard.
3. Verify your public bio and project role/details; unconfirmed education, client permissions, metrics and achievements have intentionally not been invented.
4. Deploy behind HTTPS with `FLASK_DEBUG=0`, persistent storage for `portfolio.db`, and regular backups.
5. Configure a production WSGI server (for example Gunicorn) rather than Flask's development server.

## Project case study accuracy
The featured Jaiswal Press case study is derived from the uploaded ZIP. Its source includes Flask routes, SQLite enquiry/content tables, a protected admin section, content and template editors, image upload handling, and enquiry search/status/export. The portfolio labels this as a full-stack project without inventing traffic, sales, client outcomes or performance metrics.

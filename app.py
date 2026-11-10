import os, sqlite3, secrets, time
from pathlib import Path
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()
BASE = Path(__file__).resolve().parent
DB = BASE / 'portfolio.db'
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')
if not app.secret_key:
    raise RuntimeError('SECRET_KEY is missing. Copy .env.example to .env and set it before starting the app.')
if not ADMIN_PASSWORD_HASH:
    raise RuntimeError('ADMIN_PASSWORD_HASH is missing. Generate a Werkzeug password hash and set it in .env.')
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=2*1024*1024)
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')

PROJECT = {
 'slug':'jaiswal-press', 'name':'Jaiswal Press', 'type':'Client website',
 'tagline':'A complete digital presence for a print business.',
 'description':'A multi-page business website with a custom Flask backend, SQLite data storage and a password-protected administration area.',
 'year':'2026', 'stack':['Python','Flask','SQLite','HTML','CSS','JavaScript'],
 'features':['Five responsive public pages','Protected administrator login','Editable website content and full-page templates','Image uploads and image library','Contact form with SQLite enquiry storage','Enquiry search, read/unread status and CSV export'],
 'role':'Full-stack development', 'note':'Project details are based on the supplied source-code archive.'
}

def db():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; return con

def init_db():
    with db() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,email TEXT NOT NULL,subject TEXT,message TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP,is_read INTEGER DEFAULT 0)''')
        con.execute('''CREATE TABLE IF NOT EXISTS profile(key TEXT PRIMARY KEY,value TEXT NOT NULL)''')
        defaults={'headline':'Curious mind. Creative execution.','intro':'I’m Aryan — a curious learner exploring technology, programming and software development. I enjoy solving problems, experimenting with ideas and turning them into useful digital experiences.','email':'','github':'','linkedin':'','availability':'Open to learning, collaboration and meaningful projects.'}
        for k,v in defaults.items(): con.execute('INSERT OR IGNORE INTO profile(key,value) VALUES(?,?)',(k,v))
init_db()

def csrf():
    if '_csrf' not in session: session['_csrf']=secrets.token_hex(24)
    return session['_csrf']
app.jinja_env.globals['csrf_token']=csrf
@app.before_request
def protect_posts():
    if request.method=='POST' and request.path.startswith('/admin'):
        if not secrets.compare_digest(request.form.get('_csrf',''),session.get('_csrf','')):
            abort(400)
def admin_required(fn):
    @wraps(fn)
    def wrapped(*a,**kw):
        if not session.get('admin'): return redirect(url_for('login',next=request.path))
        return fn(*a,**kw)
    return wrapped

def profile():
    with db() as con: return {r['key']:r['value'] for r in con.execute('SELECT * FROM profile')}

@app.route('/')
def home(): return render_template('home.html',profile=profile(),project=PROJECT)
@app.route('/about')
def about(): return render_template('about.html',profile=profile())
@app.route('/projects')
def projects(): return render_template('projects.html',project=PROJECT)
@app.route('/projects/<slug>')
def project_detail(slug):
    if slug != PROJECT['slug']: abort(404)
    return render_template('project_detail.html',project=PROJECT)
@app.route('/contact',methods=['GET','POST'])
def contact():
    if request.method=='POST':
        name=request.form.get('name','').strip()[:100]; email=request.form.get('email','').strip()[:160]; subject=request.form.get('subject','').strip()[:160]; message=request.form.get('message','').strip()[:5000]
        if not name or '@' not in email or len(message)<5:
            flash('Please enter your name, a valid email and a message.','error')
            return render_template('contact.html',profile=profile())
        with db() as con: con.execute('INSERT INTO messages(name,email,subject,message) VALUES(?,?,?,?)',(name,email,subject,message))
        flash('Message received. Thanks for reaching out.','success'); return redirect(url_for('contact'))
    return render_template('contact.html',profile=profile())
@app.route('/admin/login',methods=['GET','POST'])
def login():
    if session.get('admin'): return redirect(url_for('dashboard'))
    if request.method=='POST':
        password=request.form.get('password','')
        if ADMIN_PASSWORD_HASH and check_password_hash(ADMIN_PASSWORD_HASH,password):
            session.clear(); session['admin']=True; return redirect(url_for('dashboard'))
        flash('Login failed. Check your password and try again.','error')
    return render_template('login.html')
@app.route('/admin/logout',methods=['POST'])
@admin_required
def logout(): session.clear(); return redirect(url_for('home'))
@app.route('/admin')
@admin_required
def dashboard():
    with db() as con:
        messages=con.execute('SELECT * FROM messages ORDER BY id DESC').fetchall()
        total=con.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
        unread=con.execute('SELECT COUNT(*) FROM messages WHERE is_read=0').fetchone()[0]
    return render_template('dashboard.html',messages=messages,total=total,unread=unread,profile=profile())
@app.route('/admin/message/<int:mid>/toggle',methods=['POST'])
@admin_required
def toggle_message(mid):
    with db() as con: con.execute('UPDATE messages SET is_read=CASE is_read WHEN 0 THEN 1 ELSE 0 END WHERE id=?',(mid,))
    return redirect(url_for('dashboard'))
@app.route('/admin/message/<int:mid>/delete',methods=['POST'])
@admin_required
def delete_message(mid):
    with db() as con: con.execute('DELETE FROM messages WHERE id=?',(mid,))
    return redirect(url_for('dashboard'))
@app.route('/admin/profile',methods=['POST'])
@admin_required
def update_profile():
    allowed={'headline','intro','email','github','linkedin','availability'}
    with db() as con:
        for k in allowed:
            if k in request.form: con.execute('INSERT INTO profile(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(k,request.form[k].strip()[:3000]))
    flash('Profile settings saved.','success'); return redirect(url_for('dashboard'))
@app.errorhandler(404)
def not_found(e): return render_template('404.html'),404
if __name__=='__main__': app.run(debug=os.getenv('FLASK_DEBUG')=='1')

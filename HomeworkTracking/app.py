from flask import Flask, render_template, request, redirect, url_for
import sqlite3, os

app = Flask(__name__)

# ---- Veritabanı oluşturma veya kontrol etme ----
def init_db():
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS assignments
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT, teacher_id INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY, assignment_id INTEGER, student_id INTEGER, content TEXT, parent_check TEXT)''')
    conn.commit()
    conn.close()
    print("✅ Veritabanı hazır: odev.db")

# ---- Giriş sayfası ----
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    role = request.form['role']
    return redirect(url_for(f'{role}_dashboard', name=name))

# ---- Hoca Paneli ----
@app.route('/teacher/<name>')
def teacher_dashboard(name):
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute("SELECT * FROM assignments")
    assignments = c.fetchall()
    conn.close()
    return render_template('teacher_dashboard.html', name=name, assignments=assignments)

@app.route('/teacher/<name>/add', methods=['POST'])
def add_assignment(name):
    title = request.form['title']
    desc = request.form['desc']
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute("INSERT INTO assignments (title, description, teacher_id) VALUES (?, ?, ?)", (title, desc, 1))
    conn.commit()
    conn.close()
    return redirect(url_for('teacher_dashboard', name=name))

# ---- Öğrenci Paneli ----
@app.route('/student/<name>')
def student_dashboard(name):
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute("SELECT * FROM assignments")
    assignments = c.fetchall()
    conn.close()
    return render_template('student_dashboard.html', name=name, assignments=assignments)

@app.route('/submit/<int:assignment_id>', methods=['POST'])
def submit_assignment(assignment_id):
    content = request.form['content']
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute("INSERT INTO submissions (assignment_id, student_id, content, parent_check) VALUES (?, ?, ?, ?)",
              (assignment_id, 1, content, 'Bekliyor'))
    conn.commit()
    conn.close()
    return redirect(url_for('student_dashboard', name='ogrenci'))

# ---- Veli Paneli ----
@app.route('/parent/<name>')
def parent_dashboard(name):
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute("SELECT * FROM submissions")
    submissions = c.fetchall()
    conn.close()
    return render_template('parent_dashboard.html', name=name, submissions=submissions)

@app.route('/parent/check/<int:submission_id>/<status>')
def parent_check(submission_id, status):
    conn = sqlite3.connect('odev.db')
    c = conn.cursor()
    c.execute("UPDATE submissions SET parent_check=? WHERE id=?", (status, submission_id))
    conn.commit()
    conn.close()
    return redirect(url_for('parent_dashboard', name='veli'))

# ---- Ana çalıştırma ----
if __name__ == '__main__':
    if not os.path.exists('odev.db'):
        print("📂 odev.db bulunamadı, oluşturuluyor...")
        init_db()
    else:
        print("💾 odev.db zaten mevcut, tablo kontrolü yapılıyor...")
        init_db()

    app.run(debug=True)

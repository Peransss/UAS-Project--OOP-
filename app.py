from flask import  Flask, flash, redirect, render_template, request, url_for, session
from config import Config

class MataKuliah:
    def __init__(self, nama, deskripsi, materi, video_url):
        self.nama = nama
        self.deskripsi = deskripsi
        self.materi = materi  # list of string
        self.video_url = video_url

# Data matkul
matkul_dict = {
    "Struktur Data": MataKuliah(
        "Struktur Data",
        "Struktur Data membahas cara menyimpan, mengelola, dan memproses data secara efisien.",
        ["Array & Linked List", "Stack & Queue", "Tree & Graph"],
        "https://www.youtube.com/embed/1OEu9C51K2A"
    ),
    "Aljabar Linier": MataKuliah(
        "Aljabar Linier",
        "Aljabar Linier mempelajari vektor, matriks, dan transformasi linier.",
        ["Vektor & Matriks", "SPL", "Transformasi Linier"],
        "https://www.youtube.com/embed/2OEu9C51K2B"
    ),
    "Pemrograman Dasar": MataKuliah(
        "Pemrograman Dasar",
        "Pemrograman Dasar mengenalkan konsep dasar pemrograman komputer.",
        ["Variabel & Tipe Data", "Percabangan & Perulangan", "Fungsi"],
        "https://www.youtube.com/embed/3OEu9C51K2C"
    ),
    # Tambahkan matkul lain sesuai kebutuhan
}

class App_Kursus:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = '!@#$%^&*()'
        self.con = Config()
        self.routes()

    def routes(self):
        @self.app.route('/testdb')
        def testdb():
            try:
                if self.con.mysql is not None:
                    return "Database connection successful"
            except Exception as e:
                return f"Database connection failed: {e}"

        @self.app.route('/')
        def index():
            return render_template('main.html')

        @self.app.route('/index')
        def index2():
            return render_template('main.html')

        @self.app.route('/bantuan')
        def bantuan():
            return render_template('bantuan.html')

        @self.app.route('/login/')
        def login():
            return render_template('login.html')

        @self.app.route('/register/')
        def register():
            return render_template('register.html')

        @self.app.route('/reg-ai')
        def reg_ai():
            return render_template('register-admin-instruktur.html')

        @self.app.route('/login/process', methods=['POST'])
        def loginProcess():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                role = request.form.get('role')

                cur = self.con.mysql.cursor()
                try:
                    if role:
                        cur.execute(
                            "SELECT * FROM users WHERE username = %s AND password = md5(%s) AND role = %s",
                            (username, password, role)
                        )
                    else:
                        cur.execute(
                            "SELECT * FROM users WHERE username = %s AND password = md5(%s)",
                            (username, password)
                        )

                    user = cur.fetchone()
                    cur.close()

                    if user:
                        session['user_id'] = user[0]
                        session['username'] = user[2]
                        session['role'] = user[4]
                        flash('Login successful!', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash('Invalid credentials or role!', 'error')
                        return redirect(url_for('login'))
                except Exception as e:
                    flash(f"Login failed: {e}", 'error')
                    return redirect(url_for('login'))

        @self.app.route('/register/process', methods=['POST'])
        def registerProcess():
            if request.method == 'POST':
                full_name = request.form['full_name']
                username = request.form['username']
                password = request.form['password']
                role = 'Mahasiswa'

                cur = self.con.mysql.cursor()
                try:
                    cur.execute(
                        'INSERT INTO users (fullname, username, password, role) VALUES (%s, %s, md5(%s), %s)',
                        (full_name, username, password, role)
                    )
                    self.con.mysql.commit()
                    flash('Registration successful! You can now log in.', 'success')
                except Exception as e:
                    flash(f'Registration failed: {e}', 'error')
                finally:
                    cur.close()

                return redirect(url_for('login'))

        @self.app.route('/register-admin-instruktur/process', methods=['POST'])
        def registerAdminInstrukturProcess():
            if request.method == 'POST':
                full_name = request.form['full_name']
                username = request.form['username']
                password = request.form['password']
                role = request.form['role']

                if role not in ['admin', 'instruktur']:
                    flash('Invalid role selected!', 'error')
                    return redirect(url_for('reg_ai'))

                cur = self.con.mysql.cursor()
                try:
                    cur.execute(
                        'INSERT INTO users (fullname, username, password, role) VALUES (%s, %s, md5(%s), %s)',
                        (full_name, username, password, role)
                    )
                    self.con.mysql.commit()
                    flash('Registration successful! You can now log in.', 'success')
                except Exception as e:
                    flash(f'Registration failed: {e}', 'error')
                finally:
                    cur.close()

                return redirect(url_for('login'))

        @self.app.route('/logout')
        def logout():
            session.clear()
            flash('You have been logged out.', 'info')
            return redirect(url_for('login'))

        # Python
        @self.app.route('/courses/view')
        def view_courses():
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
                    # Fetch courses based on user role
                    if user_role == "mahasiswa":
                        cur.execute("SELECT * FROM courses WHERE visibility = 'public'")
                    elif user_role == "instruktur":
                        cur.execute("SELECT * FROM courses WHERE instructor_id = %s", (user_id,))
                    elif user_role == "admin":
                        cur.execute("SELECT * FROM courses")
                    else:
                        flash("Invalid role detected!", "error")
                        return redirect(url_for('login'))

                    courses = cur.fetchall()
                    return render_template('courses.html', courses=courses, role=user_role)
                except Exception as e:
                    flash(f"Error fetching courses: {e}", "error")
                    return redirect(url_for('index'))
                finally:
                    cur.close()
            else:
                flash("Please log in to view courses.", "error")
                return redirect(url_for('login'))

        @self.app.route('/courses/edit', methods=['GET', 'POST'])
        def edit_courses():
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
                    if request.method == 'POST':
                        course_id = request.form['course_id']
                        course_name = request.form['course_name']
                        course_description = request.form['course_description']

                        if user_role == "mahasiswa":
                            flash("Permission denied! Mahasiswa cannot edit courses.", "error")
                            return redirect(url_for('view_courses'))
                        elif user_role == "instruktur":
                            cur.execute(
                                "UPDATE courses SET name = %s, description = %s WHERE id = %s AND instructor_id = %s",
                                (course_name, course_description, course_id, user_id)
                            )
                        elif user_role == "admin":
                            cur.execute(
                                "UPDATE courses SET name = %s, description = %s WHERE id = %s",
                                (course_name, course_description, course_id)
                            )
                        else:
                            flash("Invalid role detected!", "error")
                            return redirect(url_for('login'))

                        self.con.mysql.commit()
                        flash("Course updated successfully!", "success")
                        return redirect(url_for('view_courses'))
                    else:
                        if user_role == "mahasiswa":
                            flash("Permission denied! Mahasiswa cannot edit courses.", "error")
                            return redirect(url_for('view_courses'))
                        elif user_role == "instruktur":
                            cur.execute("SELECT * FROM courses WHERE instructor_id = %s", (user_id,))
                        elif user_role == "admin":
                            cur.execute("SELECT * FROM courses")
                        else:
                            flash("Invalid role detected!", "error")
                            return redirect(url_for('login'))

                        courses = cur.fetchall()
                        return render_template('edit_courses.html', courses=courses, role=user_role)
                except Exception as e:
                    flash(f"Error editing courses: {e}", "error")
                    return redirect(url_for('view_courses'))
                finally:
                    cur.close()
            else:
                flash("Please log in to edit courses.", "error")
                return redirect(url_for('login'))

        def get_komentar_for_matkul(nama_matkul):
            # Kembalikan list komentar sesuai matkul, atau list kosong
            return []

        @self.app.route('/mulaibelajar')
        def mulaibelajar():
            nama_matkul = request.args.get('matkul')
            matkul = matkul_dict.get(nama_matkul)
            if not matkul:
                flash("Mata kuliah tidak ditemukan.", "error")
                return redirect(url_for('index'))
            return render_template('mulaibelajar.html', matkul=matkul)


    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
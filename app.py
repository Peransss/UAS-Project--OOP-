from flask import  Flask, flash, redirect, render_template, request, url_for, session
from config import Config

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

        @self.app.route('/courses/view', methods=['GET'])
        def view_or_mulaibelajar():
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')
                matkul = request.args.get('matkul')

                cur = self.con.mysql.cursor()
                try:
                    if matkul:
                        cur.execute("""
                            SELECT c.id, c.name, c.description, c.materials, c.videos, u.fullname AS instructor_name
                            FROM courses c
                            LEFT JOIN users u ON c.instructor_id = u.id
                            WHERE c.name = %s
                        """, (matkul,))
                        matkul_data = cur.fetchone()

                        if not matkul_data:
                            cur.execute("""
                                INSERT INTO courses (name, description, visibility, materials, videos, instructor_id)
                                VALUES (%s, %s, %s, %s, %s, NULL)
                            """, (matkul, 'Deskripsi belum tersedia', 'public', '[]', '[]'))
                            self.con.mysql.commit()

                            cur.execute("""
                                SELECT c.id, c.name, c.description, c.materials, c.videos, u.fullname AS instructor_name
                                FROM courses c
                                LEFT JOIN users u ON c.instructor_id = u.id
                                WHERE c.name = %s
                            """, (matkul,))
                            matkul_data = cur.fetchone()

                        cur.execute("""
                            SELECT u.fullname, cm.comment, cm.created_at
                            FROM comments cm
                            JOIN users u ON cm.user_id = u.id
                            WHERE cm.course_id = %s
                            ORDER BY cm.created_at DESC
                        """, (matkul_data[0],))
                        komentar_list = cur.fetchall()


                        return render_template('mulaibelajar.html', matkul=matkul_data, komentar_list=komentar_list,
                                               id_matkul=matkul_data[0])
                    else:
                        # Handle `view_courses` functionality
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
                        return render_template('mulaibelajar.html', courses=courses, role=user_role)
                except Exception as e:
                    flash(f"Error: {e}", "error")
                    return redirect(url_for('index'))
                finally:
                    cur.close()
            else:
                flash("Please log in to view courses.", "error")
                return redirect(url_for('login'))


        def get_komentar_for_matkul(nama_matkul):
            return []

        @self.app.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
        def edit_mulaibelajar(course_id):
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
                    if request.method == 'POST':
                        cur.execute("SELECT name, description, materials, videos FROM courses WHERE id = %s",
                                    (course_id,))
                        current_course = cur.fetchone()

                        if not current_course:
                            flash("Course not found!", "error")
                            return redirect(url_for('view_courses'))

                        course_name = request.form.get('name', current_course[0])
                        course_description = request.form.get('description', current_course[1])
                        course_materials = request.form.get('materials', current_course[2])
                        course_videos = request.form.get('videos', current_course[3])

                        if user_role == "instruktur":
                            cur.execute(
                                "UPDATE courses SET name = %s, description = %s, materials = %s, videos = %s WHERE id = %s AND instructor_id = %s",
                                (course_name, course_description, course_materials, course_videos, course_id, user_id)
                            )
                        elif user_role == "admin":
                            cur.execute(
                                "UPDATE courses SET name = %s, description = %s, materials = %s, videos = %s WHERE id = %s",
                                (course_name, course_description, course_materials, course_videos, course_id)
                            )
                        else:
                            flash("Permission denied!", "error")
                            return redirect(url_for('view_courses'))

                        self.con.mysql.commit()
                        flash("Course updated successfully!", "success")
                        return redirect(url_for('view_courses'))
                    else:
                        cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
                        course = cur.fetchone()

                        if not course:
                            flash("Course not found!", "error")
                            return redirect(url_for('view_courses'))

                        return render_template('edit_mulaibelajar.html', course=course)
                except Exception as e:
                    flash(f"Error editing course: {e}", "error")
                    return redirect(url_for('view_courses'))
                finally:
                    cur.close()
            else:
                flash("Please log in to edit courses.", "error")
                return redirect(url_for('login'))

        @self.app.route('/view_courses', methods=['GET'])
        def view_courses():
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
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
                    if not courses:
                        flash("No courses found!", "info")
                    return render_template('view_courses.html', courses=courses, role=user_role)
                except Exception as e:
                    flash(f"Error fetching courses: {e}", "error")
                    return redirect(url_for('index'))
                finally:
                    cur.close()
            else:
                flash("Please log in to view courses.", "error")
                return redirect(url_for('login'))
        self.app.run(debug=True)

if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
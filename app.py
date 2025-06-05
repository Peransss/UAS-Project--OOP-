from flask import  Flask, flash, redirect, render_template, request, url_for, session
from config import Config
import os, pdfkit

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
                        session['fullname'] = user[1]
                        session['username'] = user[2]
                        session['role'] = user[4]

                        if session['role'] == 'admin':
                            session['role'] = 'Admin'
                        elif session['role'] == 'mahasiswa':
                            session['role'] = 'Mahasiswa'
                        else:
                            session['role'] = 'Instruktur'

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
                        # Check if the user has purchased the course
                        cur.execute("""
                            SELECT * FROM purchases WHERE user_id = %s AND course_id = (
                                SELECT id FROM courses WHERE name = %s
                            )
                        """, (user_id, matkul))
                        purchase = cur.fetchone()

                        # Fetch course data
                        cur.execute("""
                            SELECT c.id, c.name, c.description, c.materials, c.videos, u.fullname AS instructor_name
                            FROM courses c
                            LEFT JOIN users u ON c.instructor_id = u.id
                            WHERE c.name = %s
                        """, (matkul,))
                        matkul_data = cur.fetchone()

                        # Fetch comments
                        cur.execute("""
                            SELECT u.fullname, cm.comment, cm.created_at
                            FROM comments cm
                            JOIN users u ON cm.user_id = u.id
                            WHERE cm.course_id = %s
                            ORDER BY cm.created_at DESC
                        """, (matkul_data[0],))
                        komentar_list = cur.fetchall()

                        # Render the page with locked content if not purchased
                        return render_template(
                            'mulaibelajar.html',
                            matkul=matkul_data,
                            komentar_list=komentar_list,
                            id_matkul=matkul_data[0],
                            nama_ins=matkul_data[5],
                            is_locked=not purchase  # Pass locked status to the template
                        )
                    else:
                        # Display list of courses
                        if user_role == "Mahasiswa":
                            cur.execute("SELECT * FROM courses WHERE visibility = 'public'")
                        elif user_role == "Instruktur":
                            cur.execute("SELECT * FROM courses WHERE instructor_id = %s", (user_id,))
                        elif user_role == "Admin":
                            cur.execute("SELECT * FROM courses")
                        else:
                            flash("Invalid role detected!", "error")
                            return redirect(url_for('login'))

                        courses = cur.fetchall()
                        return render_template('mulaibelajar.html', courses=courses)
                except Exception as e:
                    flash(f"Error: {e}", "error")
                    return redirect(url_for('index'))
                finally:
                    cur.close()
            else:
                flash("Please log in to view courses.", "error")
                return redirect(url_for('login'))

        @self.app.route('/courses/edit/<int:course_id>', methods=['GET'])
        def edit_course(course_id):
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
                    cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
                    course = cur.fetchone()

                    if not course:
                        flash("Course not found!", "error")
                        return redirect(url_for('view_courses'))

                    if user_role == "Instruktur" and course[6] != user_id:
                        flash("You are not authorized to edit this course!", "error")
                        return redirect(url_for('view_courses'))

                    return render_template('edit_mulaibelajar.html', course=course, course_id=course_id)
                except Exception as e:
                    flash(f"Error fetching course: {e}", "error")
                    return redirect(url_for('view_courses'))
                finally:
                    cur.close()
            else:
                flash("Please log in to edit courses.", "error")
                return redirect(url_for('login'))

        @self.app.route('/courses/edit/process/<int:course_id>', methods=['POST'])
        def edit_course_process(course_id):
            if 'user_id' in session:
                user_role = session.get('role')
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
                    cur.execute("SELECT * FROM courses WHERE id = %s", (course_id,))
                    course = cur.fetchone()

                    if not course:
                        flash("Course not found!", "error")
                        return redirect(url_for('view_courses'))

                    if user_role == "Instruktur" and course[6] != user_id:
                        flash("You are not authorized to edit this course!", "error")
                        return redirect(url_for('view_courses'))

                    course_name = request.form.get('name') or course[1]
                    course_description = request.form.get('description') or course[2]
                    course_materials = request.form.get('materials') or course[3]
                    course_videos = request.form.get('videos') or course[4]
                    instructor_id = request.form.get('instructor_id') or course[6]

                    cur.execute(
                        "UPDATE courses SET name = %s, description = %s, materials = %s, videos = %s, instructor_id = %s WHERE id = %s",
                        (course_name, course_description, course_materials, course_videos, instructor_id, course_id)
                    )
                    self.con.mysql.commit()
                    flash("Course updated successfully!", "success")
                    return redirect(url_for('view_courses'))
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
                    if user_role == "Mahasiswa":
                        cur.execute("SELECT * FROM courses WHERE visibility = 'public'")
                    elif user_role == "Instruktur":
                        cur.execute("SELECT * FROM courses WHERE instructor_id = %s", (user_id,))
                    elif user_role == "Admin":
                        cur.execute("SELECT * FROM courses")
                    else:
                        flash("Invalid role detected!", "error")
                        return redirect(url_for('login'))

                    courses = cur.fetchall()
                    if not courses:
                        flash("No courses found!", "info")
                    return render_template('main.html', courses=courses, role=user_role)
                except Exception as e:
                    flash(f"Error fetching courses: {e}", "error")
                    return redirect(url_for('index'))
                finally:
                    cur.close()
            else:
                flash("Please log in to view courses.", "error")
                return redirect(url_for('login'))

        @self.app.route('/courses/buy/<int:course_id>', methods=['POST'])
        def buy_course(course_id):
            if 'user_id' in session:
                user_id = session.get('user_id')

                cur = self.con.mysql.cursor()
                try:
                    # Periksa apakah course sudah dibeli
                    cur.execute("SELECT * FROM purchases WHERE user_id = %s AND course_id = %s", (user_id, course_id))
                    purchase = cur.fetchone()

                    if purchase:
                        flash("Anda sudah membeli course ini!", "info")
                        return redirect(url_for('view_courses'))

                    # Tambahkan pembelian
                    cur.execute("INSERT INTO purchases (user_id, course_id) VALUES (%s, %s)", (user_id, course_id))
                    self.con.mysql.commit()
                    flash("Pembelian berhasil!", "success")
                    return redirect(url_for('view_courses'))
                except Exception as e:
                    flash(f"Error: {e}", "error")
                    return redirect(url_for('view_courses'))
                finally:
                    cur.close()
            else:
                flash("Please log in to buy courses.", "error")
                return redirect(url_for('login'))

        @self.app.route('/transaction')
        def transaction():
            if 'user_id' not in session:
                flash("Please log in to view transactions.", "error")
                return redirect(url_for('login'))

            user_id = session['user_id']
            cur = self.con.mysql.cursor()
            try:
                # Fetch transactions for the logged-in user
                cur.execute('''
                    SELECT u.fullname AS user_name, c.name AS course_name, p.purchase_date
                    FROM purchases p
                    JOIN users u ON p.user_id = u.id
                    JOIN courses c ON p.course_id = c.id
                    WHERE p.user_id = %s
                ''', (user_id,))
                data = cur.fetchall()
            except Exception as e:
                flash(f"Error fetching transaction data: {e}", "error")
                return redirect(url_for('index'))
            finally:
                cur.close()

            # Render template HTML for the report
            rendered = render_template('transaction.html', data=data)

            # Set the path to the wkhtmltopdf executable
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

            # Define options for wkhtmltopdf
            options = {
                'enable-local-file-access': True,
                'disable-smart-shrinking': True,
                'quiet': ''
            }

            # Generate the PDF using the configuration and options
            pdf = pdfkit.from_string(rendered, False, configuration=config, options=options)

            # Send the PDF file as a response
            response = self.app.response_class(pdf, content_type='application/pdf')
            response.headers['Content-Disposition'] = f'inline; filename={session.get("fullname")}-transaction.pdf'
            return response

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
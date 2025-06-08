from flask import Flask, flash, redirect, render_template, request, url_for, session
from config import Config
import json
import pdfkit

class Session:
    #ENKAPSULASI koneksi database dan session
    def __init__(self, db_connection):
        self.con = db_connection
        self.mysql = self.con.mysql

    def get_user_session(self):
        if 'user_id' in session:
            return {
                'user_id': session.get('user_id'),
                'fullname': session.get('fullname'),
                'role': session.get('role')
            }
        return None


class AuthController(Session):
    #ENKAPSULASI semua terkait authtentication user
    #INHERITANCE dari Session untuk akses database
    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role')

            cur = self.mysql.cursor()
            try:
                query = "SELECT * FROM users WHERE username = %s AND password = md5(%s)"
                params = (username, password)
                if role:
                    query += " AND role = %s"
                    params += (role,)

                cur.execute(query, params)
                user = cur.fetchone()
                cur.close()

                if user:
                    session['user_id'] = user[0]
                    session['fullname'] = user[1]
                    session['username'] = user[2]
                    session['role'] = user[4].capitalize()

                    flash('Login successful!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid credentials or role!', 'error')
                    return redirect(url_for('login'))
            except Exception as e:
                flash(f"Login failed: {e}", 'error')
                return redirect(url_for('login'))
        return render_template('login.html')

    def register(self, role='Mahasiswa'):
        if request.method == 'POST':
            full_name = request.form['full_name']
            username = request.form['username']
            password = request.form['password']

            if 'role' in request.form:
                role = request.form['role']
                if role not in ['admin', 'instruktur']:
                    flash('Invalid role selected!', 'error')
                    return redirect(url_for('reg_ai'))

            cur = self.mysql.cursor()
            try:
                cur.execute(
                    'INSERT INTO users (fullname, username, password, role) VALUES (%s, %s, md5(%s), %s)',
                    (full_name, username, password, role)
                )
                self.mysql.commit()
                flash('Registration successful! You can now log in.', 'success')
            except Exception as e:
                self.mysql.rollback()
                flash(f'Registration failed: {e}', 'error')
            finally:
                cur.close()
            return redirect(url_for('login'))
        if role == 'Mahasiswa':
            return render_template('register.html')
        else:
            return render_template('register-admin-instruktur.html')

    def logout(self):
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))


class CourseController(Session):
    #ENKAPSULASI terkait kursus
    #INHERITANCE dari Session untuk akses database
    def get_courses_by_role(self, user_role, user_id):
        cur = self.mysql.cursor()
        if user_role == "Mahasiswa":
            cur.execute("SELECT * FROM courses WHERE visibility = 'public'")
        elif user_role == "Instruktur":
            cur.execute("SELECT * FROM courses WHERE instructor_id = %s", (user_id,))
        elif user_role == "Admin":
            cur.execute("SELECT * FROM courses")
        else:
            cur.close()
            return None
        courses = cur.fetchall()
        cur.close()
        return courses

    def view_all_courses(self):
        user_session = self.get_user_session()
        if not user_session:
            flash("Please log in to view courses.", "error")
            return redirect(url_for('login'))

        try:
            courses = self.get_courses_by_role(user_session['role'], user_session['user_id'])
            if courses is None:
                flash("Invalid role detected!", "error")
                return redirect(url_for('login'))

            if not courses:
                flash("No courses found!", "info")

            return render_template('main.html', courses=courses, role=user_session['role'])
        except Exception as e:
            flash(f"Error fetching courses: {e}", "error")
            return redirect(url_for('index'))

    def view_or_manage_single_course(self):
        user_session = self.get_user_session()
        if not user_session:
            flash("Please log in to view courses.", "error")
            return redirect(url_for('login'))

        matkul_name = request.args.get('matkul')
        if not matkul_name:
            courses = self.get_courses_by_role(user_session['role'], user_session['user_id'])
            return render_template('mulaibelajar.html', courses=courses)

        cur = self.mysql.cursor()
        try:
            cur.execute("""
                SELECT c.id, c.name, c.description, c.materials, c.videos, u.fullname AS instructor_name
                FROM courses c LEFT JOIN users u ON c.instructor_id = u.id
                WHERE c.name = %s
            """, (matkul_name.strip(),))
            matkul_data = cur.fetchone()

            if not matkul_data:
                flash("Mata kuliah tidak ditemukan!", "error")
                return redirect(url_for('view_or_mulaibelajar'))

            course_id = matkul_data[0]

            if request.method == 'POST':
                komentar = request.form.get('comment')
                if komentar:
                    cur.execute("INSERT INTO comments (course_id, user_id, comment) VALUES (%s, %s, %s)",
                                (course_id, user_session['user_id'], komentar))
                    self.mysql.commit()
                    flash("Komentar berhasil dikirim", "success")

            cur.execute("""
                SELECT u.fullname, cm.comment, cm.created_at
                FROM comments cm JOIN users u ON cm.user_id = u.id
                WHERE cm.course_id = %s ORDER BY cm.created_at DESC
            """, (course_id,))
            komentar_list = cur.fetchall()

            is_locked = True
            if user_session['role'] in ['Instruktur', 'Admin']:
                is_locked = False
            else:
                cur.execute("SELECT * FROM purchases WHERE user_id = %s AND course_id = %s",
                            (user_session['user_id'], course_id))
                is_locked = not cur.fetchone()

            materi_list = json.loads(matkul_data[3]) if matkul_data[3] else []
            videos_list = json.loads(matkul_data[4]) if matkul_data[4] else []

            return render_template(
                'mulaibelajar.html', matkul=matkul_data, komentar_list=komentar_list,
                id_matkul=course_id, materi_list=materi_list, videos_list=videos_list,
                nama_ins=matkul_data[5], is_locked=is_locked, videos_json=json.dumps(videos_list)
            )
        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for('index'))
        finally:
            cur.close()

    def buy_course(self, course_id):
        user_session = self.get_user_session()
        if not user_session:
            flash("Please log in to buy courses.", "error")
            return redirect(url_for('login'))

        cur = self.mysql.cursor()
        try:
            cur.execute("SELECT * FROM purchases WHERE user_id = %s AND course_id = %s",
                        (user_session['user_id'], course_id))
            if cur.fetchone():
                flash("Anda sudah membeli course ini!", "info")
            else:
                cur.execute("INSERT INTO purchases (user_id, course_id) VALUES (%s, %s)",
                            (user_session['user_id'], course_id))
                self.mysql.commit()
                flash("Pembelian berhasil!", "success")
        except Exception as e:
            self.mysql.rollback()
            flash(f"Error: {e}", "error")
        finally:
            cur.close()
        return redirect(url_for('view_courses'))


class TransactionController(Session):
    # ENKAPSULASI terkait transaksi
    # INHERITANCE dari Session untuk akses database
    def generate_pdf_report(self):
        user_session = self.get_user_session()
        if not user_session:
            flash("Please log in to view transactions.", "error")
            return redirect(url_for('login'))

        cur = self.mysql.cursor()
        try:
            cur.execute('''
                SELECT u.fullname, c.name, p.purchase_date
                FROM purchases p
                JOIN users u ON p.user_id = u.id
                JOIN courses c ON p.course_id = c.id
                WHERE p.user_id = %s
            ''', (user_session['user_id'],))
            data = cur.fetchall()
        except Exception as e:
            flash(f"Error fetching transaction data: {e}", "error")
            return redirect(url_for('index'))
        finally:
            cur.close()

        rendered_html = render_template('transaction.html', data=data)

        try:
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            options = {'enable-local-file-access': True, 'quiet': ''}
            pdf = pdfkit.from_string(rendered_html, False, configuration=config, options=options)

            response = Flask.response_class(pdf, content_type='application/pdf')
            response.headers['Content-Disposition'] = f'inline; filename={user_session["fullname"]}-transaction.pdf'
            return response
        except FileNotFoundError:
            flash("Error: wkhtmltopdf not found. Please check the path.", "error")
            return "PDF generation failed. Please check server configuration."
        except Exception as e:
            flash(f"Could not generate PDF: {e}", "error")
            return "PDF generation failed."



class App_Kursus:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = '!@#$%^&*()'

        db_config = Config()

        self.auth_controller = AuthController(db_config)
        self.course_controller = CourseController(db_config)
        self.transaction_controller = TransactionController(db_config)

        self.routes()

    def routes(self):

        @self.app.route('/')
        @self.app.route('/index')
        def index(): return render_template('main.html')

        @self.app.route('/bantuan')
        def bantuan(): return render_template('bantuan.html')

        @self.app.route('/login/', methods=['GET', 'POST'])
        def login(): return self.auth_controller.login()

        @self.app.route('/register/', methods=['GET', 'POST'])
        def register(): return self.auth_controller.register()

        @self.app.route('/reg-ai', methods=['GET', 'POST'])
        def reg_ai(): return self.auth_controller.register(role='Admin/Instruktur')

        @self.app.route('/logout')
        def logout(): return self.auth_controller.logout()

        @self.app.route('/courses/view', methods=['GET', 'POST'])
        def view_or_mulaibelajar(): return self.course_controller.view_or_manage_single_course()

        @self.app.route('/view_courses', methods=['GET'])
        def view_courses(): return self.course_controller.view_all_courses()

        @self.app.route('/courses/buy/<int:course_id>', methods=['POST'])
        def buy_course(course_id): return self.course_controller.buy_course(course_id)

        @self.app.route('/transaction')
        def transaction(): return self.transaction_controller.generate_pdf_report()

    def run(self):
        self.app.run(debug=True)


if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
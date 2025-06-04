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
                role = request.form.get('role')  # Optional role input

                cur = self.con.mysql.cursor()
                try:
                    # Query to check user credentials
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
                        # Store user info in session
                        session['user_id'] = user[0]  # Assuming `id` is the first column
                        session['username'] = user[2]  # Assuming `username` is the third column
                        session['role'] = user[4]  # Assuming `role` is the fifth column
                        flash('Login successful!', 'success')
                        return redirect(url_for('index'))  # Correct endpoint name
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
                role = 'Mahasiswa'  # Hardcoded role for registration

                cur = self.con.mysql.cursor()
                try:
                    # Insert user data into the database
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
                role = request.form['role']  # Role selected from the form

                if role not in ['admin', 'instruktur']:
                    flash('Invalid role selected!', 'error')
                    return redirect(url_for('reg_ai'))

                cur = self.con.mysql.cursor()
                try:
                    # Insert user data into the database
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

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
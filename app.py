from flask import  Flask, flash, redirect, render_template, request, url_for, session
from config import Config
import sqlite3 as sql

class App_Kursus:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = '!@#$%^&*()'
        self.con = Config()
        self.routes()

    def routes(self):
        def query_db(username, password):
            conn = sql.connect('uas_pbo.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            result = cursor.fetchone()
            conn.close()
            return result

        @self.app.route('/testdb')
        def testdb():
            try:
                if self.con.mysql is not None:
                    return "Database connection successful"
            except Exception as e:
                return f"Database connection failed: {e}"

        @self.app.route('/')
        def index():
            return render_template('Main_page.html')

        @self.app.route('/login/')
        def login():
            return render_template('login.html')

        @self.app.route('/login/process', methods=['GET', 'POST'])
        def loginProcess():
            username = request.form['username']
            password = request.form['password']
            data = query_db(username, password)
            if data:
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Wrong username/password. Please check again!', 'failed')                

        @self.app.route('/register/')
        def regiester():
            return render_template('register.html')

        @self.app.route('/register/process', methods=['POST'])
        def registerProcess():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                flash('Registration successful!', 'success')
            return redirect(url_for('login'))

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
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
            return render_template('Main_page.html')

        @self.app.route('/login/', methods=['GET', 'POST'])
        def login():
            return render_template('login.html')

        @self.app.route('/register/', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            return render_template('register.html')

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    portal = App_Kursus()
    portal.run()
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uk46h1g6df3164hd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///odoo.db'
genai.configure(api_key="AIzaSyCINANC0bVIuccsledE2UfHez6YslI4LcA")
model = genai.GenerativeModel("gemini-2.0-flash")

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class BudgetEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    entry_type = db.Column(db.String(10), nullable=False)  


with app.app_context():
    db.create_all()

@app.route('/budgets', methods=['GET', 'POST'])
def budgets():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        category = request.form['category']
        entry_type = request.form['type']

        new_entry = BudgetEntry(
            amount=amount,
            description=description,
            category=category,
            entry_type=entry_type
        )
        db.session.add(new_entry)
        db.session.commit()

        return redirect(url_for('budgets'))

    entries = BudgetEntry.query.all()

  
    total_income = sum(entry.amount for entry in entries if entry.entry_type == 'income')
    total_expenses = sum(entry.amount for entry in entries if entry.entry_type == 'expense')
    balance = total_income - total_expenses

    return render_template('budgets.html',
                         entries=entries, 
                         total_income=total_income, 
                         total_expenses=total_expenses, 
                         balance=balance, title="budgets")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    username = request.form['username']
    password = request.form['password']
    if User.query.filter_by(username=username).first():
        flash('That name’s taken!')
        return redirect(url_for('signup'))
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash('You’re in! Now log in.')
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=current_user.username, title="dashboard")

@app.route('/savings')
def savings():
    return render_template('savings.html', username=current_user.username, title="savings")

@app.route('/ai_insights')
def ai_insights():
    return render_template('ai_insights.html', title="AI Insights")

@app.route('/challenges')
def challenges():
    return render_template('challenges.html', title="challanges")

@app.route('/finance')
def finance():
    return render_template('finance.html', title="finance")

@app.route('/settings')
def settings():
    return render_template('settings.html', title="settings")

@app.route('/help')
def help():
    return render_template('help.html', title="help")

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect(url_for('dashboard'))
    flash('Wrong name or password!')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/ask_gemini", methods=["POST"])
def ask_gemini():
    try:
        data = request.get_json()
        user_input = data.get("query") if data else None
        
        if not user_input:
            return jsonify({"error": "No query provided"}), 400

        response = model.generate_content(user_input)

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/gemini")
def gemini_page():
    return render_template("gemini.html", title="gemini")

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uk46h1g6df3164hd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///odoo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

genai.configure(api_key="AIzaSyCINANC0bVIuccsledE2UfHez6YslI4LcA")
model = genai.GenerativeModel("gemini-2.0-flash")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
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
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Wrong name or password!')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter(
        (Transaction.sender_id == current_user.id) | 
        (Transaction.receiver_id == current_user.id)
    ).order_by(Transaction.timestamp.desc()).limit(10).all()
    
    transaction_data = []
    for t in transactions:
        sender = User.query.get(t.sender_id)
        receiver = User.query.get(t.receiver_id)
        transaction_data.append({
            'timestamp': t.timestamp,
            'amount': t.amount,
            'sender_id': t.sender_id,
            'receiver_id': t.receiver_id,
            'sender_username': sender.username,
            'receiver_username': receiver.username
        })
    
    return render_template('dashboard.html', 
                         username=current_user.username, 
                         transactions=transaction_data,
                         balance=current_user.balance,
                         title="dashboard")

@app.route('/budgets', methods=['GET', 'POST'])
@login_required
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
            entry_type=entry_type,
            user_id=current_user.id
        )
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('budgets'))

    entries = BudgetEntry.query.filter_by(user_id=current_user.id).all()
    total_income = sum(entry.amount for entry in entries if entry.entry_type == 'income')
    total_expenses = sum(entry.amount for entry in entries if entry.entry_type == 'expense')
    budget_balance = total_income - total_expenses

    return render_template('budgets.html',
                         entries=entries,
                         total_income=total_income,
                         total_expenses=total_expenses,
                         balance=budget_balance,
                         title="budgets")

@app.route('/send_payment', methods=['GET', 'POST'])
@login_required
def send_payment():
    if request.method == 'POST':
        receiver_username = request.form['receiver']
        amount = float(request.form['amount'])

        receiver = User.query.filter_by(username=receiver_username).first()
        
        if not receiver:
            flash('Receiver not found')
            return redirect(url_for('send_payment'))
        
        if current_user.id == receiver.id:
            flash('Cannot send money to yourself')
            return redirect(url_for('send_payment'))
        
        if current_user.balance < amount:
            flash('Insufficient funds')
            return redirect(url_for('send_payment'))
        
        if amount <= 0:
            flash('Invalid amount')
            return redirect(url_for('send_payment'))

        transaction = Transaction(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            amount=amount,
            status='completed'
        )
        
        current_user.balance -= amount
        receiver.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Payment sent successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('send_payment.html', title="Send Payment")

@app.route('/add_funds', methods=['GET', 'POST'])
@login_required
def add_funds():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        
        if amount <= 0:
            flash('Invalid amount')
            return redirect(url_for('add_funds'))
        
        current_user.balance += amount
        db.session.commit()
        
        flash('Funds added successfully')
        return redirect(url_for('dashboard'))
    
    return render_template('add_funds.html', title="Add Funds")

@app.route('/savings')
@login_required
def savings():
    return render_template('savings.html', username=current_user.username, title="savings")

@app.route('/challenges')
@login_required
def challenges():
    return render_template('challenges.html', title="challenges", username=current_user.username)

@app.route('/money_match')
@login_required
def money_match():
    return render_template('money_match.html', title="money match")

@app.route('/quize_game')
@login_required
def quize_game():
    return render_template('quize_game.html', title="quize game")

@app.route('/saving_spin_game')
@login_required
def saving_spin_game():
    return render_template('saving_spin_game.html', title="saving spin game")

@app.route('/finance')
@login_required
def finance():
    return render_template('finance.html', title="finance")

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title="settings")

@app.route('/help')
@login_required
def help():
    return render_template('help.html', title="help")

@app.route("/ask_gemini", methods=["POST"])
@login_required
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
@login_required
def gemini_page():
    return render_template("gemini.html", title="gemini")

if __name__ == '__main__':
    app.run(debug=True)
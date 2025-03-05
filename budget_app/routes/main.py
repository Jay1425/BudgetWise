from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Transaction, User  # Add this import

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template("index.html")

@main_bp.route('/dashboard')
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

@main_bp.route('/savings')
@login_required
def savings():
    return render_template('savings.html', username=current_user.username, title="savings")

@main_bp.route('/challenges')
@login_required
def challenges():
    return render_template('challenges.html', title="challenges", username=current_user.username)

@main_bp.route('/money_match')
@login_required
def money_match():
    return render_template('money_match.html', title="money match")

@main_bp.route('/quize_game')
@login_required
def quize_game():
    return render_template('quize_game.html', title="quize game")

@main_bp.route('/saving_spin_game')
@login_required
def saving_spin_game():
    return render_template('saving_spin_game.html', title="saving spin game")

@main_bp.route('/finance')
@login_required
def finance():
    return render_template('finance.html', title="finance")

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title="settings")

@main_bp.route('/help')
@login_required
def help():
    return render_template('help.html', title="help")
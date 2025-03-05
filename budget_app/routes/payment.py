from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import User, Transaction
from .. import db

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/send_payment', methods=['GET', 'POST'])
@login_required
def send_payment():
    if request.method == 'POST':
        receiver_username = request.form['receiver']
        amount = float(request.form['amount'])

        receiver = User.query.filter_by(username=receiver_username).first()
        
        if not receiver:
            flash('Receiver not found')
            return redirect(url_for('payment.send_payment'))
        
        if current_user.id == receiver.id:
            flash('Cannot send money to yourself')
            return redirect(url_for('payment.send_payment'))
        
        if current_user.balance < amount:
            flash('Insufficient funds')
            return redirect(url_for('payment.send_payment'))
        
        if amount <= 0:
            flash('Invalid amount')
            return redirect(url_for('payment.send_payment'))

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
        return redirect(url_for('main.dashboard'))
    
    return render_template('send_payment.html', title="Send Payment")

@payment_bp.route('/add_funds', methods=['GET', 'POST'])
@login_required
def add_funds():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        
        if amount <= 0:
            flash('Invalid amount')
            return redirect(url_for('payment.add_funds'))
        
        current_user.balance += amount
        db.session.commit()
        
        flash('Funds added successfully')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_funds.html', title="Add Funds")
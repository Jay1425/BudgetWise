from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..models import BudgetEntry
from .. import db

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budgets', methods=['GET', 'POST'])
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
        return redirect(url_for('budget.budgets'))

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
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db
from models.expense import Expense

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/expenses')
@login_required
def expense_list():
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot access Operational Expenses.', 'danger')
        return redirect(url_for('main.dashboard'))

    category_filter = request.args.get('category', '')
    month_filter = request.args.get('month', '')

    query = Expense.query

    if category_filter:
        query = query.filter(Expense.category == category_filter)
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            query = query.filter(
                func.extract('year', Expense.date) == year,
                func.extract('month', Expense.date) == month
            )
        except Exception:
            pass

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()
    total_expense = sum(e.amount for e in expenses)

    # Category-wise breakdown
    categories = [
        'Feed', 'Veterinary & Medical', 'Maintenance & Repairs',
        'Labor & Wages', 'Utilities & Electricity', 'Equipment & Machinery',
        'Fuel & Transport', 'Miscellaneous'
    ]
    
    category_totals = {}
    for cat in categories:
        cat_sum = sum(e.amount for e in expenses if e.category == cat)
        if cat_sum > 0:
            category_totals[cat] = round(cat_sum, 2)

    return render_template(
        'expenses.html',
        expenses=expenses,
        categories=categories,
        category_totals=category_totals,
        total_expense=round(total_expense, 2),
        selected_category=category_filter,
        selected_month=month_filter,
        today=date.today().strftime('%Y-%m-%d')
    )

@expense_bp.route('/expenses/add', methods=['POST'])
@login_required
def add_expense():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Miscellaneous')
    amount_str = request.form.get('amount', '0')
    date_str = request.form.get('date', '')
    paid_to = request.form.get('paid_to', '').strip()
    payment_method = request.form.get('payment_method', 'Cash')
    receipt_number = request.form.get('receipt_number', '').strip()
    description = request.form.get('description', '').strip()

    if not title or not amount_str:
        flash('Title and Amount are required.', 'danger')
        return redirect(url_for('expense.expense_list'))

    try:
        amount = float(amount_str)
        exp_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

        exp = Expense(
            title=title,
            category=category,
            amount=amount,
            date=exp_date,
            paid_to=paid_to,
            payment_method=payment_method,
            receipt_number=receipt_number,
            description=description
        )
        db.session.add(exp)
        db.session.commit()
        flash(f'Expense of ₹{amount:.2f} ({title}) recorded.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding expense: {str(e)}', 'danger')

    return redirect(url_for('expense.expense_list'))

@expense_bp.route('/expenses/delete/<int:id>', methods=['POST'])
@login_required
def delete_expense(id):
    exp = Expense.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    flash('Expense record deleted.', 'info')
    return redirect(url_for('expense.expense_list'))

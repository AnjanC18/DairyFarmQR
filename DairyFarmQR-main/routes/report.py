from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from models import db
from models.animal import Animal
from models.milk import MilkProduction
from models.expense import Expense

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports')
@login_required
def reports():
    from flask import redirect, url_for, flash
    from flask_login import current_user
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot access Farm Reports & Financial Analytics.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Date range default: Last 30 days
    today = date.today()
    start_default = today - timedelta(days=29)

    start_str = request.args.get('start_date', start_default.strftime('%Y-%m-%d'))
    end_str = request.args.get('end_date', today.strftime('%Y-%m-%d'))

    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
    except Exception:
        start_date = start_default

    try:
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    except Exception:
        end_date = today

    # Fetch milk records in range
    milk_query = MilkProduction.query.filter(MilkProduction.date >= start_date, MilkProduction.date <= end_date)
    milk_records = milk_query.all()

    total_milk_qty = round(sum(r.quantity_liters for r in milk_records), 2)
    total_milk_revenue = round(sum(r.total_amount for r in milk_records), 2)
    avg_daily_milk = round(total_milk_qty / max((end_date - start_date).days + 1, 1), 2)
    avg_fat = round(sum(r.fat_percentage for r in milk_records) / len(milk_records), 2) if milk_records else 0.0

    # Fetch expenses in range
    expense_query = Expense.query.filter(Expense.date >= start_date, Expense.date <= end_date)
    expense_records = expense_query.all()
    total_expense = round(sum(e.amount for e in expense_records), 2)

    net_profit = round(total_milk_revenue - total_expense, 2)

    # Day by day trend for Chart.js
    num_days = (end_date - start_date).days + 1
    # Cap daily breakdown points if range is too large
    step = max(1, num_days // 30)
    
    trend_dates = []
    trend_milk = []
    trend_revenue = []
    trend_expense = []

    curr = start_date
    while curr <= end_date:
        d_str = curr.strftime('%d %b')
        m_records = [r for r in milk_records if r.date == curr]
        e_records = [e for e in expense_records if e.date == curr]

        d_milk = sum(r.quantity_liters for r in m_records)
        d_rev = sum(r.total_amount for r in m_records)
        d_exp = sum(e.amount for e in e_records)

        trend_dates.append(d_str)
        trend_milk.append(round(d_milk, 2))
        trend_revenue.append(round(d_rev, 2))
        trend_expense.append(round(d_exp, 2))

        curr += timedelta(days=1)

    # Top Yielding Cattle
    animal_yields = {}
    for r in milk_records:
        animal_yields[r.animal_id] = animal_yields.get(r.animal_id, 0.0) + r.quantity_liters

    sorted_animals = sorted(animal_yields.items(), key=lambda x: x[1], reverse=True)[:5]
    top_animals = []
    top_animal_labels = []
    top_animal_data = []

    for a_id, qty in sorted_animals:
        anim = db.session.get(Animal, a_id)
        if anim:
            top_animals.append({
                'animal': anim,
                'total_yield': round(qty, 2),
                'avg_daily': round(qty / max(num_days, 1), 2)
            })
            top_animal_labels.append(f"{anim.tag_number} ({anim.name or anim.breed})")
            top_animal_data.append(round(qty, 2))

    # Category breakdown for expense pie chart
    category_map = {}
    for e in expense_records:
        category_map[e.category] = category_map.get(e.category, 0.0) + e.amount
    
    expense_categories = list(category_map.keys())
    expense_cat_amounts = [round(v, 2) for v in category_map.values()]

    return render_template(
        'reports.html',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        total_milk_qty=total_milk_qty,
        total_milk_revenue=total_milk_revenue,
        avg_daily_milk=avg_daily_milk,
        avg_fat=avg_fat,
        total_expense=total_expense,
        net_profit=net_profit,
        trend_dates=trend_dates,
        trend_milk=trend_milk,
        trend_revenue=trend_revenue,
        trend_expense=trend_expense,
        top_animals=top_animals,
        top_animal_labels=top_animal_labels,
        top_animal_data=top_animal_data,
        expense_categories=expense_categories,
        expense_cat_amounts=expense_cat_amounts
    )

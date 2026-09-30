from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from sqlalchemy import func
from models import db
from models.animal import Animal
from models.milk import MilkProduction
from models.feed import FeedInventory
from models.vaccination import Vaccination
from models.expense import Expense

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    start_of_month = date(today.year, today.month, 1)

    # Animal metrics
    total_animals = Animal.query.count()
    milking_animals = Animal.query.filter_by(milking_status='Milking').count()
    dry_animals = Animal.query.filter_by(milking_status='Dry').count()
    pregnant_animals = Animal.query.filter_by(milking_status='Pregnant').count()
    sick_animals = Animal.query.filter_by(health_status='Under Treatment').count()

    # Today's Milk
    today_records = MilkProduction.query.filter_by(date=today).all()
    today_milk_qty = round(sum(r.quantity_liters for r in today_records), 2)
    today_milk_rev = round(sum(r.total_amount for r in today_records), 2)

    # 7-day milk trend data for Chart.js
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    chart_dates = [d.strftime('%d %b') for d in last_7_days]
    chart_milk_data = []
    chart_morning_data = []
    chart_evening_data = []

    for d in last_7_days:
        day_records = MilkProduction.query.filter_by(date=d).all()
        day_total = sum(r.quantity_liters for r in day_records)
        day_morn = sum(r.quantity_liters for r in day_records if r.session == 'Morning')
        day_eve = sum(r.quantity_liters for r in day_records if r.session == 'Evening')
        
        chart_milk_data.append(round(day_total, 2))
        chart_morning_data.append(round(day_morn, 2))
        chart_evening_data.append(round(day_eve, 2))

    # Month to date revenue vs expense
    month_milk_revenue = db.session.query(func.sum(MilkProduction.total_amount))\
        .filter(MilkProduction.date >= start_of_month, MilkProduction.date <= today).scalar() or 0.0

    month_expenses = db.session.query(func.sum(Expense.amount))\
        .filter(Expense.date >= start_of_month, Expense.date <= today).scalar() or 0.0

    net_profit = round(month_milk_revenue - month_expenses, 2)

    # Low stock alerts
    low_feed_items = [f for f in FeedInventory.query.all() if f.is_low_stock]

    # Upcoming / Overdue vaccinations
    all_vaccines = Vaccination.query.all()
    for v in all_vaccines:
        v.update_status()
    db.session.commit()

    urgent_vaccines = Vaccination.query.filter(
        (Vaccination.status == 'Overdue') | 
        ((Vaccination.status == 'Upcoming') & (Vaccination.next_due_date <= today + timedelta(days=7)))
    ).order_by(Vaccination.next_due_date.asc()).limit(5).all()

    # Recent milk records
    recent_milk = MilkProduction.query.order_by(MilkProduction.date.desc(), MilkProduction.id.desc()).limit(7).all()

    return render_template(
        'dashboard.html',
        total_animals=total_animals,
        milking_animals=milking_animals,
        dry_animals=dry_animals,
        pregnant_animals=pregnant_animals,
        sick_animals=sick_animals,
        today_milk_qty=today_milk_qty,
        today_milk_rev=today_milk_rev,
        month_milk_revenue=round(month_milk_revenue, 2),
        month_expenses=round(month_expenses, 2),
        net_profit=net_profit,
        chart_dates=chart_dates,
        chart_milk_data=chart_milk_data,
        chart_morning_data=chart_morning_data,
        chart_evening_data=chart_evening_data,
        low_feed_items=low_feed_items,
        urgent_vaccines=urgent_vaccines,
        recent_milk=recent_milk
    )

from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.feed import FeedInventory, FeedConsumption

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/feed')
@login_required
def feed_list():
    feeds = FeedInventory.query.order_by(FeedInventory.category, FeedInventory.feed_name).all()
    consumptions = FeedConsumption.query.order_by(FeedConsumption.date.desc(), FeedConsumption.id.desc()).limit(20).all()

    total_stock_value = sum(f.stock_value for f in feeds)
    low_stock_count = sum(1 for f in feeds if f.is_low_stock)

    return render_template(
        'feed.html',
        feeds=feeds,
        consumptions=consumptions,
        total_stock_value=round(total_stock_value, 2),
        low_stock_count=low_stock_count,
        today=date.today().strftime('%Y-%m-%d')
    )

@feed_bp.route('/feed/add-stock', methods=['POST'])
@login_required
def add_stock():
    feed_name = request.form.get('feed_name', '').strip()
    category = request.form.get('category', 'Concentrate')
    quantity = request.form.get('quantity', '0')
    unit = request.form.get('unit', 'kg')
    unit_cost = request.form.get('unit_cost', '0')
    min_threshold = request.form.get('minimum_threshold', '50')
    supplier = request.form.get('supplier', '').strip()

    if not feed_name:
        flash('Feed name is required.', 'danger')
        return redirect(url_for('feed.feed_list'))

    try:
        qty_val = float(quantity)
        cost_val = float(unit_cost)
        min_val = float(min_threshold)

        # Check if already exists to top-up stock
        existing = FeedInventory.query.filter(FeedInventory.feed_name.ilike(feed_name)).first()
        if existing:
            existing.current_stock += qty_val
            existing.unit_cost = cost_val if cost_val > 0 else existing.unit_cost
            existing.minimum_threshold = min_val
            existing.supplier = supplier or existing.supplier
            existing.last_restocked = date.today()
            flash(f'Stock updated: Added {qty_val} {unit} to {existing.feed_name}. Current total: {existing.current_stock} {unit}.', 'success')
        else:
            new_feed = FeedInventory(
                feed_name=feed_name,
                category=category,
                current_stock=qty_val,
                unit=unit,
                unit_cost=cost_val,
                minimum_threshold=min_val,
                supplier=supplier,
                last_restocked=date.today()
            )
            db.session.add(new_feed)
            flash(f'New feed "{feed_name}" added to inventory with {qty_val} {unit} in stock.', 'success')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding feed stock: {str(e)}', 'danger')

    return redirect(url_for('feed.feed_list'))

@feed_bp.route('/feed/log-consumption', methods=['POST'])
@login_required
def log_consumption():
    feed_id = request.form.get('feed_id')
    date_str = request.form.get('date', '')
    quantity_used = request.form.get('quantity_used', '0')
    group_or_animal = request.form.get('group_or_animal', 'All Milking Cattle')

    if not feed_id or not quantity_used:
        flash('Please select feed and specify quantity used.', 'danger')
        return redirect(url_for('feed.feed_list'))

    feed = FeedInventory.query.get_or_404(int(feed_id))
    try:
        qty = float(quantity_used)
        if qty <= 0:
            flash('Quantity must be greater than 0.', 'danger')
            return redirect(url_for('feed.feed_list'))

        if feed.current_stock < qty:
            flash(f'Insufficient stock! Current stock of {feed.feed_name} is only {feed.current_stock} {feed.unit}.', 'warning')
            return redirect(url_for('feed.feed_list'))

        log_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        cost = round(qty * feed.unit_cost, 2)

        # Deduct from stock
        feed.current_stock -= qty

        consumption = FeedConsumption(
            feed_id=feed.id,
            date=log_date,
            quantity_used=qty,
            group_or_animal=group_or_animal,
            cost=cost,
            recorded_by=current_user.full_name
        )
        db.session.add(consumption)
        db.session.commit()

        flash(f'Logged feeding: {qty} {feed.unit} of {feed.feed_name} (Cost: ₹{cost:.2f}). Remaining: {feed.current_stock} {feed.unit}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error logging feed consumption: {str(e)}', 'danger')

    return redirect(url_for('feed.feed_list'))

@feed_bp.route('/feed/delete/<int:id>', methods=['POST'])
@login_required
def delete_feed(id):
    feed = FeedInventory.query.get_or_404(id)
    db.session.delete(feed)
    db.session.commit()
    flash('Feed item deleted.', 'info')
    return redirect(url_for('feed.feed_list'))

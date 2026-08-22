from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.animal import Animal
from models.milk import MilkProduction

milk_bp = Blueprint('milk', __name__)

@milk_bp.route('/milk')
@login_required
def milk_list():
    date_filter_str = request.args.get('date', '')
    session_filter = request.args.get('session', '')
    animal_filter = request.args.get('animal_id', '')

    query = MilkProduction.query

    if date_filter_str:
        try:
            d = datetime.strptime(date_filter_str, '%Y-%m-%d').date()
            query = query.filter(MilkProduction.date == d)
        except ValueError:
            pass
    if session_filter:
        query = query.filter(MilkProduction.session == session_filter)
    if animal_filter:
        query = query.filter(MilkProduction.animal_id == int(animal_filter))

    records = query.order_by(MilkProduction.date.desc(), MilkProduction.id.desc()).all()

    # Summary calculations for current filtered view
    total_qty = round(sum(r.quantity_liters for r in records), 2)
    total_revenue = round(sum(r.total_amount for r in records), 2)
    morning_qty = round(sum(r.quantity_liters for r in records if r.session == 'Morning'), 2)
    evening_qty = round(sum(r.quantity_liters for r in records if r.session == 'Evening'), 2)
    avg_fat = round(sum(r.fat_percentage for r in records) / len(records), 2) if records else 0.0

    animals = Animal.query.filter_by(milking_status='Milking').order_by(Animal.tag_number).all()

    return render_template(
        'milk_production.html',
        records=records,
        animals=animals,
        total_qty=total_qty,
        total_revenue=total_revenue,
        morning_qty=morning_qty,
        evening_qty=evening_qty,
        avg_fat=avg_fat,
        selected_date=date_filter_str,
        selected_session=session_filter,
        selected_animal=animal_filter,
        today=date.today().strftime('%Y-%m-%d')
    )

@milk_bp.route('/milk/add', methods=['GET', 'POST'])
@login_required
def add_milk():
    if request.method == 'POST':
        animal_id = request.form.get('animal_id')
        date_str = request.form.get('date', '')
        session = request.form.get('session', 'Morning')
        quantity = request.form.get('quantity_liters', '0')
        fat = request.form.get('fat_percentage', '4.0')
        snf = request.form.get('snf_percentage', '8.5')
        rate = request.form.get('rate_per_liter', '40.0')
        remarks = request.form.get('remarks', '').strip()

        if not animal_id or not quantity:
            flash('Please select an animal and enter milk quantity.', 'danger')
            return redirect(url_for('milk.milk_list'))

        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
            qty_val = float(quantity)
            fat_val = float(fat) if fat else 4.0
            snf_val = float(snf) if snf else 8.5
            rate_val = float(rate) if rate else 40.0

            record = MilkProduction(
                animal_id=int(animal_id),
                date=entry_date,
                session=session,
                quantity_liters=qty_val,
                fat_percentage=fat_val,
                snf_percentage=snf_val,
                rate_per_liter=rate_val,
                recorded_by=current_user.full_name,
                remarks=remarks
            )
            record.calculate_total()

            db.session.add(record)
            db.session.commit()

            animal = db.session.get(Animal, int(animal_id))
            tag = animal.tag_number if animal else ''
            flash(f'Logged {qty_val} L milk for {tag} ({session} session). Total: ₹{record.total_amount:.2f}', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error logging milk entry: {str(e)}', 'danger')

        return redirect(url_for('milk.milk_list'))

    preselect_animal = request.args.get('animal_id')
    animals = Animal.query.order_by(Animal.tag_number).all()
    return render_template('milk_production.html', animals=animals, preselect_animal=preselect_animal, today=date.today().strftime('%Y-%m-%d'))

@milk_bp.route('/milk/quick-entry', methods=['GET', 'POST'])
@login_required
def quick_entry():
    milking_cows = Animal.query.filter_by(milking_status='Milking').order_by(Animal.tag_number).all()
    today_str = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        date_str = request.form.get('entry_date', today_str)
        session = request.form.get('session', 'Morning')
        default_rate = float(request.form.get('default_rate', '40.0') or 40.0)
        entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        count = 0
        total_logged_qty = 0.0

        for animal in milking_cows:
            qty_input = request.form.get(f'qty_{animal.id}', '').strip()
            fat_input = request.form.get(f'fat_{animal.id}', '').strip()
            snf_input = request.form.get(f'snf_{animal.id}', '').strip()

            if qty_input:
                try:
                    qty = float(qty_input)
                    if qty > 0:
                        fat = float(fat_input) if fat_input else 4.0
                        snf = float(snf_input) if snf_input else 8.5
                        
                        rec = MilkProduction(
                            animal_id=animal.id,
                            date=entry_date,
                            session=session,
                            quantity_liters=qty,
                            fat_percentage=fat,
                            snf_percentage=snf,
                            rate_per_liter=default_rate,
                            recorded_by=current_user.full_name,
                            remarks='Batch Entry'
                        )
                        rec.calculate_total()
                        db.session.add(rec)
                        count += 1
                        total_logged_qty += qty
                except ValueError:
                    continue

        db.session.commit()
        flash(f'Batch entry complete: Logged {count} cattle records totaling {total_logged_qty:.2f} L ({session} session).', 'success')
        return redirect(url_for('milk.milk_list'))

    return render_template('quick_milk_entry.html', milking_cows=milking_cows, today=today_str)

@milk_bp.route('/milk/delete/<int:id>', methods=['POST'])
@login_required
def delete_milk(id):
    rec = MilkProduction.query.get_or_404(id)
    db.session.delete(rec)
    db.session.commit()
    flash('Milk record deleted successfully.', 'info')
    return redirect(url_for('milk.milk_list'))

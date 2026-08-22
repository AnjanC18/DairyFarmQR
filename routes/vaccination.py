from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.animal import Animal
from models.vaccination import Vaccination

vaccination_bp = Blueprint('vaccination', __name__)

@vaccination_bp.route('/vaccinations')
@login_required
def vaccination_list():
    # Refresh statuses
    all_vaccines = Vaccination.query.all()
    for v in all_vaccines:
        v.update_status()
    db.session.commit()

    status_filter = request.args.get('status', '')
    animal_filter = request.args.get('animal_id', '')

    query = Vaccination.query

    if status_filter:
        query = query.filter(Vaccination.status == status_filter)
    if animal_filter:
        query = query.filter(Vaccination.animal_id == int(animal_filter))

    vaccinations = query.order_by(Vaccination.next_due_date.asc(), Vaccination.id.desc()).all()
    animals = Animal.query.order_by(Animal.tag_number).all()

    today = date.today()
    overdue_count = sum(1 for v in all_vaccines if v.status == 'Overdue')
    upcoming_count = sum(1 for v in all_vaccines if v.status == 'Upcoming' and v.next_due_date <= today + timedelta(days=14))
    completed_count = sum(1 for v in all_vaccines if v.status == 'Completed')

    return render_template(
        'vaccination.html',
        vaccinations=vaccinations,
        animals=animals,
        selected_status=status_filter,
        selected_animal=animal_filter,
        overdue_count=overdue_count,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        today=today.strftime('%Y-%m-%d')
    )

@vaccination_bp.route('/vaccinations/add', methods=['POST'])
@login_required
def add_vaccination():
    animal_id = request.form.get('animal_id')
    vaccine_name = request.form.get('vaccine_name', '').strip()
    administered_date_str = request.form.get('administered_date', '')
    next_due_date_str = request.form.get('next_due_date', '')
    veterinarian = request.form.get('veterinarian', '').strip()
    status = request.form.get('status', 'Completed')
    remarks = request.form.get('remarks', '').strip()

    if not animal_id or not vaccine_name or not next_due_date_str:
        flash('Animal, Vaccine Name, and Next Due Date are required.', 'danger')
        return redirect(url_for('vaccination.vaccination_list'))

    try:
        administered_date = datetime.strptime(administered_date_str, '%Y-%m-%d').date() if administered_date_str else date.today()
        next_due_date = datetime.strptime(next_due_date_str, '%Y-%m-%d').date()

        vax = Vaccination(
            animal_id=int(animal_id),
            vaccine_name=vaccine_name,
            administered_date=administered_date,
            next_due_date=next_due_date,
            veterinarian=veterinarian,
            status=status,
            remarks=remarks
        )
        vax.update_status()

        db.session.add(vax)
        db.session.commit()

        animal = db.session.get(Animal, int(animal_id))
        tag = animal.tag_number if animal else ''
        flash(f'Vaccination record for {tag} ({vaccine_name}) created successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error saving vaccination: {str(e)}', 'danger')

    return redirect(url_for('vaccination.vaccination_list'))

@vaccination_bp.route('/vaccinations/mark-done/<int:id>', methods=['POST'])
@login_required
def mark_done(id):
    vax = Vaccination.query.get_or_404(id)
    vax.status = 'Completed'
    vax.administered_date = date.today()
    
    # Optionally compute next due date (e.g. 6 months / 180 days by default)
    vax.next_due_date = date.today() + timedelta(days=180)
    db.session.commit()

    flash(f'Vaccination "{vax.vaccine_name}" marked as administered. Next booster set to {vax.next_due_date}.', 'success')
    return redirect(url_for('vaccination.vaccination_list'))

@vaccination_bp.route('/vaccinations/delete/<int:id>', methods=['POST'])
@login_required
def delete_vaccination(id):
    vax = Vaccination.query.get_or_404(id)
    db.session.delete(vax)
    db.session.commit()
    flash('Vaccination record deleted.', 'info')
    return redirect(url_for('vaccination.vaccination_list'))

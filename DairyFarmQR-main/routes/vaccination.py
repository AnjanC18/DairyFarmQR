from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot add vaccination records.', 'danger')
        return redirect(url_for('vaccination.vaccination_list'))

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
            veterinarian=veterinarian or current_user.full_name,
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
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot update vaccination status.', 'danger')
        return redirect(url_for('vaccination.vaccination_list'))

    vax = Vaccination.query.get_or_404(id)
    vax.status = 'Completed'
    vax.administered_date = date.today()
    vax.next_due_date = date.today() + timedelta(days=180)
    vax.veterinarian = current_user.full_name
    db.session.commit()

    flash(f'Vaccination "{vax.vaccine_name}" marked as administered today. Next booster scheduled for {vax.next_due_date.strftime("%d %b %Y")}.', 'success')
    return redirect(request.referrer or url_for('vaccination.vaccination_list'))

@vaccination_bp.route('/api/vaccinations/mark-done/<int:id>', methods=['POST'])
@login_required
def api_mark_done(id):
    if not current_user.is_manager():
        return jsonify({'success': False, 'message': 'Access denied. Only Farm Managers and Admins can mark vaccinations as done.'}), 403

    vax = Vaccination.query.get_or_404(id)
    vax.status = 'Completed'
    vax.administered_date = date.today()
    vax.next_due_date = date.today() + timedelta(days=180)
    vax.veterinarian = current_user.full_name
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Vaccine "{vax.vaccine_name}" marked as DONE on {vax.administered_date.strftime("%d %b %Y")}! Next booster set for {vax.next_due_date.strftime("%d %b %Y")}.',
        'vaccination': {
            'id': vax.id,
            'vaccine_name': vax.vaccine_name,
            'administered_date': vax.administered_date.strftime('%d %b %Y'),
            'next_due_date': vax.next_due_date.strftime('%d %b %Y'),
            'status': vax.status,
            'veterinarian': vax.veterinarian
        }
    })

@vaccination_bp.route('/api/vaccinations/quick-add', methods=['POST'])
@login_required
def api_quick_add():
    if not current_user.is_manager():
        return jsonify({'success': False, 'message': 'Access denied. Only Farm Managers and Admins can log vaccinations.'}), 403

    data = request.get_json() if request.is_json else request.form
    animal_id = data.get('animal_id')
    vaccine_name = data.get('vaccine_name', '').strip()
    next_due_days = int(data.get('next_due_days', 180))
    remarks = data.get('remarks', 'Administered during QR Scan Inspection').strip()

    if not animal_id or not vaccine_name:
        return jsonify({'success': False, 'message': 'Animal ID and Vaccine name are required.'}), 400

    try:
        vax = Vaccination(
            animal_id=int(animal_id),
            vaccine_name=vaccine_name,
            administered_date=date.today(),
            next_due_date=date.today() + timedelta(days=next_due_days),
            veterinarian=current_user.full_name,
            status='Completed',
            remarks=remarks
        )
        db.session.add(vax)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Vaccine "{vaccine_name}" administered & recorded successfully.',
            'vaccination': {
                'id': vax.id,
                'vaccine_name': vax.vaccine_name,
                'administered_date': vax.administered_date.strftime('%d %b %Y'),
                'next_due_date': vax.next_due_date.strftime('%d %b %Y'),
                'status': vax.status,
                'veterinarian': vax.veterinarian
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error logging vaccination: {str(e)}'}), 500

@vaccination_bp.route('/vaccinations/delete/<int:id>', methods=['POST'])
@login_required
def delete_vaccination(id):
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot delete vaccination records.', 'danger')
        return redirect(url_for('vaccination.vaccination_list'))

    vax = Vaccination.query.get_or_404(id)
    db.session.delete(vax)
    db.session.commit()
    flash('Vaccination record deleted.', 'info')
    return redirect(url_for('vaccination.vaccination_list'))

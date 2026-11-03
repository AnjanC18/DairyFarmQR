from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.animal import Animal
from models.treatment import MedicalTreatment

treatment_bp = Blueprint('treatment', __name__)

@treatment_bp.route('/treatments')
@login_required
def treatment_list():
    status_filter = request.args.get('status', '').strip()
    animal_filter = request.args.get('animal_id', '').strip()
    page = request.args.get('page', 1, type=int)

    query = MedicalTreatment.query

    if status_filter:
        query = query.filter(MedicalTreatment.status == status_filter)
    if animal_filter:
        try:
            query = query.filter(MedicalTreatment.animal_id == int(animal_filter))
        except ValueError:
            pass

    pagination = query.order_by(MedicalTreatment.administered_date.desc(), MedicalTreatment.id.desc()).paginate(page=page, per_page=10, error_out=False)
    treatments = pagination.items

    animals = Animal.query.order_by(Animal.tag_number).all()
    under_treatment_count = MedicalTreatment.query.filter_by(status='Under Treatment').count()
    active_withdrawal_count = sum(1 for t in MedicalTreatment.query.filter_by(status='Under Treatment').all() if t.is_in_withdrawal)

    return render_template(
        'treatments.html',
        treatments=treatments,
        pagination=pagination,
        animals=animals,
        selected_status=status_filter,
        selected_animal=animal_filter,
        under_treatment_count=under_treatment_count,
        active_withdrawal_count=active_withdrawal_count,
        today=date.today().strftime('%Y-%m-%d')
    )

@treatment_bp.route('/treatments/add', methods=['POST'])
@login_required
def add_treatment():
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot log medical treatments.', 'danger')
        return redirect(url_for('treatment.treatment_list'))

    animal_id = request.form.get('animal_id')
    diagnosis = request.form.get('diagnosis', '').strip()
    symptoms = request.form.get('symptoms', '').strip()
    treatment_given = request.form.get('treatment_given', '').strip()
    date_str = request.form.get('administered_date', '')
    veterinarian = request.form.get('veterinarian', '').strip()
    withdrawal_days = request.form.get('withdrawal_period_days', '3')
    cost_str = request.form.get('cost', '0.0')
    notes = request.form.get('notes', '').strip()

    if not animal_id or not diagnosis or not treatment_given:
        flash('Animal, diagnosis, and treatment details are required.', 'danger')
        return redirect(url_for('treatment.treatment_list'))

    try:
        adm_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        withdrawal = int(withdrawal_days) if withdrawal_days else 3
        cost = float(cost_str) if cost_str else 0.0

        treatment = MedicalTreatment(
            animal_id=int(animal_id),
            diagnosis=diagnosis,
            symptoms=symptoms,
            treatment_given=treatment_given,
            administered_date=adm_date,
            veterinarian=veterinarian or current_user.full_name,
            withdrawal_period_days=withdrawal,
            status='Under Treatment',
            cost=cost,
            notes=notes
        )
        db.session.add(treatment)

        # Update animal health status to Under Treatment
        animal = db.session.get(Animal, int(animal_id))
        if animal and animal.health_status != 'Under Treatment':
            animal.health_status = 'Under Treatment'

        db.session.commit()
        flash(f'Medical treatment logged for {animal.tag_number if animal else ""}. Milk withdrawal period: {withdrawal} days.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error logging medical treatment: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('treatment.treatment_list'))

@treatment_bp.route('/treatments/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    if not current_user.is_manager():
        flash('Access denied. Only managers can update treatment records.', 'danger')
        return redirect(url_for('treatment.treatment_list'))

    treatment = MedicalTreatment.query.get_or_404(id)
    new_status = request.form.get('status', 'Recovered')
    treatment.status = new_status

    # If marked recovered, check if animal has other active treatments
    animal = treatment.animal
    if animal and new_status == 'Recovered':
        other_active = MedicalTreatment.query.filter(
            MedicalTreatment.animal_id == animal.id,
            MedicalTreatment.id != treatment.id,
            MedicalTreatment.status == 'Under Treatment'
        ).count()
        if other_active == 0:
            animal.health_status = 'Healthy'

    db.session.commit()
    flash(f'Treatment record #{treatment.id} updated to "{new_status}".', 'success')
    return redirect(request.referrer or url_for('treatment.treatment_list'))

@treatment_bp.route('/treatments/<int:id>/delete', methods=['POST'])
@login_required
def delete_treatment(id):
    if not current_user.is_admin():
        flash('Access denied. Only administrators can delete medical treatment records.', 'danger')
        return redirect(url_for('treatment.treatment_list'))

    treatment = MedicalTreatment.query.get_or_404(id)
    db.session.delete(treatment)
    db.session.commit()
    flash('Medical treatment record deleted successfully.', 'success')
    return redirect(url_for('treatment.treatment_list'))

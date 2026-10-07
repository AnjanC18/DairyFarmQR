import os
from flask import Blueprint, render_template, jsonify, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from models import db
from models.animal import Animal
from models.milk import MilkProduction
from models.vaccination import Vaccination
from utils.qr_helper import generate_animal_qr

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/scan-qr')
@login_required
def scan_qr():
    return render_template('scan_qr.html')

@qr_bp.route('/api/qr/lookup/<path:tag_number>')
@login_required
def api_lookup(tag_number):
    tag = tag_number.strip().upper()
    animal = Animal.query.filter((Animal.tag_number == tag) | (Animal.tag_number == tag_number.strip())).first()
    
    if not animal:
        return jsonify({'success': False, 'message': f'No animal found with tag number "{tag}"'}), 404

    # Fetch last milk record
    last_milk = MilkProduction.query.filter_by(animal_id=animal.id).order_by(MilkProduction.date.desc(), MilkProduction.id.desc()).first()
    last_milk_info = {
        'date': last_milk.date.strftime('%d %b %Y') if last_milk else 'N/A',
        'session': last_milk.session if last_milk else 'N/A',
        'qty': f"{last_milk.quantity_liters} L" if last_milk else '0 L'
    } if last_milk else None

    # Fetch vaccinations for this animal
    all_vax = Vaccination.query.filter_by(animal_id=animal.id).order_by(Vaccination.next_due_date.asc(), Vaccination.id.desc()).all()
    vax_list = []
    for v in all_vax:
        v.update_status()
        vax_list.append({
            'id': v.id,
            'vaccine_name': v.vaccine_name,
            'administered_date': v.administered_date.strftime('%d %b %Y') if v.administered_date else 'N/A',
            'next_due_date': v.next_due_date.strftime('%d %b %Y') if v.next_due_date else 'N/A',
            'status': v.status,
            'is_overdue': v.is_overdue,
            'veterinarian': v.veterinarian or 'Farm Vet',
            'remarks': v.remarks or ''
        })

    return jsonify({
        'success': True,
        'is_manager': current_user.is_manager(),
        'animal': {
            'id': animal.id,
            'tag_number': animal.tag_number,
            'name': animal.name or 'Unnamed',
            'species': animal.species,
            'breed': animal.breed,
            'gender': animal.gender,
            'age': animal.age,
            'milking_status': animal.milking_status,
            'health_status': animal.health_status,
            'today_milk': f"{animal.today_milk} L",
            'total_milk': f"{animal.total_milk} L",
            'qr_image_url': f"/static/qr_codes/{animal.qr_code_image}" if animal.qr_code_image else None,
            'last_milk': last_milk_info,
            'vaccinations': vax_list
        }
    })

@qr_bp.route('/qr/download/<int:animal_id>')
@login_required
def download_qr(animal_id):
    animal = Animal.query.get_or_404(animal_id)
    if not animal.qr_code_image:
        animal.qr_code_image = generate_animal_qr(animal.tag_number)
        db.session.commit()

    qr_folder = current_app.config['QR_FOLDER']
    if not os.path.exists(os.path.join(qr_folder, animal.qr_code_image)):
        generate_animal_qr(animal.tag_number)

    return send_from_directory(
        qr_folder,
        animal.qr_code_image,
        as_attachment=True,
        download_name=f"QR_{animal.tag_number}.png"
    )

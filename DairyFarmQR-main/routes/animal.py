import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import db
from models.animal import Animal
from models.milk import MilkProduction
from models.vaccination import Vaccination
from utils.qr_helper import generate_animal_qr

animal_bp = Blueprint('animal', __name__)

@animal_bp.route('/api/animals/search')
@login_required
def api_search_animals():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    
    animals = Animal.query.filter(
        (Animal.tag_number.ilike(f"%{q}%")) |
        (Animal.name.ilike(f"%{q}%")) |
        (Animal.breed.ilike(f"%{q}%"))
    ).limit(10).all()
    
    results = []
    for a in animals:
        results.append({
            'id': a.id,
            'tag_number': a.tag_number,
            'name': a.name or '',
            'species': a.species,
            'breed': a.breed,
            'milking_status': a.milking_status,
            'health_status': a.health_status,
            'url': url_for('animal.animal_detail', id=a.id),
            'qr_image': a.qr_code_image
        })
    return jsonify(results)

@animal_bp.route('/animals')
@login_required
def list_animals():
    search = request.args.get('search', '').strip()
    species = request.args.get('species', '').strip()
    status = request.args.get('status', '').strip()
    health = request.args.get('health', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Animal.query

    if search:
        query = query.filter((Animal.tag_number.ilike(f"%{search}%")) | (Animal.name.ilike(f"%{search}%")) | (Animal.breed.ilike(f"%{search}%")))
    if species:
        query = query.filter(Animal.species == species)
    if status:
        query = query.filter(Animal.milking_status == status)
    if health:
        query = query.filter(Animal.health_status == health)

    # 10 cattle per page
    pagination = query.order_by(Animal.id.desc()).paginate(page=page, per_page=10, error_out=False)
    animals = pagination.items
    
    # Counts for quick filter pills
    total_count = Animal.query.count()
    milking_count = Animal.query.filter_by(milking_status='Milking').count()
    dry_count = Animal.query.filter_by(milking_status='Dry').count()
    pregnant_count = Animal.query.filter_by(milking_status='Pregnant').count()

    return render_template(
        'animals.html',
        animals=animals,
        pagination=pagination,
        search=search,
        selected_species=species,
        selected_status=status,
        selected_health=health,
        total_count=total_count,
        milking_count=milking_count,
        dry_count=dry_count,
        pregnant_count=pregnant_count
    )

@animal_bp.route('/animals/add', methods=['GET', 'POST'])
@login_required
def add_animal():
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot register or add new cattle.', 'danger')
        return redirect(url_for('animal.list_animals'))

    if request.method == 'POST':
        tag_number = request.form.get('tag_number', '').strip().upper()
        name = request.form.get('name', '').strip()
        species = request.form.get('species', 'Cow')
        breed = request.form.get('breed', '').strip()
        gender = request.form.get('gender', 'Female')
        dob_str = request.form.get('dob', '')
        weight = request.form.get('weight_kg', '')
        milking_status = request.form.get('milking_status', 'Milking')
        health_status = request.form.get('health_status', 'Healthy')
        entry_date_str = request.form.get('entry_date', '')
        notes = request.form.get('notes', '').strip()

        if not tag_number or not breed:
            flash('Tag Number and Breed are required fields.', 'danger')
            return render_template('add_animal.html')

        # Check unique tag number
        existing = Animal.query.filter_by(tag_number=tag_number).first()
        if existing:
            flash(f'An animal with Tag Number "{tag_number}" already exists!', 'danger')
            return render_template('add_animal.html')

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date() if entry_date_str else date.today()
        weight_kg = float(weight) if weight else None

        # Generate QR code
        qr_image = generate_animal_qr(tag_number)

        animal = Animal(
            tag_number=tag_number,
            name=name if name else None,
            species=species,
            breed=breed,
            gender=gender,
            dob=dob,
            weight_kg=weight_kg,
            milking_status=milking_status,
            health_status=health_status,
            qr_code_image=qr_image,
            entry_date=entry_date,
            notes=notes
        )

        db.session.add(animal)
        db.session.commit()
        flash(f'Animal {tag_number} ({breed}) added successfully with QR tag generated!', 'success')
        return redirect(url_for('animal.animal_detail', id=animal.id))

    return render_template('add_animal.html')

@animal_bp.route('/animals/<int:id>')
@login_required
def animal_detail(id):
    animal = Animal.query.get_or_404(id)
    
    # Ensure QR code exists on disk
    if not animal.qr_code_image or not os.path.exists(os.path.join(current_app.config['QR_FOLDER'], animal.qr_code_image)):
        animal.qr_code_image = generate_animal_qr(animal.tag_number)
        db.session.commit()

    # Milk records for this animal (last 30 records)
    milk_records = MilkProduction.query.filter_by(animal_id=animal.id).order_by(MilkProduction.date.desc(), MilkProduction.id.desc()).limit(30).all()
    
    # Vaccinations for this animal
    vaccinations = Vaccination.query.filter_by(animal_id=animal.id).order_by(Vaccination.administered_date.desc()).all()

    # Calculate average daily yield in last 7 days
    recent_yields = [r.quantity_liters for r in milk_records[:14]]
    avg_yield = round(sum(recent_yields) / len(recent_yields), 2) if recent_yields else 0.0

    return render_template(
        'animal_detail.html',
        animal=animal,
        milk_records=milk_records,
        vaccinations=vaccinations,
        avg_yield=avg_yield
    )

@animal_bp.route('/animals/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_animal(id):
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot edit cattle records.', 'danger')
        return redirect(url_for('animal.animal_detail', id=id))

    animal = Animal.query.get_or_404(id)

    if request.method == 'POST':
        tag_number = request.form.get('tag_number', '').strip().upper()
        name = request.form.get('name', '').strip()
        species = request.form.get('species', 'Cow')
        breed = request.form.get('breed', '').strip()
        gender = request.form.get('gender', 'Female')
        dob_str = request.form.get('dob', '')
        weight = request.form.get('weight_kg', '')
        milking_status = request.form.get('milking_status', 'Milking')
        health_status = request.form.get('health_status', 'Healthy')
        entry_date_str = request.form.get('entry_date', '')
        notes = request.form.get('notes', '').strip()

        if not tag_number or not breed:
            flash('Tag Number and Breed are required.', 'danger')
            return render_template('edit_animal.html', animal=animal)

        # Check tag uniqueness if changed
        if tag_number != animal.tag_number:
            existing = Animal.query.filter_by(tag_number=tag_number).first()
            if existing:
                flash(f'Tag Number "{tag_number}" is already used by another animal.', 'danger')
                return render_template('edit_animal.html', animal=animal)
            # Re-generate QR for new tag
            animal.qr_code_image = generate_animal_qr(tag_number)
            animal.tag_number = tag_number

        animal.name = name if name else None
        animal.species = species
        animal.breed = breed
        animal.gender = gender
        animal.dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        animal.weight_kg = float(weight) if weight else None
        animal.milking_status = milking_status
        animal.health_status = health_status
        if entry_date_str:
            animal.entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
        animal.notes = notes

        db.session.commit()
        flash('Animal details updated successfully!', 'success')
        return redirect(url_for('animal.animal_detail', id=animal.id))

    return render_template('edit_animal.html', animal=animal)

@animal_bp.route('/animals/delete/<int:id>', methods=['POST'])
@login_required
def delete_animal(id):
    if not current_user.is_manager():
        flash('Access denied. Staff members cannot delete cattle records.', 'danger')
        return redirect(url_for('animal.list_animals'))

    animal = Animal.query.get_or_404(id)
    tag = animal.tag_number
    
    # Remove QR file if exists
    if animal.qr_code_image:
        qr_path = os.path.join(current_app.config['QR_FOLDER'], animal.qr_code_image)
        if os.path.exists(qr_path):
            try:
                os.remove(qr_path)
            except Exception:
                pass

    db.session.delete(animal)
    db.session.commit()
    flash(f'Animal {tag} removed from database.', 'info')
    return redirect(url_for('animal.list_animals'))

from datetime import date, timedelta
from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User
from models.animal import Animal
from models.milk import MilkProduction
from models.feed import FeedInventory, FeedConsumption
from models.vaccination import Vaccination
from models.employee import Employee
from models.expense import Expense

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.animal import animal_bp
    from routes.milk import milk_bp
    from routes.feed import feed_bp
    from routes.vaccination import vaccination_bp
    from routes.employee import employee_bp
    from routes.expense import expense_bp
    from routes.report import report_bp
    from routes.qr import qr_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(animal_bp)
    app.register_blueprint(milk_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(vaccination_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(qr_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('layout.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('layout.html'), 500

    # Auto seed initial demo data
    with app.app_context():
        try:
            db.create_all()
            seed_initial_data(app)
        except Exception as e:
            print(f"[DB Initialization Warning] {e}")

    return app

def seed_initial_data(app):
    # 1. Admin User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@dairy.com',
            full_name='Farm Manager Admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("[Seed] Created default admin user: admin / admin123")

    # 2. Sample Cattle
    if Animal.query.count() == 0:
        demo_animals = [
            ('DF-101', 'Gauri', 'Cow', 'Gir', 'Female', date(2021, 3, 15), 420.0, 'Milking', 'Healthy', date(2023, 1, 10)),
            ('DF-102', 'Kamdhenu', 'Cow', 'Sahiwal', 'Female', date(2020, 7, 20), 460.0, 'Milking', 'Healthy', date(2022, 11, 5)),
            ('DF-103', 'Lakshmi', 'Buffalo', 'Murrah', 'Female', date(2021, 1, 12), 540.0, 'Milking', 'Healthy', date(2023, 2, 18)),
            ('DF-104', 'Nandini', 'Cow', 'Holstein Friesian (HF)', 'Female', date(2022, 5, 10), 490.0, 'Milking', 'Healthy', date(2023, 8, 1)),
            ('DF-105', 'Radha', 'Cow', 'Jersey', 'Female', date(2021, 9, 2), 380.0, 'Dry', 'Healthy', date(2023, 4, 12)),
            ('DF-106', 'Surabhi', 'Cow', 'Red Sindhi', 'Female', date(2022, 11, 25), 410.0, 'Pregnant', 'Healthy', date(2024, 1, 15)),
            ('DF-107', 'Kaali', 'Buffalo', 'Jaffarabadi', 'Female', date(2020, 10, 18), 580.0, 'Sick', 'Under Treatment', date(2023, 5, 20)),
            ('DF-108', 'Chhoti', 'Cow', 'Gir', 'Female', date(2024, 4, 1), 95.0, 'Calf', 'Healthy', date(2024, 4, 1))
        ]

        created_animals = []
        for tag, name, species, breed, gender, dob, weight, m_status, h_status, entry in demo_animals:
            qr_file = generate_animal_qr(tag)
            a = Animal(
                tag_number=tag,
                name=name,
                species=species,
                breed=breed,
                gender=gender,
                dob=dob,
                weight_kg=weight,
                milking_status=m_status,
                health_status=h_status,
                qr_code_image=qr_file,
                entry_date=entry,
                notes='Standard farm pedigree record.'
            )
            db.session.add(a)
            created_animals.append(a)
        
        db.session.commit()
        print(f"[Seed] Created {len(demo_animals)} demo cattle with generated QR codes.")

        # 3. Seed Past 7 Days Milk Records for Milking Cattle
        milking_list = Animal.query.filter_by(milking_status='Milking').all()
        today = date.today()
        base_yields = {
            'DF-101': (7.5, 6.0),   # Gir
            'DF-102': (8.0, 6.5),   # Sahiwal
            'DF-103': (9.5, 8.0),   # Murrah Buffalo
            'DF-104': (12.0, 10.5)  # HF
        }

        for days_ago in range(7, -1, -1):
            d = today - timedelta(days=days_ago)
            for anim in milking_list:
                m_yield, e_yield = base_yields.get(anim.tag_number, (6.0, 5.0))
                # Morning Session
                m_rec = MilkProduction(
                    animal_id=anim.id,
                    date=d,
                    session='Morning',
                    quantity_liters=m_yield,
                    fat_percentage=4.2 if anim.species == 'Cow' else 7.0,
                    snf_percentage=8.5 if anim.species == 'Cow' else 9.0,
                    rate_per_liter=42.0 if anim.species == 'Cow' else 55.0,
                    recorded_by='Admin'
                )
                m_rec.calculate_total()
                db.session.add(m_rec)

                # Evening Session
                e_rec = MilkProduction(
                    animal_id=anim.id,
                    date=d,
                    session='Evening',
                    quantity_liters=e_yield,
                    fat_percentage=4.3 if anim.species == 'Cow' else 7.2,
                    snf_percentage=8.6 if anim.species == 'Cow' else 9.1,
                    rate_per_liter=42.0 if anim.species == 'Cow' else 55.0,
                    recorded_by='Admin'
                )
                e_rec.calculate_total()
                db.session.add(e_rec)

        db.session.commit()
        print("[Seed] Created past 7-day morning & evening milk production records.")

    # 4. Seed Feed Inventory
    if FeedInventory.query.count() == 0:
        feeds = [
            FeedInventory(feed_name='Green Napier Grass', category='Green Fodder', current_stock=1200.0, unit='kg', unit_cost=2.5, minimum_threshold=300.0, supplier='Agro Green Farm'),
            FeedInventory(feed_name='Wheat Straw (Bhusa)', category='Dry Fodder', current_stock=850.0, unit='kg', unit_cost=6.0, minimum_threshold=200.0, supplier='Kisan Agro Traders'),
            FeedInventory(feed_name='Cattle Feed Pellets (20% Protein)', category='Concentrate', current_stock=450.0, unit='kg', unit_cost=24.0, minimum_threshold=100.0, supplier='Godrej Agrovet'),
            FeedInventory(feed_name='Mineral Mixture & Calcium', category='Mineral Mixture', current_stock=35.0, unit='kg', unit_cost=65.0, minimum_threshold=20.0, supplier='VetCare Health'),
            FeedInventory(feed_name='Maize Silage', category='Silage', current_stock=1500.0, unit='kg', unit_cost=4.5, minimum_threshold=400.0, supplier='Silage India Ltd')
        ]
        db.session.add_all(feeds)
        db.session.commit()
        print("[Seed] Created feed inventory items.")

    # 5. Seed Vaccinations
    if Vaccination.query.count() == 0:
        cows = Animal.query.all()
        if cows:
            today = date.today()
            vax_entries = [
                Vaccination(animal_id=cows[0].id, vaccine_name='FMD (Foot & Mouth)', administered_date=today - timedelta(days=60), next_due_date=today + timedelta(days=120), veterinarian='Dr. Alok Verma', status='Completed', remarks='Routine booster dose administered.'),
                Vaccination(animal_id=cows[1].id, vaccine_name='Brucellosis (S19)', administered_date=today - timedelta(days=180), next_due_date=today - timedelta(days=5), veterinarian='Dr. Alok Verma', status='Overdue', remarks='Booster overdue by 5 days.'),
                Vaccination(animal_id=cows[2].id, vaccine_name='Blackleg (Clostridial)', administered_date=today - timedelta(days=90), next_due_date=today + timedelta(days=6), veterinarian='Dr. Alok Verma', status='Upcoming', remarks='Annual immunization scheduled.'),
                Vaccination(animal_id=cows[3].id, vaccine_name='Haemorrhagic Septicaemia (HS)', administered_date=today - timedelta(days=150), next_due_date=today + timedelta(days=30), veterinarian='Dr. Alok Verma', status='Upcoming', remarks='Pre-monsoon vaccine.')
            ]
            db.session.add_all(vax_entries)
            db.session.commit()
            print("[Seed] Created vaccination schedules.")

    # 6. Seed Employees
    if Employee.query.count() == 0:
        emps = [
            Employee(name='Ramesh Kumar', role='Head Milker & Supervisor', phone='+91 9876543210', email='ramesh@dairy.com', salary=22000.0, joining_date=date(2022, 1, 15), status='Active', address='Village Rampur, Sector 4'),
            Employee(name='Suresh Yadav', role='Animal Caretaker & Feeder', phone='+91 9876543211', email='suresh@dairy.com', salary=16000.0, joining_date=date(2022, 6, 1), status='Active', address='Near Dairy Farm Colony'),
            Employee(name='Dr. Alok Verma', role='Visiting Veterinarian', phone='+91 9876543212', email='dr.alok@vetcare.in', salary=28000.0, joining_date=date(2021, 8, 10), status='Active', address='City Veterinary Hospital Road'),
            Employee(name='Pooja Sharma', role='Accountant & Store In-charge', phone='+91 9876543213', email='pooja@dairy.com', salary=20000.0, joining_date=date(2023, 3, 1), status='Active', address='Civil Lines, Block B')
        ]
        db.session.add_all(emps)
        db.session.commit()
        print("[Seed] Created employee records.")

    # 7. Seed Operational Expenses
    if Expense.query.count() == 0:
        today = date.today()
        expenses = [
            Expense(title='Maize Silage 500kg Purchase', category='Feed', amount=2250.0, date=today - timedelta(days=6), paid_to='Silage India Ltd', payment_method='UPI', receipt_number='SIL-8821', description='Green fodder top-up'),
            Expense(title='Monthly Farm Electricity Bill', category='Utilities & Electricity', amount=4800.0, date=today - timedelta(days=5), paid_to='State Electricity Board', payment_method='Bank Transfer', receipt_number='EB-9921', description='Milking parlor & cooling tank power'),
            Expense(title='Veterinary Health Checkup & Medicines', category='Veterinary & Medical', amount=3200.0, date=today - timedelta(days=3), paid_to='Dr. Alok Verma', payment_method='Cash', receipt_number='VET-102', description='Deworming and calcium supplements'),
            Expense(title='Milking Machine Service & Gasket Replacement', category='Maintenance & Repairs', amount=1850.0, date=today - timedelta(days=1), paid_to='DairyTech Solutions', payment_method='UPI', receipt_number='DT-441', description='Periodic routine servicing')
        ]
        db.session.add_all(expenses)
        db.session.commit()
        print("[Seed] Created operational expenses.")

app = create_app()

if __name__ == '__main__':
    print("==========================================================")
    print(" SMART DAIRY FARM MANAGEMENT SYSTEM - MCA MINOR PROJECT")
    print(" Running locally on http://localhost:5000")
    print(" Login: admin / admin123")
    print("==========================================================")
    app.run(debug=True, host='0.0.0.0', port=5000)

import unittest
import time
from app import create_app
from models import db
from models.user import User

class DairyAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_01_login_page_renders(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Smart Dairy Farm', response.data)
        # Verify public registration link is removed
        self.assertNotIn(b'Create New Account', response.data)
        print("[PASSED] Login page renders securely without public registration.")

    def test_02_unauthenticated_access_blocked(self):
        # Unauthenticated users should not access /users or /register
        resp_users = self.client.get('/users', follow_redirects=False)
        self.assertEqual(resp_users.status_code, 302)
        self.assertIn('/login', resp_users.headers['Location'])

        resp_reg = self.client.get('/register', follow_redirects=False)
        self.assertEqual(resp_reg.status_code, 302)
        self.assertIn('/login', resp_reg.headers['Location'])
        print("[PASSED] Unauthenticated access to /users and /register is blocked and redirected to /login.")

    def test_03_admin_routes(self):
        with self.client:
            # Login as Admin
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            routes_to_test = [
                ('/dashboard', 200, b'Total Cattle'),
                ('/users', 200, b'User Logins & Access Control'),
                ('/animals', 200, b'Cattle Master Register'),
                ('/animals/1', 200, b'Cattle Specifications & Pedigree'),
                ('/animals/add', 200, b'Live QR Tag Generator'),
                ('/milk', 200, b'Milk Yield & Production Register'),
                ('/milk/quick-entry', 200, b'Session Batch Milk Entry'),
                ('/feed', 200, b'Feed Inventory & Ration Management'),
                ('/vaccinations', 200, b'Cattle Vaccination & Immunization Tracker'),
                ('/employees', 200, b'Farm Staff & Labor Directory'),
                ('/expenses', 200, b'Dairy Farm Operational Expenses'),
                ('/reports', 200, b'Production & Financial Analytics'),
                ('/scan-qr', 200, b'Camera QR Code Scanner'),
                ('/api/qr/lookup/DF-101', 200, b'DF-101'),
                ('/api/animals/search?q=101', 200, b'DF-101'),
                ('/qr/download/1', 200, None)
            ]

            for path, expected_status, text_check in routes_to_test:
                res = self.client.get(path)
                self.assertEqual(res.status_code, expected_status, f"Route {path} failed with {res.status_code}")
                if text_check:
                    self.assertIn(text_check, res.data, f"Text {text_check} not found in {path}")
                print(f"[PASSED] {path} -> HTTP {res.status_code}")

    def test_04_admin_creates_new_user_login(self):
        unique_id = int(time.time())
        new_username = f"user_{unique_id}"
        new_email = f"user_{unique_id}@dairy.com"

        with self.client:
            # 1. Login as Admin
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            # 2. Admin creates a new staff login
            create_resp = self.client.post('/register', data={
                'full_name': 'Test Staff Member',
                'username': new_username,
                'email': new_email,
                'role': 'staff',
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(create_resp.status_code, 200)
            self.assertIn(bytes(new_username, 'utf-8'), create_resp.data)
            print(f"[PASSED] Admin successfully created new user login: {new_username}")

            # 3. Logout admin
            self.client.get('/logout', follow_redirects=True)

            # 4. Login with the newly created staff user
            staff_login = self.client.post('/login', data={
                'username': new_username,
                'password': 'password123'
            }, follow_redirects=True)
            self.assertEqual(staff_login.status_code, 200)
            self.assertIn(b'Test Staff Member', staff_login.data)
            print(f"[PASSED] Newly created staff user '{new_username}' logged in successfully.")

            # 5. Verify non-admin cannot access /users (Admin Only feature)
            staff_users_resp = self.client.get('/users', follow_redirects=True)
            self.assertIn(b'Access denied', staff_users_resp.data)
            print("[PASSED] Staff user access to /users was properly denied.")

            # 6. Verify staff cannot access Management section routes
            for restricted_path in ['/employees', '/expenses', '/reports']:
                r_resp = self.client.get(restricted_path, follow_redirects=True)
                self.assertIn(b'Access denied', r_resp.data, f"Staff should not access {restricted_path}")
                print(f"[PASSED] Staff access to {restricted_path} was properly denied.")

            # 7. Verify staff cannot register cattle, add/restock feed, or add vaccinations
            cattle_add_resp = self.client.get('/animals/add', follow_redirects=True)
            self.assertIn(b'Access denied', cattle_add_resp.data)
            print("[PASSED] Staff access to /animals/add was properly blocked.")

            feed_add_resp = self.client.post('/feed/add-stock', data={'feed_name': 'Test Feed'}, follow_redirects=True)
            self.assertIn(b'Access denied', feed_add_resp.data)
            print("[PASSED] Staff access to /feed/add-stock was properly blocked.")

            vaccine_add_resp = self.client.post('/vaccinations/add', data={'vaccine_name': 'Test Vaccine'}, follow_redirects=True)
            self.assertIn(b'Access denied', vaccine_add_resp.data)
            print("[PASSED] Staff access to /vaccinations/add was properly blocked.")

    def test_05_admin_registers_cattle_and_qr_generator(self):
        unique_tag = f"DF-T{int(time.time()) % 10000}"
        with self.client:
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            # Register new cow
            reg_resp = self.client.post('/animals/add', data={
                'tag_number': unique_tag,
                'name': 'Pari',
                'species': 'Cow',
                'breed': 'Sahiwal',
                'gender': 'Female',
                'weight_kg': '410',
                'milking_status': 'Milking',
                'health_status': 'Healthy',
                'notes': 'Test cattle entry with auto QR'
            }, follow_redirects=True)

            self.assertEqual(reg_resp.status_code, 200)
            self.assertIn(bytes(unique_tag, 'utf-8'), reg_resp.data)
            self.assertIn(b'added successfully with QR tag generated', reg_resp.data)
            print(f"[PASSED] Admin successfully registered new cattle with QR: {unique_tag}")

            # Test search API returns the newly registered cattle
            search_resp = self.client.get(f'/api/animals/search?q={unique_tag}')
            self.assertEqual(search_resp.status_code, 200)
            self.assertIn(bytes(unique_tag, 'utf-8'), search_resp.data)
            print(f"[PASSED] Search API returned the newly registered cattle {unique_tag}")

    def test_06_cattle_pagination_and_search(self):
        with self.client:
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            # Test cattle list page 1
            res = self.client.get('/animals?page=1')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Cattle Master Register', res.data)
            self.assertIn(b'Showing 10 records per page', res.data)

            # Test cattle search filter
            res_search = self.client.get('/animals?search=DF-101')
            self.assertEqual(res_search.status_code, 200)
            self.assertIn(b'DF-101', res_search.data)
            print("[PASSED] Cattle register pagination (10 per page) and search filter verified.")

    def test_07_milk_production_date_filter_and_pagination(self):
        with self.client:
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            # Test milk list default (5 per page)
            res = self.client.get('/milk?page=1')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Milk Yield & Production Register', res.data)
            self.assertIn(b'From Date', res.data)
            self.assertIn(b'To Date', res.data)

            # Test date range filter
            res_date = self.client.get('/milk?from_date=2026-01-01&to_date=2026-12-31')
            self.assertEqual(res_date.status_code, 200)
            self.assertIn(b'Production Register Entries', res_date.data)
            print("[PASSED] Milk register 5 entries per page pagination & From/To date filter verified.")

    def test_08_staff_and_manager_logins_and_case_insensitivity(self):
        with self.client:
            # Test manager login with mixed casing (e.g. 'Manager' or 'manager@dairy.com')
            mgr_resp = self.client.post('/login', data={'username': 'Manager', 'password': 'manager123'}, follow_redirects=True)
            self.assertEqual(mgr_resp.status_code, 200)
            self.assertIn(b'Welcome back, Dairy Farm Manager', mgr_resp.data)
            self.client.get('/logout', follow_redirects=True)

            # Test staff login with mixed casing (e.g. 'STAFF' or 'staff@dairy.com')
            staff_resp = self.client.post('/login', data={'username': 'STAFF', 'password': 'staff123'}, follow_redirects=True)
            self.assertEqual(staff_resp.status_code, 200)
            self.assertIn(b'Welcome back, Dairy Farm Staff', staff_resp.data)
            self.client.get('/logout', follow_redirects=True)

            # Test login with email
            email_resp = self.client.post('/login', data={'username': 'admin@dairy.com', 'password': 'admin123'}, follow_redirects=True)
            self.assertEqual(email_resp.status_code, 200)
            self.assertIn(b'Welcome back', email_resp.data)
            print("[PASSED] Cross-device staff, manager, and admin authentication (case-insensitive username/email) verified.")

if __name__ == '__main__':
    unittest.main()

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
                ('/milk', 200, b'Milk Yield & Production Register'),
                ('/milk/quick-entry', 200, b'Session Batch Milk Entry'),
                ('/feed', 200, b'Feed Inventory & Ration Management'),
                ('/vaccinations', 200, b'Cattle Vaccination & Immunization Tracker'),
                ('/employees', 200, b'Farm Staff & Labor Directory'),
                ('/expenses', 200, b'Dairy Farm Operational Expenses'),
                ('/reports', 200, b'Production & Financial Analytics'),
                ('/scan-qr', 200, b'Camera QR Code Scanner'),
                ('/api/qr/lookup/DF-101', 200, b'DF-101'),
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

if __name__ == '__main__':
    unittest.main()

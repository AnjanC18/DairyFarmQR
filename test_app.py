import unittest
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

    def test_02_login_and_access_dashboard(self):
        # Perform login
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Farm Overview & Production Monitoring', response.data)

    def test_03_protected_routes(self):
        with self.client:
            # Login
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            routes_to_test = [
                ('/dashboard', 200, b'Total Cattle'),
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

    def test_04_register_new_account(self):
        # Register a new user
        reg_response = self.client.post('/register', data={
            'full_name': 'Vikram Singh',
            'username': 'vikram',
            'email': 'vikram@dairy.com',
            'role': 'manager',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(reg_response.status_code, 200)
        self.assertIn(b'Vikram Singh', reg_response.data)
        print("[PASSED] Account registration -> New user 'vikram' created and logged in.")

if __name__ == '__main__':
    unittest.main()

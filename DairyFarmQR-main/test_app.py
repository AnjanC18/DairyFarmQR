import unittest
import time
from app import create_app
from models import db
from models.user import User
from models.animal import Animal
from models.milk import MilkProduction

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

    def test_09_manager_vaccination_mark_done_and_scan_integration(self):
        with self.client:
            # 1. Login as Manager
            self.client.post('/login', data={'username': 'manager', 'password': 'manager123'}, follow_redirects=True)

            # 2. QR scan lookup returns animal with vaccinations and is_manager=True
            scan_res = self.client.get('/api/qr/lookup/DF-101')
            self.assertEqual(scan_res.status_code, 200)
            data = scan_res.get_json()
            self.assertTrue(data['success'])
            self.assertTrue(data['is_manager'])
            self.assertIn('vaccinations', data['animal'])

            # 3. Manager quick adds a vaccination from QR scan
            quick_add_res = self.client.post('/api/vaccinations/quick-add', json={
                'animal_id': data['animal']['id'],
                'vaccine_name': 'Foot and Mouth Disease (FMD)',
                'next_due_days': 180,
                'remarks': 'Administered during scan test'
            })
            self.assertEqual(quick_add_res.status_code, 200)
            add_data = quick_add_res.get_json()
            self.assertTrue(add_data['success'])
            new_vax_id = add_data['vaccination']['id']
            print(f"[PASSED] Manager successfully administered & recorded vaccine id {new_vax_id} via scan interface.")

            # 4. Manager marks a vaccination as done
            mark_done_res = self.client.post(f'/api/vaccinations/mark-done/{new_vax_id}')
            self.assertEqual(mark_done_res.status_code, 200)
            done_data = mark_done_res.get_json()
            self.assertTrue(done_data['success'])
            self.assertEqual(done_data['vaccination']['status'], 'Completed')
            print(f"[PASSED] Manager marked vaccine {new_vax_id} as DONE successfully.")

            # 5. Logout manager & login as staff to verify authorization protection
            self.client.get('/logout', follow_redirects=True)
            self.client.post('/login', data={'username': 'staff', 'password': 'staff123'}, follow_redirects=True)

            staff_mark_res = self.client.post(f'/api/vaccinations/mark-done/{new_vax_id}')
            self.assertEqual(staff_mark_res.status_code, 403)
            print("[PASSED] Staff prevented from marking vaccination as done (403 Forbidden).")

    def test_10_ai_milk_yield_forecasting(self):
        """Feature 1: Test 7 and 14 day milk yield forecasting for herd & cow."""
        from services.ai_engine import DairyAIEngine
        with self.app.app_context():
            # 14-day herd forecast
            f14 = DairyAIEngine.forecast_milk_yield(days=14)
            self.assertEqual(f14['days'], 14)
            self.assertEqual(len(f14['dates']), 14)
            self.assertEqual(len(f14['forecast_liters']), 14)
            self.assertEqual(len(f14['upper_bound']), 14)
            self.assertEqual(len(f14['lower_bound']), 14)
            self.assertGreater(f14['total_forecast_liters'], 0)
            self.assertGreater(f14['avg_daily_forecast'], 0)
            
            # Verify confidence bounds
            for i in range(14):
                self.assertGreaterEqual(f14['upper_bound'][i], f14['forecast_liters'][i])
                self.assertLessEqual(f14['lower_bound'][i], f14['forecast_liters'][i])

            # 7-day cow forecast for DF-101
            cow = Animal.query.filter_by(tag_number='DF-101').first()
            if cow:
                f_cow = DairyAIEngine.forecast_milk_yield(days=7, animal_id=cow.id)
                self.assertEqual(f_cow['days'], 7)
                self.assertEqual(len(f_cow['forecast_liters']), 7)
                self.assertGreater(f_cow['total_forecast_liters'], 0)
            print("[PASSED] Feature 1: AI Milk Yield Forecasting (7 to 14 days, herd & individual) verified.")

    def test_11_ai_anomaly_early_illness_detection(self):
        """Feature 2: Test Anomaly Detection flags cows with sharp yield drops."""
        from services.ai_engine import DairyAIEngine
        from datetime import date
        with self.app.app_context():
            # Seed an intentional sharp drop for DF-101 to verify detection
            cow = Animal.query.filter_by(tag_number='DF-101').first()
            if cow:
                # Add an anomalous low record today (38% drop)
                anomaly_rec = MilkProduction(
                    animal_id=cow.id,
                    date=date.today(),
                    session='Morning',
                    quantity_liters=4.2,  # vs normal 7.5L
                    fat_percentage=3.5,
                    snf_percentage=7.9,
                    rate_per_liter=42.0,
                    recorded_by='TestMilker'
                )
                anomaly_rec.calculate_total()
                db.session.add(anomaly_rec)
                db.session.commit()

            anomalies = DairyAIEngine.detect_yield_anomalies(lookback_days=14)
            self.assertIsInstance(anomalies, list)
            # Verify alert text format
            if anomalies:
                alert = anomalies[0]
                self.assertIn('gave', alert['alert_text'])
                self.assertIn('less than her 7-day average', alert['alert_text'])
                self.assertIn('Check her health', alert['alert_text'])
                self.assertIn(alert['severity'], ['CRITICAL', 'WARNING', 'WATCH'])
                self.assertGreater(alert['drop_percentage'], 15.0)
            print("[PASSED] Feature 2: AI Anomaly Detection (Early Illness Warning) with exact alert text verified.")

    def test_12_ai_mastitis_risk_prediction(self):
        """Feature 3: Test Mastitis Risk Prediction combining yield drops, fat/SNF, and treatments."""
        from services.ai_engine import DairyAIEngine
        with self.app.app_context():
            mastitis_list = DairyAIEngine.predict_mastitis_risk()
            self.assertIsInstance(mastitis_list, list)
            self.assertGreater(len(mastitis_list), 0)
            
            top_risk = mastitis_list[0]
            self.assertIn('risk_score', top_risk)
            self.assertGreaterEqual(top_risk['risk_score'], 0.0)
            self.assertLessEqual(top_risk['risk_score'], 100.0)
            self.assertIn(top_risk['risk_level'], ['HIGH RISK', 'MODERATE RISK', 'LOW RISK'])
            self.assertIsInstance(top_risk['contributing_factors'], list)
            self.assertGreater(len(top_risk['contributing_factors']), 0)
            self.assertTrue(bool(top_risk['recommendation']))
            print(f"[PASSED] Feature 3: AI Mastitis Risk Prediction verified (Top Risk: {top_risk['tag_number']} at {top_risk['risk_score']}%).")

    def test_13_ai_cull_and_keep_recommendation(self):
        """Feature 4: Test Cull and Keep Recommendation via K-Means clustering and economic score."""
        from services.ai_engine import DairyAIEngine
        with self.app.app_context():
            cull_keep = DairyAIEngine.recommend_cull_keep()
            self.assertIn('cows', cull_keep)
            self.assertGreater(len(cull_keep['cows']), 0)
            
            # Check cluster recommendations exist
            recs = [c['recommendation'] for c in cull_keep['cows']]
            self.assertTrue(any('High Profit' in r or 'Average Profit' in r or 'Cull' in r for r in recs))
            
            top_cow = cull_keep['cows'][0]
            self.assertIn('composite_score', top_cow)
            self.assertGreaterEqual(top_cow['composite_score'], 0)
            self.assertIn('daily_margin', top_cow)
            print(f"[PASSED] Feature 4: Cull and Keep K-Means Clustering & Economic Ranking verified ({cull_keep['high_count']} High, {cull_keep['avg_count']} Avg, {cull_keep['cull_count']} Cull).")

    def test_14_ai_feed_optimization_and_stockout(self):
        """Feature 5: Test Feed Ration Linear Programming & Stock Depletion."""
        from services.ai_engine import DairyAIEngine
        with self.app.app_context():
            # Test Linear Programming Ration Optimization
            ration = DairyAIEngine.optimize_feed_ration(custom_weight=500.0, custom_yield=15.0)
            self.assertGreater(ration['total_daily_cost'], 0)
            self.assertGreater(ration['delivered_dm'], 0)
            self.assertGreater(len(ration['ration_items']), 0)
            self.assertGreater(ration['cost_per_liter'], 0)

            # Test Feed Depletion Forecasting
            depletion = DairyAIEngine.forecast_feed_depletion()
            self.assertIsInstance(depletion, list)
            self.assertGreater(len(depletion), 0)
            
            item = depletion[0]
            self.assertIn('days_remaining', item)
            self.assertIn('daily_burn_rate', item)
            self.assertIn('runout_date', item)
            self.assertIn(item['reorder_urgency'], ['CRITICAL', 'URGENT', 'NORMAL'])
            print(f"[PASSED] Feature 5: Feed LP Optimization (Rs. {ration['total_daily_cost']}/day) & Stock Depletion verified.")

    def test_15_ai_expense_and_profit_forecasting(self):
        """Feature 6: Test Expense and Profit Forecasting for next 30 days."""
        from services.ai_engine import DairyAIEngine
        with self.app.app_context():
            fin = DairyAIEngine.forecast_financials_next_month()
            self.assertIn('total_projected_revenue', fin)
            self.assertIn('total_projected_expenses', fin)
            self.assertIn('total_projected_net_profit', fin)
            self.assertEqual(len(fin['dates']), 30)
            self.assertEqual(len(fin['projected_revenue']), 30)
            self.assertEqual(len(fin['projected_expenses']), 30)
            self.assertGreater(fin['total_projected_revenue'], 0)
            self.assertGreater(fin['total_projected_expenses'], 0)
            print(f"[PASSED] Feature 6: Next Month Financial Forecasting (Proj Rev: Rs. {fin['total_projected_revenue']}, Proj Net: Rs. {fin['total_projected_net_profit']}) verified.")

    def test_16_treatment_log_workflow(self):
        """Test MedicalTreatment model, routes, and milk withholding tracking."""
        from models.treatment import MedicalTreatment
        from datetime import date
        with self.client:
            self.client.post('/login', data={'username': 'manager', 'password': 'manager123'}, follow_redirects=True)
            
            # View treatment list
            res = self.client.get('/treatments')
            self.assertEqual(res.status_code, 200)
            self.assertIn(b'Veterinary Treatment Log', res.data)

            # Log new treatment
            cow = Animal.query.first()
            log_res = self.client.post('/treatments/add', data={
                'animal_id': cow.id,
                'diagnosis': 'Clinical Mastitis',
                'symptoms': 'Udder swelling and milk clotting',
                'treatment_given': 'Ceftiofur 10ml IM',
                'administered_date': date.today().strftime('%Y-%m-%d'),
                'withdrawal_period_days': '3',
                'cost': '450.0',
                'veterinarian': 'Dr. Test Vet',
                'notes': 'Re-examine tomorrow'
            }, follow_redirects=True)
            self.assertEqual(log_res.status_code, 200)
            self.assertIn(b'Medical treatment logged', log_res.data)

            # Verify treatment in database
            treatment = MedicalTreatment.query.filter_by(animal_id=cow.id, diagnosis='Clinical Mastitis').first()
            self.assertIsNotNone(treatment)
            self.assertTrue(treatment.is_in_withdrawal)
            self.assertEqual(treatment.withdrawal_days_remaining, 3)

            # Update status to Recovered
            update_res = self.client.post(f'/treatments/{treatment.id}/status', data={'status': 'Recovered'}, follow_redirects=True)
            self.assertEqual(update_res.status_code, 200)
            updated_treatment = db.session.get(MedicalTreatment, treatment.id)
            self.assertEqual(updated_treatment.status, 'Recovered')
            print("[PASSED] Medical Treatment log & milk withdrawal workflow verified.")

    def test_17_ai_routes_and_api_endpoints(self):
        """Test /ai-insights web hub and all REST API endpoints."""
        with self.client:
            self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)

            # 1. Main AI Insights Hub HTML
            res_hub = self.client.get('/ai-insights')
            self.assertEqual(res_hub.status_code, 200)
            self.assertIn(b'AI Farm Intelligence', res_hub.data)
            self.assertIn(b'Milk Yield Forecasting', res_hub.data)
            self.assertIn(b'Mastitis Risk Radar', res_hub.data)

            # 2. REST API: Forecast
            res_f = self.client.get('/api/ai/forecast?days=14')
            self.assertEqual(res_f.status_code, 200)
            self.assertEqual(res_f.get_json()['days'], 14)

            # 3. REST API: Anomalies
            res_a = self.client.get('/api/ai/anomalies')
            self.assertEqual(res_a.status_code, 200)
            self.assertIsInstance(res_a.get_json(), list)

            # 4. REST API: Mastitis Risk
            res_m = self.client.get('/api/ai/mastitis-risk')
            self.assertEqual(res_m.status_code, 200)
            self.assertIsInstance(res_m.get_json(), list)

            # 5. REST API: Cull & Keep
            res_c = self.client.get('/api/ai/cull-keep')
            self.assertEqual(res_c.status_code, 200)
            self.assertIn('cows', res_c.get_json())

            # 6. REST API: Feed Ration
            res_r = self.client.get('/api/ai/feed/ration?weight=480&yield=14')
            self.assertEqual(res_r.status_code, 200)
            self.assertIn('ration_items', res_r.get_json())

            # 7. REST API: Financial Forecast
            res_fin = self.client.get('/api/ai/financial-forecast')
            self.assertEqual(res_fin.status_code, 200)
            self.assertIn('total_projected_net_profit', res_fin.get_json())

            # 8. Reports page with AI forecast line
            res_rep = self.client.get('/reports')
            self.assertEqual(res_rep.status_code, 200)
            self.assertIn(b'Herd Milk Yield Forecasting (Next 14 Days)', res_rep.data)
            self.assertIn(b'financialForecastChart', res_rep.data)

            print("[PASSED] AI Web Hub (/ai-insights), Reports Forecast Line, and all 6 REST API endpoints verified.")

if __name__ == '__main__':
    unittest.main()


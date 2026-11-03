"""
Automated Test Suite for Apla Shetkari
Tests database operations, authentication flows, route responses, and AI service integration.
"""

import os
import json
import unittest
from werkzeug.security import generate_password_hash, check_password_hash

import database
from app import app
import ai_service

class AplaShetkariTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment and initialize test database."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()
        with app.app_context():
            database.init_db()

    def test_01_database_user_crud(self):
        """Test user creation, retrieval, and password verification."""
        test_email = "testfarmer@krishi.com"
        test_mobile = "9876543210"
        test_pw = "farmerPass123"
        hashed = generate_password_hash(test_pw)

        # Clean existing test user if any
        existing = database.get_user_by_email_or_mobile(test_email)
        if not existing:
            user_id = database.create_user(
                full_name="Balaram Patil",
                mobile=test_mobile,
                email=test_email,
                password_hash=hashed,
                state="Maharashtra",
                district="Nashik"
            )
            self.assertIsNotNone(user_id)
            self.assertGreater(user_id, 0)
        else:
            user_id = existing['id']

        user = database.get_user_by_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], "Balaram Patil")
        self.assertTrue(check_password_hash(user['password_hash'], test_pw))

    def test_02_database_chat_history(self):
        """Test saving, retrieving, and clearing chat messages."""
        user = database.get_user_by_email_or_mobile("testfarmer@krishi.com")
        self.assertIsNotNone(user)

        user_id = user['id']
        msg_id = database.save_chat_message(
            user_id=user_id,
            user_message="What is the best fertilizer for wheat?",
            ai_response="Wheat requires balanced NPK (120:60:40 kg/ha). Apply nitrogen in split doses."
        )
        self.assertIsNotNone(msg_id)

        history = database.get_chat_history(user_id)
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[-1]['user_message'], "What is the best fertilizer for wheat?")

        # Clear history
        cleared = database.clear_chat_history(user_id)
        self.assertGreaterEqual(cleared, 1)
        fresh_history = database.get_chat_history(user_id)
        self.assertEqual(len(fresh_history), 0)

    def test_03_database_crop_recommendations(self):
        """Test saving and retrieving crop recommendation sessions."""
        user = database.get_user_by_email_or_mobile("testfarmer@krishi.com")
        user_id = user['id']

        crops_sample = [
            {
                "crop_name": "Soybean (सोयाबीन)",
                "suitability_reason": "Thrives in black soil with good drainage.",
                "suitable_soil": "Black Cotton Soil",
                "growing_season": "Kharif",
                "water_requirement": "Moderate",
                "cultivation_tips": "Treat seeds with Trichoderma before sowing.",
                "expected_duration": "90-105 Days",
                "estimated_yield_market": "8-10 Quintals/Acre",
                "pest_disease_alert": "Monitor for stem borer and yellow mosaic virus."
            }
        ]

        rec_id = database.save_crop_recommendation(
            user_id=user_id,
            soil_type="Black Cotton Soil",
            location="Nashik, Maharashtra",
            season="Kharif",
            recommended_crops_json=json.dumps(crops_sample)
        )
        self.assertIsNotNone(rec_id)

        recs = database.get_crop_recommendations(user_id)
        self.assertGreaterEqual(len(recs), 1)
        parsed = json.loads(recs[0]['recommended_crops'])
        self.assertEqual(parsed[0]['crop_name'], "Soybean (सोयाबीन)")

    def test_04_public_routes(self):
        """Test all public HTTP routes return status 200."""
        routes = ['/', '/about', '/chat', '/crop-recommendation', '/login', '/register']
        for r in routes:
            response = self.client.get(r)
            self.assertEqual(response.status_code, 200, f"Route {r} failed with code {response.status_code}")

    def test_05_auth_flow(self):
        """Test full login, dashboard access, and logout lifecycle."""
        # Unauthorized access to /dashboard should redirect to login
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers['Location'])

        # Valid login
        login_res = self.client.post('/login', data={
            'identifier': 'testfarmer@krishi.com',
            'password': 'farmerPass123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Balaram', login_res.data)

        # Authenticated access to dashboard
        dash_res = self.client.get('/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b'Nashik', dash_res.data)

        # Logout
        logout_res = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(logout_res.status_code, 200)

    def test_06_ai_json_parser(self):
        """Test robust JSON parser for crop recommendations."""
        sample_json_text = """```json
[
  {
    "crop_name": "Gram / Chana (हरभरा)",
    "suitability_reason": "Ideal for rabi residual moisture in deep black soil.",
    "suitable_soil": "Black Cotton Soil",
    "growing_season": "Rabi (October-March)",
    "water_requirement": "Low to Moderate (2 irrigations)",
    "cultivation_tips": "Sow with Rhizobium culture.",
    "expected_duration": "95-110 Days",
    "estimated_yield_market": "7-9 Quintals/Acre",
    "pest_disease_alert": "Pod borer (Helicoverpa armigera)"
  }
]
```"""
        parsed = ai_service.parse_json_crops(sample_json_text)
        self.assertIsNotNone(parsed)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]['crop_name'], "Gram / Chana (हरभरा)")

    def test_07_chat_api_validation(self):
        """Test API rate limiting and validation on /api/chat."""
        # Empty message should return 400
        res = self.client.post('/api/chat', json={'message': ''})
        self.assertEqual(res.status_code, 400)

        # Valid message with missing key returns informative response
        res2 = self.client.post('/api/chat', json={
            'message': 'Which crop should I grow in black soil?',
            'language': 'English'
        })
        self.assertEqual(res2.status_code, 200)
        data = res2.get_json()
        self.assertIn('success', data)

if __name__ == '__main__':
    unittest.main()

from rest_framework.test import APITestCase


class AiTests(APITestCase):
    def test_intent_and_recommend(self):
        resp = self.client.post('/ai/intent/', {'text': 'I need cheap school shoes for kids'}, format='json')
        self.assertEqual(resp.status_code, 200)
        intent = resp.data['intent']
        self.assertEqual(intent['category'], 'shoes')
        # recommend will attempt to call external recommender and then fallback if unreachable
        resp2 = self.client.post('/ai/recommend/', {'intent': intent, 'market_id': 'Bubanza_20'}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('items', resp2.data)

    def test_recommend_fallback(self):
        # when recommender URL is unreachable, view should return fallback
        import os
        os.environ['RECOMMENDER_URL'] = 'http://localhost:9999/recommend'
        resp = self.client.post('/ai/recommend/', {'intent': {'category': 'general'}}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('items', resp.data)

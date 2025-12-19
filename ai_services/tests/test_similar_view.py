from django.test import TestCase
from rest_framework.test import APIRequestFactory
from unittest.mock import patch
from ai_services.views import SimilarView

class SimilarViewTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('ai_services.views.requests.post')
    def test_similar_uses_recommender(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'items': [{'id': 1, 'score': 0.9}], 'source': 'recommender'}
        payload = {'products': [{'id': 1, 'name': 'A', 'description': 'desc'}], 'product_id': 1}
        request = self.factory.post('/ai/similar/', payload, format='json')
        response = SimilarView.as_view()(request)
        assert response.status_code == 200
        assert response.data['source'] == 'recommender'

    @patch('ai_services.views.requests.post')
    def test_similar_fallbacks_to_vector(self, mock_post):
        # First call (to recommender) raises, second call to index succeeds and query returns items
        def side_effect(url, json=None, timeout=None):
            class R:
                def __init__(self, url):
                    self._url = url
                    if 'similar' in url:
                        raise Exception('down')
                    self.status_code = 200
                def raise_for_status(self):
                    pass
                def json(self):
                    if 'query' in self._url:
                        return {'items': [{'id': 2, 'score': 0.8}], 'source': 'vector'}
                    return {'ok': True}
            return R(url)

        mock_post.side_effect = side_effect
        payload = {'products': [{'id': 2, 'name': 'B', 'description': 'desc'}], 'product_id': 2}
        request = self.factory.post('/ai/similar/', payload, format='json')
        response = SimilarView.as_view()(request)
        assert response.status_code == 200
        assert response.data['source'] == 'vector'

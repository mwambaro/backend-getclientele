from django.test import TestCase


class DocsTests(TestCase):
    def test_openapi_yaml_served(self):
        resp = self.client.get('/openapi.yaml')
        assert resp.status_code == 200
        assert b'openapi' in resp.content

    def test_swagger_ui_page(self):
        resp = self.client.get('/docs/')
        assert resp.status_code == 200
        # ensure it contains the swagger bundle script reference
        assert b'SwaggerUIBundle' in resp.content or b'swagger-ui' in resp.content

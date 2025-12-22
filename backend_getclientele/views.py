import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

SWAGGER_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>GetClientele API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js" crossorigin></script>
    <script>
      window.onload = function() {
        const ui = SwaggerUIBundle({
          url: '/openapi.yaml',
          dom_id: '#swagger-ui',
          deepLinking: true,
          presets: [SwaggerUIBundle.presets.apis],
          layout: "BaseLayout",
          // Enable the Authorize button (uses OpenAPI securitySchemes)
          oauth2RedirectUrl: window.location.origin + '/docs/',
        });
        window.ui = ui;
      };
    </script>
  </body>
</html>
"""


def swagger_ui_view(request):
    return HttpResponse(SWAGGER_HTML, content_type='text/html')


def openapi_yaml_view(request):
    # Serve the OpenAPI spec from static files (conventional approach)
    # First, check an explicit static/ path inside the project
    static_path = os.path.join(settings.BASE_DIR, 'static', 'openapi_getclientele.yaml')
    static_path = os.path.normpath(static_path)
    if os.path.exists(static_path):
        with open(static_path, 'rb') as fh:
            return HttpResponse(fh.read(), content_type='application/yaml')

    try:
        # Next, ask Django staticfiles finders (works in dev with app/static or collected files)
        from django.contrib.staticfiles import finders
        spec_path = finders.find('openapi_getclientele.yaml')
        if spec_path:
            with open(spec_path, 'rb') as fh:
                return HttpResponse(fh.read(), content_type='application/yaml')
    except Exception:
        pass

    # Fallback: look in Specs/ folder near the project root
    candidates = [
        os.path.join(settings.BASE_DIR, 'Specs', 'openapi_getclientele.yaml'),
        os.path.join(settings.BASE_DIR, '..', 'Specs', 'openapi_getclientele.yaml'),
    ]
    for p in candidates:
        p = os.path.normpath(p)
        if os.path.exists(p):
            with open(p, 'rb') as fh:
                return HttpResponse(fh.read(), content_type='application/yaml')
    return HttpResponseNotFound('OpenAPI spec not found')

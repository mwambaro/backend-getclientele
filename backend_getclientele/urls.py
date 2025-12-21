from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ai_services.views import SimilarView
from .views import swagger_ui_view, openapi_yaml_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/signup/', include('users.urls')),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('vendors/', include('vendors.urls')),
    path('map/', include('mapping.urls')),
    path('sessions/', include('sessions_app.urls')),
    path('payments/', include('payments.urls')),
    path('ai/', include('ai_services.urls')),
    # Direct route for compatibility: /api/ai/similar/
    path('api/ai/similar/', SimilarView.as_view(), name='api-similar'),
    # Swagger UI and OpenAPI spec
    path('docs/', swagger_ui_view, name='swagger-ui'),
    path('openapi.yaml', openapi_yaml_view, name='openapi-yaml'),
]

Add /api/ai/similar/ route

If your project includes ai_services via `path('api/ai/', include('ai_services.urls'))`, ensure `ai_services/urls.py` contains:

from django.urls import path
from . import views

urlpatterns = [
    path('intent/', views.IntentView.as_view(), name='intent'),
    path('recommend/', views.RecommendView.as_view(), name='recommend'),
    path('similar/', views.SimilarView.as_view(), name='similar'),
]

If you prefer to add a direct root route (no include), add to `backend_getclientele/urls.py`:

from ai_services.views import SimilarView

urlpatterns += [
    path('api/ai/similar/', SimilarView.as_view(), name='api-similar'),
]

OpenAPI update
- I added `/api/ai/similar` to `Specs/openapi_getclientele.yaml` to match the intended API route.

Notes
- The `SimilarView` tries the recommender `/similar` endpoint (fast) and falls back to the vector service `/index` + `/query` on error.
- If you'd like, I can try to edit your project's urls directly; I couldn't locate the root urls file via the workspace search tools, so I left this patch for you to apply. If you want me to apply it directly, tell me the path to the root `urls.py` file (I can attempt to patch it).
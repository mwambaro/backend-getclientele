from django.urls import path
from .views import IntentView, RecommendView, CategorizeView, RankView, NavigationView, ForecastView

urlpatterns = [
    path('intent/', IntentView.as_view(), name='ai_intent'),
    path('recommend/', RecommendView.as_view(), name='ai_recommend'),
    path('categorize/', CategorizeView.as_view(), name='ai_categorize'),
    path('rank/', RankView.as_view(), name='ai_rank'),
    path('navigation/', NavigationView.as_view(), name='ai_navigation'),
    path('forecast/', ForecastView.as_view(), name='ai_forecast'),
]

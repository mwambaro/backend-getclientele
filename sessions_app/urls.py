from django.urls import path
from .views import CreateSessionView, SessionDetailView, AddItemView

urlpatterns = [
    path('', CreateSessionView.as_view(), name='session_create'),
    path('<int:id>/', SessionDetailView.as_view(), name='session_detail'),
    path('<int:id>/add_item/', AddItemView.as_view(), name='session_add_item'),
]

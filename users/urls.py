from django.urls import path
from .views import SignupView, UserDetailView

urlpatterns = [
    path('', SignupView.as_view(), name='signup'),
    path('<int:id>/', UserDetailView.as_view(), name='user_detail'),
]

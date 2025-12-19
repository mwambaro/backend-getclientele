from django.urls import path
from .views import StartTraceView, StopTraceView

urlpatterns = [
    path('trace/start/', StartTraceView.as_view(), name='trace_start'),
    path('trace/stop/<int:id>/', StopTraceView.as_view(), name='trace_stop'),
]

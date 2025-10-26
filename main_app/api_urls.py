from django.urls import path
from . import api_views

urlpatterns = [
    # API endpoints
    path('test/', api_views.test_api, name='test_api'),
]


















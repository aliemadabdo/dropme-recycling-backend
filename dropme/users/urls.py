from django.urls import path
from .views import (
    UserRegistrationView,
    UserProfileView,
    UserStatsView,
)

app_name = 'users'

urlpatterns = [    
    # User management
    path('users/register/', UserRegistrationView.as_view(), name='user-register'),
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('users/me/stats/', UserStatsView.as_view(), name='user-stats'),
]
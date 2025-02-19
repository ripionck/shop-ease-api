from django.urls import path
from .views import UserRegistrationView, UserLoginView, UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile')
]

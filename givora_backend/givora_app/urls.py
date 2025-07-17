from django.urls import path
from .views import register, login_view, logout_view, create_donation, verify_payment

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('donate/', create_donation, name='create_donation'),
    path('donate/verify/', verify_payment, name='verify_payment'),
]

from django.urls import path
from .views import register, login_view, logout_view, create_donation, verify_payment, user_role, \
    volunteer_details, volunteer_upcoming_events, volunteer_donation_tracking, test_endpoint, update_volunteer_profile, \
    user_donations, get_donation_by_id

urlpatterns = [
    path('user/donations/', user_donations, name='user_donations'),
    path('donations/<int:donation_id>/', get_donation_by_id, name='get_donation_by_id'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('donate/', create_donation, name='create_donation'),
    path('donate/verify/', verify_payment, name='verify_payment'),
    path('user-role/', user_role, name='user_role'),
    
    # Test endpoint
    path('test/', test_endpoint, name='test_endpoint'),
    
    # Volunteer API endpoints
    path('volunteer/details/', volunteer_details, name='volunteer_details'),
    path('volunteer/profile/update/', update_volunteer_profile, name='update_volunteer_profile'),
    path('volunteer/events/', volunteer_upcoming_events, name='volunteer_events'),
    path('volunteer/donations/', volunteer_donation_tracking, name='volunteer_donations'),
]

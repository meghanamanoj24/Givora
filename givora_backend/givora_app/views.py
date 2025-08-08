from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Donation, MoneyDonation, ItemDonation, FoodDonation, User
import razorpay
from rest_framework.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.db.models import Sum, Count
from rest_framework.authtoken.models import Token

# Create your views here.

@api_view(['GET'])
def test_endpoint(request):
    """Test endpoint to verify URL routing"""
    return Response({'message': 'Test endpoint working!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_role(request):
    user = request.user
    if user.is_authenticated:
        # Get role from user model
        role = user.role
        # For admin users
        if user.email == 'admin@gmail.com' or user.is_superuser:
            role = 'Admin'
        return Response({'role': role}, status=status.HTTP_200_OK)
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            if request.content_type and request.content_type.startswith('multipart/form-data'):
                firstname = request.POST.get('firstname', '').strip()
                lastname = request.POST.get('lastname', '').strip()
                email = request.POST.get('email', '').strip()
                password = request.POST.get('password', '')
                phone_number = request.POST.get('phone_number', '').strip()
                address = request.POST.get('address', '').strip()
                role = request.POST.get('role', '').strip()
                photo = request.FILES.get('photo')  # Optional
            else:
                data = json.loads(request.body)
                firstname = data.get('firstname', '').strip()
                lastname = data.get('lastname', '').strip()
                email = data.get('email', '').strip()
                password = data.get('password', '')
                phone_number = data.get('phone_number', '').strip()
                address = data.get('address', '').strip()
                role = data.get('role', '').strip()
                photo = None

            if not all([firstname, lastname, email, password, phone_number, address, role]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)
            if len(password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters.'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'User already exists.'}, status=400)

            user = User.objects.create_user(
                email=email,
                password=password,
                firstname=firstname,
                lastname=lastname,
                phone_number=phone_number,
                address=address,
                role=role,
            )
            if photo:
                user.photo = photo
                user.save()
            return JsonResponse({'message': 'Registration successful!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            password = data.get('password', '')
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required.'}, status=400)
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)  # Use Django session login
                # Get or create token
                token, created = Token.objects.get_or_create(user=user)
                # Get role from user model
                role = user.role
                # For admin users
                if user.email == 'admin@gmail.com' or user.is_superuser:
                    role = 'Admin'
                # Return token along with other info
                return JsonResponse({
                    'message': 'Login successful!', 
                    'role': role, 
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'role': role
                    }
                }, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials.'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out successfully.'}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def volunteer_details(request):
    """Get details of the currently logged-in volunteer"""
    user = request.user
    if user.is_authenticated:
        if user.role == 'Volunteer':
            # Manually create user data dictionary to handle optional photo field
            user_data = {
                'id': user.id,
                'email': user.email,
                'firstname': user.firstname,
                'lastname': user.lastname,
                'phone_number': user.phone_number,
                'address': user.address,
                'role': user.role,
                'photo': user.photo.url if user.photo else None,  # Handle optional photo
            }
            
            # Enhanced volunteer profile data
            volunteer_data = {
                'user': user_data,
                'profile': {
                    'volunteer_since': '2023',  # You can add this field to User model later
                    'availability': ['Weekends', 'Evenings'],  # Available time slots
                    'interests': [
                        'Food Distribution',
                        'Clothing Drives', 
                        'Fundraising',
                        'Education'
                    ],
                    'bio': f'Dedicated volunteer committed to making a difference in the community through various humanitarian activities.',
                    'preferred_activities': ['Food Distribution', 'Clothing Drives'],
                    'emergency_contact': {
                        'name': f'{user.firstname} {user.lastname}',
                        'phone': user.phone_number,
                        'relationship': 'Self'
                    }
                },
                'stats': {
                    'assigned_tasks': 7,
                    'completed_tasks': 3,
                    'lives_impacted': 120,
                    'total_events': 10,
                    'hours_served': 45,
                    'current_streak': 5,  # Days of consecutive volunteering
                    'total_donations_collected': 25,
                    'communities_served': 8
                },
                'skills': [
                    'Food Service',
                    'Organization', 
                    'Communication',
                    'Leadership',
                    'First Aid',
                    'Event Planning'
                ],
                'certifications': [
                    'Food Safety Training',
                    'First Aid Certified',
                    'Child Safety Training'
                ],
                'achievements': [
                    'Top Volunteer of the Month - March 2023',
                    '100 Hours Milestone',
                    'Community Impact Award'
                ],
                'preferences': {
                    'preferred_events': ['Food Distribution', 'Clothing Drives', 'Fundraising'],
                    'max_hours_per_week': 15,
                    'travel_distance': 25,  # km
                    'group_size_preference': 'Medium (5-10 people)',
                    'special_needs_support': True
                }
            }
            return Response(volunteer_data, status=status.HTTP_200_OK)
        return Response({'error': 'User is not a volunteer'}, status=status.HTTP_403_FORBIDDEN)
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_volunteer_profile(request):
    """Update volunteer profile information"""
    user = request.user
    if user.is_authenticated and user.role == 'Volunteer':
        try:
            data = request.data
            
            # Update basic user information
            if 'firstname' in data:
                user.firstname = data['firstname']
            if 'lastname' in data:
                user.lastname = data['lastname']
            if 'phone_number' in data:
                user.phone_number = data['phone_number']
            if 'address' in data:
                user.address = data['address']
            
            # Handle photo upload if provided
            if 'photo' in request.FILES:
                user.photo = request.FILES['photo']
            
            user.save()
            
            return Response({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'role': user.role,
                    'photo': user.photo.url if user.photo else None,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def volunteer_upcoming_events(request):
    """Get upcoming events for volunteers"""
    user = request.user
    if user.is_authenticated and user.role == 'Volunteer':
        # Placeholder data - in a real app, this would come from a database
        events = [
            {
                'id': 1,
                'title': 'Food Distribution Drive',
                'date': '2023-11-15',
                'time': '10:00 AM - 2:00 PM',
                'location': 'Community Center, 123 Main St',
                'status': 'Upcoming',
                'description': 'Distributing food packages to homeless individuals'
            },
            {
                'id': 2,
                'title': 'Clothing Donation Sorting',
                'date': '2023-11-18',
                'time': '9:00 AM - 12:00 PM',
                'location': 'Givora Warehouse, 456 Oak Ave',
                'status': 'Upcoming',
                'description': 'Sorting and organizing donated clothing items'
            },
            {
                'id': 3,
                'title': 'Elderly Care Visit',
                'date': '2023-11-20',
                'time': '3:00 PM - 5:00 PM',
                'location': 'Sunshine Retirement Home, 789 Elm St',
                'status': 'Upcoming',
                'description': 'Visiting elderly residents and providing companionship'
            }
        ]
        return Response(events, status=status.HTTP_200_OK)
    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def volunteer_donation_tracking(request):
    """Get donation tracking information for volunteers"""
    user = request.user
    if user.is_authenticated and user.role == 'Volunteer':
        # Placeholder data - in a real app, this would come from a database
        donations = [
            {
                'id': 101,
                'type': 'Food',
                'date': '2023-11-10',
                'status': 'Delivered',
                'items': 'Rice, Beans, Canned Goods',
                'quantity': '50 kg',
                'destination': 'Community Shelter'
            },
            {
                'id': 102,
                'type': 'Clothing',
                'date': '2023-11-12',
                'status': 'In Transit',
                'items': 'Winter Jackets, Gloves',
                'quantity': '30 items',
                'destination': 'Homeless Outreach Center'
            },
            {
                'id': 103,
                'type': 'Money',
                'date': '2023-11-14',
                'status': 'Processed',
                'items': 'Cash Donation',
                'quantity': '$500',
                'destination': 'Education Fund'
            }
        ]
        return Response(donations, status=status.HTTP_200_OK)
    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

# Helper: Check if user is Donor

def is_donor(user):
    return user.role == 'Donor'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_donation(request):
    user = request.user
    print('DEBUG: user.is_authenticated:', user.is_authenticated)
    print('DEBUG: user.email:', getattr(user, 'email', None))
    print('DEBUG: user.role:', getattr(user, 'role', None))
    print('DEBUG: request.method:', request.method)
    print('DEBUG: request.data:', request.data)
    if not user.is_authenticated:
        raise PermissionDenied('You must be logged in to donate.')
    # Anyone authenticated can donate now
    data = request.data
    donation_type = data.get('donation_type')
    if not donation_type:
        return Response({'error': 'Donation type is required.'}, status=status.HTTP_400_BAD_REQUEST)
    donation = Donation.objects.create(user=user, donation_type=donation_type)
    if donation_type == 'money':
        amount = data.get('amount')
        region = data.get('region')
        purpose = data.get('purpose')
        money = MoneyDonation.objects.create(donation=donation, amount=amount, region=region, purpose=purpose)
        # Create Razorpay order
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        order_data = {
            'amount': int(float(amount) * 100),  # Razorpay expects paise
            'currency': 'INR',
            'payment_capture': 1
        }
        order = client.order.create(data=order_data)
        money.razorpay_order_id = order['id']
        money.save()
        return Response({
            'order_id': order['id'],
            'razorpay_key': settings.RAZOR_KEY_ID,
            'donation_id': donation.id
        }, status=status.HTTP_201_CREATED)
    elif donation_type == 'items':
        item_type = data.get('item_type')
        target_group = data.get('target_group')
        address = data.get('address')
        people_count = data.get('people_count')
        image = request.FILES.get('image')
        ItemDonation.objects.create(donation=donation, item_type=item_type, target_group=target_group, address=address, people_count=people_count, image=image)
        donation.status = 'completed'
        donation.save()
        return Response({'message': 'Item donation recorded.'}, status=status.HTTP_201_CREATED)
    elif donation_type == 'food':
        food_type = data.get('food_type')
        target_group = data.get('target_group')
        stock = data.get('stock')
        address = data.get('address')
        FoodDonation.objects.create(donation=donation, food_type=food_type, target_group=target_group, stock=stock, address=address)
        donation.status = 'completed'
        donation.save()
        return Response({'message': 'Food donation recorded.'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Invalid donation type.'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def verify_payment(request):
    data = request.data
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')
    
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return Response({'error': 'Missing payment verification data'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        money_donation = MoneyDonation.objects.get(razorpay_order_id=razorpay_order_id)
        
        # Verify payment with Razorpay
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params)
        except razorpay.errors.SignatureVerificationError as e:
            return Response({'error': 'Invalid payment signature'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Update donation status
        money_donation.razorpay_payment_id = razorpay_payment_id
        money_donation.payment_status = 'paid'
        money_donation.save()
        
        money_donation.donation.status = 'completed'
        money_donation.donation.save()
        
        return Response({
            'message': 'Payment verified successfully',
            'donation_id': money_donation.donation.id,
            'amount': money_donation.amount
        }, status=status.HTTP_200_OK)
        
    except MoneyDonation.DoesNotExist:
        return Response({'error': 'Donation not found'}, 
                       status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_donations(request):
    """Get all donations made by the current user"""
    user = request.user
    if user.is_authenticated:
        donations = Donation.objects.filter(user=user).order_by('-created_at')
        
        donation_list = []
        for donation in donations:
            donation_data = {
                'id': donation.id,
                'type': donation.donation_type,
                'status': donation.status,
                'created_at': donation.created_at,
                'details': {}
            }
            
            # Get specific donation details based on type
            if donation.donation_type == 'money':
                try:
                    money = MoneyDonation.objects.get(donation=donation)
                    donation_data['details'] = {
                        'amount': money.amount,
                        'region': money.region,
                        'purpose': money.purpose,
                        'payment_status': money.payment_status
                    }
                except MoneyDonation.DoesNotExist:
                    pass
            elif donation.donation_type == 'items':
                try:
                    item = ItemDonation.objects.get(donation=donation)
                    donation_data['details'] = {
                        'item_type': item.item_type,
                        'target_group': item.target_group,
                        'address': item.address,
                        'people_count': item.people_count,
                        'image': item.image.url if item.image else None
                    }
                except ItemDonation.DoesNotExist:
                    pass
            elif donation.donation_type == 'food':
                try:
                    food = FoodDonation.objects.get(donation=donation)
                    donation_data['details'] = {
                        'food_type': food.food_type,
                        'target_group': food.target_group,
                        'stock': food.stock,
                        'address': food.address
                    }
                except FoodDonation.DoesNotExist:
                    pass
                    
            donation_list.append(donation_data)
            
        return Response(donation_list, status=status.HTTP_200_OK)
    return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_donation_by_id(request, donation_id):
    """Get a specific donation by ID"""
    try:
        # First check if the donation exists
        donation = Donation.objects.get(id=donation_id)
        
        # Create the base donation data
        donation_data = {
            'id': donation.id,
            'type': donation.donation_type,
            'status': donation.status,
            'created_at': donation.created_at,
            'user': {
                'name': donation.user.name,
                'email': donation.user.email
            },
            'details': {}
        }
        
        # Get specific donation details based on type
        if donation.donation_type == 'money':
            try:
                money = MoneyDonation.objects.get(donation=donation)
                donation_data['details'] = {
                    'amount': money.amount,
                    'region': money.region,
                    'purpose': money.purpose,
                    'payment_status': money.payment_status,
                    'razorpay_order_id': money.razorpay_order_id,
                    'razorpay_payment_id': money.razorpay_payment_id
                }
            except MoneyDonation.DoesNotExist:
                pass
        elif donation.donation_type == 'items':
            try:
                item = ItemDonation.objects.get(donation=donation)
                donation_data['details'] = {
                    'item_type': item.item_type,
                    'target_group': item.target_group,
                    'address': item.address,
                    'people_count': item.people_count,
                    'image': item.image.url if item.image else None
                }
            except ItemDonation.DoesNotExist:
                pass
        elif donation.donation_type == 'food':
            try:
                food = FoodDonation.objects.get(donation=donation)
                donation_data['details'] = {
                    'food_type': food.food_type,
                    'target_group': food.target_group,
                    'stock': food.stock,
                    'address': food.address
                }
            except FoodDonation.DoesNotExist:
                pass
                
        return Response(donation_data, status=status.HTTP_200_OK)
    except Donation.DoesNotExist:
        return Response({'error': 'Donation not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
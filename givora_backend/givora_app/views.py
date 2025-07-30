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

# Create your views here.

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
                # Get role from user model
                role = user.role
                # For admin users
                if user.email == 'admin@gmail.com' or user.is_superuser:
                    role = 'Admin'
                return JsonResponse({'message': 'Login successful!', 'role': role}, status=200)
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
@api_view(['POST'])
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
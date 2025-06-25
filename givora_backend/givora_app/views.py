from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json

# Create your views here.

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('fullName', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            phone = data.get('phone', '').strip()
            user_role = data.get('userRole', '').strip()

            if not all([full_name, email, password, phone, user_role]):
                return JsonResponse({'error': 'All fields are required.'}, status=400)
            if len(password) < 8:
                return JsonResponse({'error': 'Password must be at least 8 characters.'}, status=400)
            if User.objects.filter(username=email).exists():
                return JsonResponse({'error': 'User already exists.'}, status=400)

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name,
            )
            # Optionally, save phone and user_role in a profile model or as user.last_name
            user.last_name = user_role  # Store user_role in last_name for demo
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
                # Determine role
                if user.username == 'admin@gmail.com':
                    role = 'Admin'
                elif (user.last_name or '').lower() == 'volunteer' or 'volunteer' in (user.first_name or '').lower():
                    role = 'Volunteer'
                else:
                    role = 'User'
                return JsonResponse({'message': 'Login successful!', 'role': role}, status=200)
            else:
                return JsonResponse({'error': 'Invalid credentials.'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

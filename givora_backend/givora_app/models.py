from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('Donor', 'Donor'),
        ('Volunteer', 'Volunteer'),
        ('Receiver', 'Receiver'),
    ]
    
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    password = models.CharField(max_length=128)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    address = models.TextField()
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Donor')
    
    # Override username field to use email
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname', 'phone_number', 'role']

    objects = UserManager()
    
    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.email}) - {self.role}"
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Donation(models.Model):
    DONATION_TYPE_CHOICES = [
        ('money', 'Money'),
        ('items', 'Items'),
        ('food', 'Food'),
        ('grocery', 'Grocery'),
        ('medicine', 'Medicine'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donations')
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.email} - {self.donation_type} - {self.status}"

class MoneyDonation(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='money_details')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=100)
    purpose = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='created')

    def __str__(self):
        return f"MoneyDonation: {self.amount} for {self.region} ({self.purpose})"

class ItemDonation(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='item_details')
    item_type = models.CharField(max_length=100)
    target_group = models.CharField(max_length=100)
    address = models.TextField()
    people_count = models.PositiveIntegerField()
    image = models.ImageField(upload_to='item_donations/')

    def __str__(self):
        return f"ItemDonation: {self.item_type} for {self.target_group}"

class FoodDonation(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='food_details')
    food_type = models.CharField(max_length=100)
    target_group = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    address = models.TextField()

    def __str__(self):
        return f"FoodDonation: {self.food_type} for {self.target_group}"

class GroceryDonation(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='grocery_details')
    grocery_type = models.CharField(max_length=100)
    target_group = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    address = models.TextField()

    def __str__(self):
        return f"GroceryDonation: {self.grocery_type} for {self.target_group}"

class MedicineDonation(models.Model):
    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='medicine_details')
    medicine_type = models.CharField(max_length=100)
    target_group = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    address = models.TextField()

    def __str__(self):
        return f"MedicineDonation: {self.medicine_type} for {self.target_group}"


class Orphanage(models.Model):
    name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=0)
    current_children_count = models.PositiveIntegerField(default=0)
    primary_needs = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='orphanages/', blank=True, null=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orphanages_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orphanage'
        ordering = ['-created_at']

    def __str__(self):
        return f"Orphanage: {self.name}"
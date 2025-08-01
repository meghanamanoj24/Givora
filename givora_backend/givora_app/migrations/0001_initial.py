# Generated by Django 4.2.23 on 2025-07-17 09:54

from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, validators=[django.core.validators.EmailValidator()])),
                ('password', models.CharField(max_length=128)),
                ('firstname', models.CharField(max_length=100)),
                ('lastname', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('photo', models.ImageField(blank=True, null=True, upload_to='user_photos/')),
                ('phone_number', models.CharField(max_length=15)),
                ('image', models.ImageField(blank=True, null=True, upload_to='user_images/')),
                ('role', models.CharField(choices=[('Donor', 'Donor'), ('Volunteer', 'Volunteer'), ('Receiver', 'Receiver')], default='Donor', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donation_type', models.CharField(choices=[('money', 'Money'), ('items', 'Items'), ('food', 'Food')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MoneyDonation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('region', models.CharField(max_length=100)),
                ('purpose', models.CharField(max_length=100)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_status', models.CharField(default='created', max_length=20)),
                ('donation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='money_details', to='givora_app.donation')),
            ],
        ),
        migrations.CreateModel(
            name='ItemDonation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(max_length=100)),
                ('target_group', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('people_count', models.PositiveIntegerField()),
                ('image', models.ImageField(upload_to='item_donations/')),
                ('donation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='item_details', to='givora_app.donation')),
            ],
        ),
        migrations.CreateModel(
            name='FoodDonation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_type', models.CharField(max_length=100)),
                ('target_group', models.CharField(max_length=100)),
                ('stock', models.PositiveIntegerField()),
                ('address', models.TextField()),
                ('donation', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='food_details', to='givora_app.donation')),
            ],
        ),
    ]

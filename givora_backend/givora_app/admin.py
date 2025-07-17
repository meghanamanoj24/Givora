from django.contrib import admin
from .models import User, Donation, MoneyDonation, ItemDonation, FoodDonation

# Register your models here.
admin.site.register(User)
admin.site.register(Donation)
admin.site.register(MoneyDonation)
admin.site.register(ItemDonation)
admin.site.register(FoodDonation)

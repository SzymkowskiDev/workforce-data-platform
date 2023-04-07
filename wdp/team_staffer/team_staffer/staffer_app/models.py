from django.db import models
from djmoney.models.fields import MoneyField

# Create your models here.
class Staffer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    last_role = models.CharField(max_length=100, default='')
    preferred_role = models.CharField(max_length=100)
    salary = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')
    joined_on = models.DateField(auto_now_add=True) 
    phone_number = models.CharField(max_length=100, default='')
    specializations = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    #avatar = models.ImageField(upload_to='staffer_avatar')


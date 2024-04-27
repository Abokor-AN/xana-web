from django.db import models
from django.utils import timezone

from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Create your models here.
class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    validity_duration = models.IntegerField()  # Durée de validité en jours
    price_dollars = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name

    @receiver(post_migrate)
    def create_default_instance(sender, **kwargs):
        if sender.name == 'home':
            Subscription.objects.get_or_create(name="Free Plan", validity_duration=30, price_dollars=0.0)
            Subscription.objects.get_or_create(name="Admin Plan", validity_duration=3660, price_dollars=0.0)
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    subscription = models.ForeignKey('Subscription', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.email

    @receiver(post_migrate)
    def create_default_instance(sender, **kwargs):
        if sender.name == 'home':
            Users.objects.get_or_create(email="abokor.ahmed.kadar.nour@gmail.com", full_name="Abokor Ahmed-Kadar Nour", is_staff=True, subscription=Subscription.objects.get(name="Admin Plan"))

class Password(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=128)
    user = models.ForeignKey('Users', on_delete=models.SET_NULL, null=True, blank=True)

    @receiver(post_migrate)
    def create_default_instance(sender, **kwargs):
        if sender.name == 'home':
            Password.objects.get_or_create(password="Z5Map69XrIpwX6mQZ/jB0yAbeU9dZ4iAN3lxwfBj648=",user=Users.objects.get(email="abokor.ahmed.kadar.nour@gmail.com"))

class ResetPassword(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255)
    expiration_date = models.DateTimeField()
    user = models.ForeignKey('Users', on_delete=models.SET_NULL, null=True, blank=True)

class License(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    license_id = models.CharField(max_length=255)

    def __str__(self):
        return self.license_id
from django.core.serializers import serialize
from .models import Users

from datetime import datetime

class UsersSerializers:

    def is_valid(self, data):
        
        # Vérifier que 'email' est une chaîne non vide
        if 'email' not in data or not isinstance(data['email'], str) or not data['email']:
            return False
        
        # Vérifier que 'full_name' est une chaîne
        if 'full_name' in data and not isinstance(data['full_name'], str):
            return False
        
        # Toutes les validations ont réussi, donc les données sont valides
        return True

    def to_json(self, queryset):
        return serialize('json', queryset)

    def from_json(self, data):
        return deserialize('json', data)

    def to_dict(self, obj):
        return {
            'id': obj.id,
            'email': obj.email,
            'password': obj.password,
            'full_name': obj.full_name,
            'date_joined': obj.date_joined,
            'is_staff': obj.is_staff,
            'subscription': obj.subscription
        }

    def from_dict(self, data):

        if not self.is_valid(data):  # Appel de is_valid avec 'data' en argument
            raise ValueError('Invalid data')

        now = datetime.now()
            
        return Users(
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('full_name', ''),
            date_joined=now.strftime("%Y-%m-%d %H:%M:%S"),
            is_staff=data.get('is_staff', False),
            subscription=data.get('subscription', None)
        )
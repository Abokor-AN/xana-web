from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# Create your views here.
def index(request):
    response = "secret_key = " + str(settings.ALLOWED_HOSTS)
    return HttpResponse(response)
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def index(request):
    return JsonResponse({"Msg": "Hello, world. You're at the hook index."})
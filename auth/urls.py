from django.urls import path

from . import views

urlpatterns = [
    path("signup", views.signup, name="signup"),
    path("signin", views.signin, name="signin"),
    path("reset_password", views.initialize_reset_password, name="initialize_reset_password"),
    path("reset_password/<str:token>", views.reset_password, name="reset_password"),
    path("public_key", views.get_public_key, name="get_public_key")
]
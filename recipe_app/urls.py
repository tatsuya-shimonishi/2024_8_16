from django.urls import path
from . import views
from .views import Login, SignupView

# app_name = 'recipe_app'

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", Login.as_view(), name="login"),
    # path("signup", views.signup_view, name="signup"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("recipe_list/", views.recipe_list, name="recipe_list"),
    path("recipe_detail/", views.recipe_detail, name="recipe_detail"),
]
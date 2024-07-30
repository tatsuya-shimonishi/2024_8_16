from django.urls import path
from . import views
from .views import SignupView, CustomLoginView
from django.contrib.auth import views as auth_views

# app_name = 'recipe_app'

urlpatterns = [
    path("", views.index, name="index"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("signup/", SignupView.as_view(), name="signup"),
    path("recipe_list/", views.recipe_list, name="recipe_list"),
    path("recipe_detail/", views.recipe_detail, name="recipe_detail"),
]
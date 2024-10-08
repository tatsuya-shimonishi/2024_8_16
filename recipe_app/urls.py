from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", index, name="index"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("signup/", SignupView.as_view(), name="signup"),
    path("recipe_list/", recipe_list, name="recipe_list"),
    path("recipe_detail/<int:recipe_id>/", recipe_detail, name="recipe_detail"),
    path('paginate/', paginate_view, name='paginate_view'),
    path('add_favorite/', add_favorite, name='add_favorite'),
    path('delete_favorite/', delete_favorite, name='delete_favorite'),
    path('scraping/', scraping, name='scraping'),
]
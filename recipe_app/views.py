from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *

@login_required
def index(request):
    params = {
        'title': 'ホーム'
    }
    return render(request, 'recipe_app/index.html', params)

@login_required
def recipe_list(request):
    params = {
        'title': 'レシピ一覧'
    }
    return render(request, 'recipe_app/recipe_list.html', params)

@login_required
def recipe_detail(request):
    params = {
        'title': '作り方'
    }
    return render(request, 'recipe_app/recipe_detail.html', params)

# ログイン
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'recipe_app/login.html'
    
    # フォームが正常に検証された場合
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        # ユーザー認証（成功：obj、失敗：none）
        user = authenticate(self.request, username=username, password=password)
        # ログイン
        if user is not None:
            login(self.request, user)
        return response

# 新規登録
class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "recipe_app/signup.html" 
    # ユーザー登録後のリダイレクト先ページ
    success_url = reverse_lazy("login")

    # フォームが正常に検証された場合
    def form_valid(self, form):
        # フォームへの入力内容を保存
        response = super().form_valid(form)
        return response




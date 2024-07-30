from typing import Any
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *
from .forms import *

def index(request):
    params = {
        'title': 'ホーム'
    }
    return render(request, 'recipe_app/index.html', params)

def recipe_list(request):
    params = {
        'title': 'レシピ一覧'
    }
    return render(request, 'recipe_app/recipe_list.html', params)
    
def recipe_detail(request):
    params = {
        'title': '作り方'
    }
    return render(request, 'recipe_app/recipe_detail.html', params)

# ログイン
class Login(TemplateView):
    def __init__(self) -> None:
        self.params = {
            'title': 'ログイン',
            'form': LoginForm(),
        }
    
    def get(self, request):
        return render(request, "recipe_app/login.html", self.params)
    
    def post(self, request):
        return render(request, "recipe_app/login.html", self.params)

# 新規登録
# class Signup(TemplateView):
#     def __init__(self) -> None:
#         self.params = {
#             'title': '新規登録',
#             'form': UserForm(),
#             'alert': '',
#         }
    
#     def get(self, request):
#         return render(request, "recipe_app/signup.html", self.params)
    
#     def post(self, request):
#         obj = CustomUser()
#         form = UserForm(request.POST, instance=obj)
#         form.save()
#         self.params["alert"] = f"登録完了！（名前：{request.POST['username']}）"
#         return render(request, "recipe_app/signup.html", self.params)


# 試作--------------------------

from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import SignUpForm

# ユーザー登録
class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "recipe_app/signup.html" 
    # ユーザー登録後のリダイレクト先ページ
    success_url = reverse_lazy("index")

    """ ユーザー作成後にそのままログイン状態にする処理 """
    # フォームが正常に検証された場合
    def form_valid(self, form):
        # フォームへの入力内容を保存
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        # ユーザー認証（成功：obj、失敗：none）
        user = authenticate(self.request, username=username, password=password)
        # ログイン
        if user is not None:
            login(self.request, user)
            print("OK")
        return response

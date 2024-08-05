import random
from time import sleep
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from .scraper import *

""" 定数 """
COOKING_CATEGORY_MAIN   = "主菜"
COOKING_CATEGORY_SUB    = "副菜"
COOKING_CATEGORY_SOUP   = "汁物"
COOKING_CATEGORY_DESERT = "デザート"
COOKING_CATEGORY_LIST   = {
    "main"  : COOKING_CATEGORY_MAIN,
    "sub"   : COOKING_CATEGORY_SUB,
    "soup"  : COOKING_CATEGORY_SOUP,
    "desert": COOKING_CATEGORY_DESERT,
}

""" ホーム """
@login_required
def index(request):
    params = {
        'title': 'ホーム'
    }
    
    """ レシピのスクレイピング """
    # search_word=""
    # cooking_category_word = "主菜"
    # get_data_count = 10
    # cooking_category = CookingCategory.objects.get(name=cooking_category_word).name
    # recipe_detail_url = get_recipe_list(search_word, cooking_category)
    # i = 0
    # for i in range(get_data_count):
    #     get_recipe_detail(recipe_detail_url[i]["recipe_detail_url"], cooking_category)
    #     # スクレイピングを1秒待つ
    #     sleep(1)
    
    """ DBよりレシピの取得 """
    # 各レシピを取得（主菜、副菜、汁物、デザート）
    for key, value in COOKING_CATEGORY_LIST.items():
        cooking_category = CookingCategory.objects.get(name=value)
        # 料理区分を指定してレシピ一覧を取得
        main_records = list(Recipe.objects.filter(cooking_category=cooking_category))
        # レシピ一覧からランダムに1件抽出
        main_record = random.choice(main_records)
        params[key] = main_record
    
    return render(request, 'recipe_app/index.html', params)

""" レシピ一覧 """
@login_required
def recipe_list(request):
    params = {
        'title': 'レシピ一覧'
    }
    return render(request, 'recipe_app/recipe_list.html', params)

""" 作り方 """
@login_required
def recipe_detail(request):
    params = {
        'title': '作り方'
    }    
    return render(request, 'recipe_app/recipe_detail.html', params)

""" ログイン """
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

""" 新規登録 """
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




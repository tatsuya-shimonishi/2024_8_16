from pprint import pprint
import random
from time import sleep
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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
RECIPE_GET_COUNT = 30

""" DBよりレシピの取得 """
def get_recipe(request, params, get_count=RECIPE_GET_COUNT):
    user = request.user
    
    # 各レシピを取得（主菜、副菜、汁物、デザート）
    for key, value in COOKING_CATEGORY_LIST.items():
        records = []
        recipe_list = []
        
        # 料理区分を指定してレシピ一覧を取得
        cooking_category = CookingCategory.objects.get(name=value)
        records = list(Recipe.objects.filter(cooking_category=cooking_category)[:get_count])
        
        # お気に入り登録されているかの判定を追加
        for record in records:
            is_favorite = Favorite.objects.filter(custom_user=user, recipe=record).exists()
            recipe_list.append({
                "recipe": record,
                "is_favorite": is_favorite
            })
            
        params[key] = recipe_list
    
    return params

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
    
    # 各レシピのリストを取得（主菜、副菜、汁物、デザート）
    recipe_list = get_recipe(request, params)
    
    for key in COOKING_CATEGORY_LIST.keys():
        # レシピリストからランダムに1件抽出
        record = random.choice(recipe_list[key])
        params[key] = record
    
    return render(request, 'recipe_app/index.html', params)

""" レシピ一覧 """
@login_required
def recipe_list(request):
    params = {
        'title': 'レシピ一覧'
    }
    
    # DBよりレシピの取得
    params = get_recipe(request, params)
    
    return render(request, 'recipe_app/recipe_list.html', params)

""" 作り方 """
@login_required
def recipe_detail(request, recipe_id):
    params = {
        'title': '作り方'
    }

    # DBよりレシピの取得
    recipe_obj = Recipe.objects.get(id=recipe_id)
    # 材料を取得
    ingredients_obj = recipe_obj.ingredients_set.all()
    # 作り方を取得
    instruction_obj = recipe_obj.instruction_set.all()

    # お気に入り登録されているか
    user = request.user
    is_favorite = Favorite.objects.filter(custom_user=user, recipe=recipe_obj).exists()
    
    params = {
        'recipe': recipe_obj,
        'ingredients': ingredients_obj,
        'instruction': instruction_obj,
        'is_favorite': is_favorite,
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

""" ページネーション取得（非同期通信） """
def paginate_view(request):
    page_number = request.GET.get('page', 1)
    tab = request.GET.get('tab', 'default')  
    items_per_page = 6 
    user = request.user
    recipe_list = []
    
    # タブに応じたクエリセットを生成
    if tab == 'tab1':
        category_name = COOKING_CATEGORY_MAIN
    elif tab == 'tab2':
        category_name = COOKING_CATEGORY_SUB
    elif tab == 'tab3':
        category_name = COOKING_CATEGORY_SOUP
    elif tab == 'tab4':
        category_name = COOKING_CATEGORY_DESERT
    
    # 料理区分を条件にレシピレコードを取得
    cooking_category = CookingCategory.objects.get(name=category_name)
    records = Recipe.objects.filter(cooking_category=cooking_category)
    
    # ページネーターオブジェクトを取得
    paginator = Paginator(records, items_per_page)
    page = paginator.get_page(page_number)
    records = list(page.object_list.values())
    
    # お気に入り登録されているかの判定を追加
    for record in records:
        is_favorite = Favorite.objects.filter(custom_user=user, recipe_id=record["id"]).exists()
        recipe_list.append({
            "recipe": record,
            "is_favorite": is_favorite
        })

    data = {
        'items': recipe_list,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'next_page_number': page.next_page_number() if page.has_next() else None,
        'previous_page_number': page.previous_page_number() if page.has_previous() else None,
        'num_pages': paginator.num_pages,
    }

    return JsonResponse(data)

""" お気に入り：追加 """
@login_required
def add_favorite(request):
    response_data = {
        "process": "add NG...",
        'custom_user': "",
        'recipe': "",
    }
    
    if request.method == 'POST':
        user_id = request.user.id
        item_id = request.POST.get('item_id')
        
        custom_user_name_obj = CustomUser.objects.get(id=user_id)
        recipe_obj = Recipe.objects.get(id=item_id)
        
        Favorite.objects.update_or_create(
            custom_user = custom_user_name_obj,
            recipe = recipe_obj,
            defaults = {
                'custom_user': custom_user_name_obj,
                'recipe': recipe_obj,
            }
        )
        
        response_data = {
            "process": "add",
            'custom_user': custom_user_name_obj.username,
            'recipe': recipe_obj.name,
        }
        
    return JsonResponse(response_data)

""" お気に入り：削除 """
@login_required
def delete_favorite(request):
    response_data = {
        "process": "delete NG...",
        'custom_user': "",
        'recipe': "",
    }
    
    if request.method == 'POST':
        user_id = request.user.id
        item_id = request.POST.get('item_id')
        
        custom_user_name_obj = CustomUser.objects.get(id=user_id)
        recipe_obj = Recipe.objects.get(id=item_id)
        
        Favorite.objects.filter(
            custom_user = custom_user_name_obj,
            recipe = recipe_obj,
        ).delete()
        
        response_data = {
            "process": "delete",
            'custom_user': custom_user_name_obj.username,
            'recipe': recipe_obj.name,
        }
   
    return JsonResponse(response_data)
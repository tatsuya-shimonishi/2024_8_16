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
from .constant import *
from .scraper import *
from .favorite_flg_add_or_delete import favorite_flg_add_or_delete
from .get_recipe import get_recipe


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


""" ホーム """
@login_required
def index(request):
    params = {
        'title': 'ホーム'
    }
    recipe_get_count = 1
    
    # 各レシピのリストを取得（主菜、副菜、汁物、デザート）
    recipe_list = get_recipe(request, params, get_count=recipe_get_count)
    
    for key in COOKING_CATEGORY_LIST.keys():
        # レシピが存在しない場合はスキップ
        if key not in recipe_list:
            continue
        
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

    # お気に入り登録されているか確認
    user = request.user
    is_favorite = Favorite.objects.filter(custom_user=user, recipe=recipe_obj).exists()
    
    add_params = {
        'recipe': recipe_obj,
        'ingredients': ingredients_obj,
        'instruction': instruction_obj,
        'is_favorite': is_favorite,
    }
    params.update(add_params)
    
    return render(request, 'recipe_app/recipe_detail.html', params)


""" お気に入り：追加 """
@login_required
def add_favorite(request):
    response_data = {
        "process": "add NG...",
        'custom_user': "",
        'recipe': "",
    }
    
    if request.method == 'POST':
        response_data = favorite_flg_add_or_delete(request, ADD)
        
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
        response_data = favorite_flg_add_or_delete(request, DELETE)
   
    return JsonResponse(response_data)


""" ページネーション取得（非同期通信） """
def paginate_view(request):
    page_number = request.GET.get('page', 1)
    tab = request.GET.get('tab', 'default')
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
    
    # 料理区分とユーザを条件にレシピレコードを取得
    cooking_category = CookingCategory.objects.get(name=category_name)
    records = Recipe.objects.filter(cooking_category=cooking_category, id__in=Favorite.objects.filter(custom_user=user).values_list('recipe_id', flat=True)).order_by('id')[:RECIPE_LIST_COUNT]
    
    # ページネーターオブジェクトを取得
    paginator = Paginator(records, RECIPE_LIST_PAGE)
    page = paginator.get_page(page_number)
    records = list(page.object_list.values())
    
    # お気に入り登録されているかの判定
    for record in records:
        is_favorite = Favorite.objects.filter(custom_user=user, recipe_id=record["id"], favorite_flg=True).exists()
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


""" レシピデータのスクレイピング """
@login_required
def scraping(request):
    params = {
        "title": "レシピ一覧の更新",
        "initial_display": True,
    }
    
    if request.method == 'POST':
        recipe_data = {}
        search_words = {}
        
        # お気に入り登録以外のレシピを削除
        delete_not_favorite_recipe(request)
        
        # 料理区分を全て取得
        cooking_category_obj_list = CookingCategory.objects.all()
        
        # 料理区分ごとにレシピを取得しDBへ登録
        for cooking_category_obj in cooking_category_obj_list:
            i = 0
            cooking_category = cooking_category_obj.name
            recipe_data[cooking_category] = {}
            
            # お気に入り情報より検索ワードを取得
            search_word = get_liking_search_word(request, cooking_category_obj)
            
            # 検索ワードと料理区分を指定してレシピのURLリストを取得
            recipe_detail_url = get_recipe_url_list(search_word, cooking_category, SCRAPING_COUNT)
            
            search_words[cooking_category] = search_word if search_word else "※キーワードなし"
            
            if not recipe_detail_url:
                continue
        
            # レシピデータを取得し各DBに登録
            for i in range(SCRAPING_COUNT):
                # urlが設定されていない場合は当料理区分の処理を抜ける
                if not recipe_detail_url[i:]:
                    break
                
                # レシピ詳細ページを取得
                recipe_object = get_recipe_detail(request, recipe_detail_url[i]["recipe_detail_url"], cooking_category_obj)
                
                # 取得エラーはスキップ
                if not recipe_object:
                    continue
                
                recipe_data[cooking_category][recipe_object.pk] = {}
                recipe_data[cooking_category][recipe_object.pk] = recipe_object.name
                
                # スクレイピングを1秒待つ
                sleep(SCRAPING_SLEEP)
                
        tmp = {
            "initial_display": False,
            "result": SUCCESS,
            "message": "スクレイピング完了！",
            "recipe_data": recipe_data,
            "search_words": search_words,
        }
        params.update(tmp)
            
    return render(request, 'recipe_app/scraping.html', params)
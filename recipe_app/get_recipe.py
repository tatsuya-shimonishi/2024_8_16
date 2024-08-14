from .constant import *
from .models import *

""" DBよりレシピの取得 """
def get_recipe(request, params, get_count):
    user = request.user
    
    # 各レシピを取得（主菜、副菜、汁物、デザート）
    for key, value in COOKING_CATEGORY_LIST.items():
        records = []
        recipe_list = []
        
        # 料理区分を指定してランダムにレシピ一覧を取得
        cooking_category = CookingCategory.objects.get(name=value)
        
        # ユーザーに紐づくレシピを取得
        records = list(Recipe.objects.filter(cooking_category=cooking_category, id__in=Favorite.objects.filter(custom_user=user).values_list('recipe_id', flat=True)).order_by('?')[:get_count])
        
        # 取得できなかった場合はスキップ
        if not records:
            continue
        
        # お気に入り登録されているかの判定を追加
        for record in records:
            is_favorite = Favorite.objects.filter(custom_user=user, recipe=record, favorite_flg=True).exists()
            recipe_list.append({
                "recipe": record,
                "is_favorite": is_favorite
            })
            
        params[key] = recipe_list
    
    return params
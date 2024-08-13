from .models import *

def favorite_flg_add_or_delete(request, param):
    user_id = request.user.id
    item_id = request.POST.get('item_id')
    
    # ユーザーとレシピのオブジェクトを作成
    custom_user_name_obj = CustomUser.objects.get(id=user_id)
    recipe_obj = Recipe.objects.get(id=item_id)
    
    # お気に入り追加
    Favorite.objects.update_or_create(
        custom_user = custom_user_name_obj,
        recipe = recipe_obj,
        defaults = {
            'custom_user': custom_user_name_obj,
            'recipe': recipe_obj,
            'favorite_flg': param,
        }
    )
    
    if param:
        process = "add"
    else:
        process = "delete"

    response_data = {
        "process": process,
        'custom_user': custom_user_name_obj.username,
        'recipe': recipe_obj.name,
    }
    
    return response_data
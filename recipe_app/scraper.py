import re
import requests
import os
import numpy as np
from time import sleep
from bs4 import BeautifulSoup
from recipe_app.models import *
from django.core.files.base import ContentFile
from django.db.models import Q
from .models import *
from .constant import *

""" レシピのURL一覧を取得 """
def get_recipe_url_list(search_word, cooking_category, recipe_get_count):
    
    recipes = []
    search_query = cooking_category + " " + search_word
    range_max = (recipe_get_count % 11) + 2
    
    for i in range(1, range_max):
        base_url = 'https://cookpad.com/search/'
        page = ""
        
        # 2ページ以降はURLにページ数のパラメータを設定
        if i > 1:
            page = f"?page={i}"
        
        # 検索URLを作成
        search_url = base_url + requests.utils.quote(search_query) + page
        
        # 検索結果ページをスクレイピング
        response = requests.get(search_url)
        
        if response.status_code != 200:
            break
        
        # 取得結果を解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.recipe-preview'):
            title = item.select_one('.recipe-title').get_text(strip=True)
            url = item.select_one('a')['href']
            
            recipes.append({
                'title': title,
                'recipe_detail_url': url
            })
            
            # スクレイピングを待つ
            sleep(SCRAPING_SLEEP)
        
    return recipes


""" 画像を保存 """
def save_image(img_url, model_obj):
    
    # 画像をダウンロード
    img_response = requests.get(img_url)
    # レスポンスから画像のバイナリデータを取得
    image_content = ContentFile(img_response.content)
    
    # 画像のファイル名をURLから取得
    tmp_img_filename = os.path.basename(img_url)
    img_filename = tmp_img_filename.split("?")[0] + '.webp'
    
    # 画像を保存
    model_obj.img.save(img_filename, image_content, save=True)


""" レシピ詳細を取得 """
def get_recipe_detail(request, recipe_detail_url, cooking_category_obj):
    base_url = 'https://cookpad.com'
    request_url = base_url + recipe_detail_url
    response = requests.get(request_url)
        
    if response.status_code != 200:
        return False
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 作成者名管理 ---------------------------------
    # 作者名取得
    recipe_author_name = soup.select_one('#recipe_author_name').get_text(strip=True)
    
    # 更新or登録
    Author.objects.update_or_create(
        name = recipe_author_name,  # チェックする条件
        defaults = {'name': recipe_author_name}  # 新規作成または更新する場合のデフォルト値
    )
    
    # レシピ管理 -----------------------------------
    # レシピ名
    title =  soup.select_one(".recipe-title").get_text(strip=True)
    # 作成者ID
    author_obj = Author.objects.get(name = recipe_author_name)
    # 食数
    servings = ""
    ingredients_tmp = soup.select_one('#ingredients')
    data = ingredients_tmp.select_one(".servings_for")
    if data:
        servings = data.get_text(strip=True)
    # メモ
    memo_tmp = soup.select_one('#memo_wrapper')
    memo = memo_tmp.select_one('.text_content').get_text(strip=True)
    
    # レシピレコードを更新or登録
    recipe_object, created =Recipe.objects.update_or_create(
        name = title,  # チェックする条件
        defaults = {
            'name': title,
            'url': request_url,
            'cooking_category': cooking_category_obj,
            'author': author_obj,
            'servings': servings,
            'memo': memo,
        }
    )
    
    # レシピ画像
    img_tmp = soup.select_one('#main-photo')
    img_url = img_tmp.select_one('img')['src']
    
    # 画像を保存
    save_image(img_url, recipe_object)   
    
    # 食材名管理、材料管理 --------------------------------------
    # 食材名、分量のリスト
    ingredients_list = soup.select(".ingredient_row")
    count = 0
    
    # レシピ管理をオブジェクト化
    recipe_obj = Recipe.objects.get(url=request_url)
    
    # 1レコードずつ食材名、分量を取得
    for ingredients_data in ingredients_list:
        count += 1
        name_data = None
        data = None
        amount = None
        ingredients_name = None
        
        # 食材名
        name_data = ingredients_data.select_one(".ingredient_name")
        if name_data:
            ingredients_name = name_data.get_text(strip=True)
        else:
            ingredients_data = ingredients_data.select_one(".ingredient_category")
            if ingredients_data:
                ingredients_name = ingredients_data.get_text(strip=True)
            else:
                continue
        
        # 分量
        data = ingredients_data.select_one(".ingredient_quantity")
        if data:
            amount = data.get_text(strip=True)

        # 食材名管理の更新or登録
        IngredientName.objects.update_or_create(
            name = ingredients_name,  # チェックする条件
            defaults = {'name': ingredients_name}  # 新規作成または更新する場合のデフォルト値
        )
        
        # 食材名管理をオブジェクト化
        ingredients_name_obj = IngredientName.objects.get(name=ingredients_name)
        
        # 材料管理のレコードを更新or登録
        Ingredients.objects.update_or_create(
            recipe=recipe_obj,
            order=count,
            defaults = {
                'recipe': recipe_obj,
                'ingredientName': ingredients_name_obj,
                'amount': amount,
                'order': count,
            }
        )
        
    # 作り方管理 ---------------------------------------
    step_order = 0
    
    # 作り方全体データを取得
    steps_data = soup.select_one('#steps')
    instruction_data = steps_data.select('.instruction')
    
    # 順番、画像、詳細の各レコードを取得
    for step_data in instruction_data:
        step_order += 1
        step_text = step_data.select_one('.step_text').get_text(strip=True)
    
        # 作り方管理のレコードを更新or登録
        instruction_object, created = Instruction.objects.update_or_create(
            recipe=recipe_obj,
            order=step_order,
            defaults = {
                'recipe': recipe_obj,
                'order': step_order,
                'detail': step_text,
            }
        )
        
        # 画像URLを取得
        img_url = step_data.select_one('img')
        
        if img_url:
            # 画像を保存
            save_image(img_url['src'], instruction_object)
        
    # お気に入り管理 ---------------------------------------
    user_obj = request.user
    
    # お気に入り管理のレコードを登録(存在する場合は何もしない)
    Favorite.objects.get_or_create(
        custom_user=user_obj,
        recipe=recipe_obj,
        defaults = {
            'custom_user': user_obj,
            'recipe': recipe_obj,
            'favorite_flg': False,
        }
    )

    return recipe_object


""" 検索ワードを取得 """
def get_liking_search_word(request, cooking_category_obj):
    ingredients_weight = {}
    search_word = ""
    user_obj = request.user
    
    # 除外食材名
    exclude_words = [
        '水', '酒', '塩', 'しお', '味醂', 'みりん', '砂糖', 'さとう', '醤油', 'しょうゆ', '味噌', 'みそ',
        'ごま油', 'サラダ油', '片栗粉', '酢', '七味', '一味', 'だし', '調味料', '、', '。', 'めんつゆ',
         '：', '.', 'ID', 'コショウ', '胡椒', 'こしょう', '油', '粉', '汁', 'など', 'にがり', 'スープ', '煮',
        ]
    # 除外条件のQオブジェクトを作成
    exclude_conditions = Q()
    for word in exclude_words:
        exclude_conditions |= Q(ingredientName__name__icontains=word)
        
    # キーワードから削除対象のパターン
    patterns = [
        r'【.*?】', r'\(.*?\)', r'（.*?）', r'{.*?}', r'★', r'☆', r'✿', r'、.*', 
        r'■', r'□', r'▪', r'◆', r'◇', r'〇', r'○', r'●', r'◎', r'・', r'※', 
        ]
    # パターンを | で連結して正規表現を作成
    combined_pattern = '|'.join(patterns)
    
    # お気に入りリストを取得
    favorite_list = Favorite.objects.filter(custom_user=user_obj, recipe__cooking_category=cooking_category_obj)
    
    if favorite_list:
        # お気に入りのレシピの食材すべてに重みづけを行う
        for record in favorite_list:
            # レシピの食材リストを取得
            ingredient_list = Ingredients.objects.filter(
                    recipe=record.recipe
                ).exclude(
                    amount=None
                ).exclude(
                    exclude_conditions
                )
            
            # 食材ごとに重みづけ
            for ingredient in ingredient_list:
                # 食材名から余計な装飾などを除外
                name = re.sub(combined_pattern, '', ingredient.ingredientName.name)
                
                if name not in ingredients_weight:
                    ingredients_weight[name] = 0
                
                # 食材ごとに重みを加算
                ingredients_weight[name] += 1
        
        # 合計値より確率を計算し食材名を選択
        total_weight = sum(ingredients_weight.values())
        normalized_weights = [weight / total_weight for weight in ingredients_weight.values()]
        items = list(ingredients_weight.keys())
        search_word = np.random.choice(items, p=normalized_weights)
        
        print(ingredients_weight)
        
        # # キーワードの不要部分を削除
        # cleaned_word = re.sub(combined_pattern, '', search_word)
        
    return search_word
    

""" お気に入りに登録していないレシピ削除 """
def delete_not_favorite_recipe(request):
    user_obj = request.user
    
    # ユーザーがお気に入りに登録していないレシピを取得
    delete_recipes = Recipe.objects.filter(id__in=Favorite.objects.filter(custom_user=user_obj, favorite_flg=False).values_list('recipe_id', flat=True))
    
    # 削除操作を実行
    delete_recipes.delete()
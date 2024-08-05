import requests
from bs4 import BeautifulSoup
import os
from recipe_app.models import *
from django.core.files.base import ContentFile
from django.db.models import Q

""" レシピ一覧を取得 """
def get_recipe_list(search_word, cooking_category):
    
    recipes = []
    search_query = search_word + " " + cooking_category
    
    for i in range(1, 4):
        base_url = 'https://cookpad.com/search/'
        page = ""
        # 2ページ以降はURLにページ数のパラメータを設定
        if i > 1:
            page = f"?page={i}"
        search_url = base_url + requests.utils.quote(search_query) + page
        response = requests.get(search_url)
        
        if response.status_code != 200:
            return {'error': 'Failed to retrieve page'}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for item in soup.select('.recipe-preview'):
            title = item.select_one('.recipe-title').get_text(strip=True)
            url = item.select_one('a')['href']
            recipes.append({
                'title': title,
                'recipe_detail_url': url
            })
        
        # print(recipes)
    
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
def get_recipe_detail(recipe_detail_url, cooking_category):
    base_url = 'https://cookpad.com'
    request_url = base_url + recipe_detail_url
    response = requests.get(request_url)
        
    if response.status_code != 200:
        return {'error': 'Failed to retrieve page'}
    
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
    
    # レシピURL
    request_url
    
    # 料理区分（主菜、副菜、汁物、デザート）
    cooking_category_obj = CookingCategory.objects.get(name=cooking_category)
    
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
        
        name_data = ingredients_data.select_one(".ingredient_name")
        if name_data:
            ingredients_name = name_data.get_text(strip=True)
        else:
            ingredients_name = ingredients_data.select_one(".ingredient_category").get_text(strip=True)
            
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


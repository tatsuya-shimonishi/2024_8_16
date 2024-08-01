import requests
from bs4 import BeautifulSoup
import os

""" レシピ一覧を取得 """
def get_recipe_list(search_query="肉"):
    recipes = []
    
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

""" 画像を取得 """
def get_image(img_url):
    # 画像をダウンロード
    img_response = requests.get(img_url)
    
    # 画像のファイル名をURLから取得
    tmp_img_filename = os.path.basename(img_url)
    img_filename = tmp_img_filename.split("?")[0] + '.webp'
    
    # 保存先のフルパスを作成
    download_folder = r"C:\Users\frontier-Python\Desktop\Django\RecipeProject\recipe_app\static\recipe_app\images"
    save_path = os.path.join(download_folder, img_filename)
    
    # 画像をファイルに保存
    with open(save_path, 'wb') as f:
        f.write(img_response.content)
        
    return img_filename

""" レシピ詳細を取得 """
def get_recipe_detail(recipe_detail_url):
    base_url = 'https://cookpad.com'
    request_url = base_url + recipe_detail_url
    response = requests.get(request_url)
        
    if response.status_code != 200:
        return {'error': 'Failed to retrieve page'}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 各データを抽出
    title =  soup.select_one(".recipe-title").get_text(strip=True)
    img_tmp = soup.select_one('#main-photo')
    img_src = img_tmp.select_one('img')['src']
    img_filename = get_image(img_src)
    # 食数
    ingredients_tmp = soup.select_one('#ingredients')
    servings = ingredients_tmp.select_one(".servings_for").get_text(strip=True)
    
    # 作成者名
    recipe_author_name = soup.select_one('#recipe_author_name').get_text(strip=True)
    
    # 材料 --------------------------------------
    # 並び順、食材名、分量
    ingredients_list = soup.select(".ingredient_row")
    count = 0
    for ingredients_data in ingredients_list:
        # 並び順
        count += 1
        ingredients_name = ingredients_data.select_one(".ingredient_name").get_text(strip=True)
        amount = ingredients_data.select_one(".ingredient_quantity").get_text(strip=True)
    
    # 作り方 ----------------------------
    step_order = 0
    steps_data = soup.select_one('#steps')
    instruction_data = steps_data.select('.instruction')
    # 順番、画像、詳細
    for step_data in instruction_data:
        step_order += 1
        img_src = step_data.select_one('img')['src']
        step_img = get_image(img_src)
        step_text = step_data.select_one('.step_text').get_text(strip=True)
    
    data = {
        "title": title,
        "img_url": img_src,
        "img_filename": img_filename,
        "recipe_author_name": recipe_author_name,
    }
    
    return data


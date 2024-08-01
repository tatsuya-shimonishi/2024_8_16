from django.db import models
from django.contrib.auth.models import AbstractUser

# ユーザー管理
class CustomUser(AbstractUser):
    pass

# 作成者名管理
class Author(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return f"<Author> id:{self.id} name:{self.name}"

# 料理区分管理
class CookingCategory(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return f"<CookingCategory> id:{self.id} name:{self.name}"

# レシピ管理
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    img = models.ImageField(upload_to='products/images/')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    cooking_category = models.ForeignKey(CookingCategory, on_delete=models.CASCADE)
    servings = models.CharField(max_length=200)
    def __str__(self):
        return f"<Recipe> id:{self.id} name:{self.name}"

# お気に入り管理
class Favorite(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    def __str__(self):
        return f"<Favorite> custom_user:{self.custom_user} recipe:{self.recipe}"

# 食材名管理
class IngredientName(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return f"<IngredientName> id:{self.id} name:{self.name}"

# 作り方管理
class Instruction(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    order = models.IntegerField()
    detail = models.CharField(max_length=1000)
    img = models.ImageField(upload_to='products/images/')
    def __str__(self):
        return f"<Instruction> id:{self.id} name:{self.name}"

# 材料管理
class Ingredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredientName = models.ForeignKey(IngredientName, on_delete=models.CASCADE)
    order = models.IntegerField()
    amount = models.IntegerField()
    def __str__(self):
        return f"<Ingredients> id:{self.id} name:{self.name}"


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
    cooking_category = models.ForeignKey(CookingCategory, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='images/', null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    servings = models.CharField(max_length=200, blank=True)
    memo = models.TextField(blank=True)
    def __str__(self):
        return f"<Recipe> id:{self.id} name:{self.name}"

# お気に入り管理
class Favorite(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    def __str__(self):
        return f"<Favorite> custom_user:{self.custom_user} recipe:{self.recipe.name}"

# 食材名管理
class IngredientName(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return f"<IngredientName> id:{self.id} name:{self.name}"

# 材料管理
class Ingredients(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredientName = models.ForeignKey(IngredientName, on_delete=models.CASCADE)
    amount = models.CharField(max_length=200)
    order = models.IntegerField()
    def __str__(self):
        return f"<Ingredients> id:{self.id} recipe:{self.recipe.name} ingredientName:{self.ingredientName.name}"

# 作り方管理
class Instruction(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    order = models.IntegerField()
    img = models.ImageField(upload_to='images/', null=True, blank=True)
    detail = models.TextField(blank=True)
    def __str__(self):
        return f"<Instruction> id:{self.id} recipe:{self.recipe.name} order:{self.order}"


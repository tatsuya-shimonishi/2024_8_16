from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Author)
admin.site.register(CookingCategory)
admin.site.register(Recipe)
admin.site.register(Favorite)
admin.site.register(IngredientName)
admin.site.register(Instruction)
admin.site.register(Ingredients)

# グループモデルを管理サイトから削除
admin.site.unregister(Group)
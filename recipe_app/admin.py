from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

# グループモデルを管理サイトから削除
admin.site.unregister(Group)
# カスタムユーザー
admin.site.register(CustomUser, UserAdmin)

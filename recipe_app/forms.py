from django import forms
from.models import *
from django.contrib.auth.forms import UserCreationForm

# ログイン
class LoginForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "password",
        ]
        widgets = {
            "username": forms.TextInput(attrs={'class':'form-control', 'placeholder':'ユーザ名 or メールアドレス'}),
            "password": forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'パスワード'}),
        }

# 新規登録
class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
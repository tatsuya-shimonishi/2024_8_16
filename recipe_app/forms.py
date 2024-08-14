from django import forms
from.models import *
from django.contrib.auth.forms import UserCreationForm

# ログイン
from django.contrib.auth.forms import AuthenticationForm
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'ユーザ名'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'パスワード'}),
    )

# 新規登録
class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']
    
    username = forms.CharField(
        label = "名前",
        widget = forms.TextInput(attrs={'class':'col-sm form-control', 'placeholder':'例）山田 太郎'}),
    )
    
    password1 = forms.CharField(
        label = "パスワード",
        widget = forms.PasswordInput(attrs={'class':'col-sm form-control', 'placeholder':'例）X4zRU_87'}),
    )
    
    password2 = forms.CharField(
        label = "パスワード(確認)",
        widget = forms.PasswordInput(attrs={'class':'col-sm form-control'}),
    )


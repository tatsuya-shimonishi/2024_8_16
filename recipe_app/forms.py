from django import forms
from.models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
        ]
        widgets = {
            "username": forms.TextInput(attrs={'class':'col-sm form-control', 'placeholder':'例）山田 太郎'}),
            "email": forms.EmailInput(attrs={'class':'col-sm form-control', 'placeholder':'例）XXXX@XXX.XX'}),
            "password": forms.PasswordInput(attrs={'class':'col-sm form-control', 'placeholder':'例）X4zRU_87'}),
        }
        labels = {
            "username": "名前",
            "email": "メールアドレス",
            "password": "パスワード",
        }

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

# 試作---------------------------
from django.contrib.auth.forms import UserCreationForm
class SignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
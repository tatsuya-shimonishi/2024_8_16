from django.db import models
from django.contrib.auth.models import AbstractUser

# class User(models.Model):
#     name = models.CharField(max_length=100)
#     mail = models.EmailField(max_length=200)
#     password = models.CharField(max_length=100, help_text="※8文字以上で大小英数字記号を組み合わせたもの")

#     def __str__(self):
#         return f'< {str(self.id)} : {self.name} >'

class CustomUser(AbstractUser):
   def __str__(self):
       return self.username
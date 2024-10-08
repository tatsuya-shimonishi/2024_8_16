# Generated by Django 4.2.2 on 2024-08-05 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_app', '0007_alter_ingredients_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredients',
            name='amount',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='instruction',
            name='detail',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='memo',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='servings',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

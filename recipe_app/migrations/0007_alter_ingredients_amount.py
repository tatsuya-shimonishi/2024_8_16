# Generated by Django 4.2.2 on 2024-08-05 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_app', '0006_alter_instruction_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredients',
            name='amount',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]

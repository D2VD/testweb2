# Generated by Django 4.2.3 on 2023-08-06 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0024_alter_item_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
    ]

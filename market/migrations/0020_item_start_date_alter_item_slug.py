# Generated by Django 4.2.3 on 2023-08-06 08:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0019_alter_item_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 1, 1, 0, 0, 1)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='item',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]

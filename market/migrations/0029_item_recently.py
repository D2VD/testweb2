# Generated by Django 4.2.3 on 2023-08-06 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0028_alter_item_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='recently',
            field=models.BooleanField(default=False),
        ),
    ]

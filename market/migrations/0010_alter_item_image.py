# Generated by Django 4.2.3 on 2023-08-06 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0009_alter_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, default='items/default.jpg', null=True, upload_to='items/'),
        ),
    ]

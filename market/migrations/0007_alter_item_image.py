# Generated by Django 4.2.3 on 2023-08-06 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0006_alter_item_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='media/'),
        ),
    ]

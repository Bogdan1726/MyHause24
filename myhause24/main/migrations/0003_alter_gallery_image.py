# Generated by Django 3.2.13 on 2022-07-22 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rename_phone_aboutus_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='image',
            field=models.ImageField(blank=True, upload_to='main/gallery/'),
        ),
    ]

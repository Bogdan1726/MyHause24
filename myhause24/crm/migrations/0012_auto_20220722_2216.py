# Generated by Django 3.2.13 on 2022-07-22 19:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0011_auto_20220705_1754'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner_message', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='apartment_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='cashbox',
            name='sum',
            field=models.DecimalField(decimal_places=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='apartment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receipt_apartment', to='crm.apartment'),
        ),
        migrations.AlterField(
            model_name='receipt',
            name='personal_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receipt_account', to='crm.personalaccount'),
        ),
        migrations.AlterField(
            model_name='services',
            name='title',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
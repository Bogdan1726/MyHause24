# Generated by Django 3.2.13 on 2022-06-01 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_auto_20220530_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='area',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='personalaccount',
            name='apartment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='crm.apartment'),
        ),
        migrations.AlterField(
            model_name='personalaccount',
            name='number',
            field=models.CharField(max_length=8),
        ),
    ]

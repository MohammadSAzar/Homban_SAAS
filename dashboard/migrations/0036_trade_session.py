# Generated by Django 5.1.7 on 2025-05-29 14:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0035_alter_trade_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='trade',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='trades', to='dashboard.session', verbose_name='Session'),
        ),
    ]

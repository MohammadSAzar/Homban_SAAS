# Generated by Django 5.1.7 on 2025-05-05 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_remove_person_slug_remove_rentfile_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='date',
            field=models.CharField(max_length=200, verbose_name='تاریخ معامله'),
        ),
    ]

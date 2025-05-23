# Generated by Django 5.1.7 on 2025-04-10 16:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_customer_city_customer_district_customer_province_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='customer',
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('budget_announced', models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Announced Budget')),
                ('budget_max', models.PositiveBigIntegerField(blank=True, null=True, verbose_name='Max Budget')),
                ('budget_status', models.CharField(blank=True, choices=[('CS', 'نقد'), ('UC', 'غیر نقد')], max_length=15, null=True, verbose_name='Budget Status')),
                ('room_min', models.CharField(choices=[('0', 'بدون اتاق'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', 'بیش از 5')], max_length=15, verbose_name='Min Rooms')),
                ('room_max', models.CharField(choices=[('0', 'بدون اتاق'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', 'بیش از 5')], max_length=15, verbose_name='Max Rooms')),
                ('area_min', models.PositiveIntegerField(default='1', verbose_name='Min Area')),
                ('area_max', models.PositiveIntegerField(default='1', verbose_name='Max Area')),
                ('age_min', models.CharField(choices=[('-1', 'کلید نخورده'), ('0', 'نوساز'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', 'بیش از 30')], default='1', max_length=15, verbose_name='Min Age')),
                ('age_max', models.CharField(choices=[('-1', 'کلید نخورده'), ('0', 'نوساز'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', 'بیش از 30')], default='1', max_length=15, verbose_name='Max Age')),
                ('document', models.CharField(choices=[('has', 'Has'), ('hasnt', 'Has Not')], max_length=15, verbose_name='Document')),
                ('parking', models.CharField(choices=[('has', 'Has'), ('hasnt', 'Has Not')], max_length=15, verbose_name='Parking')),
                ('elevator', models.CharField(choices=[('has', 'Has'), ('hasnt', 'Has Not')], max_length=15, verbose_name='Elevator')),
                ('warehouse', models.CharField(choices=[('has', 'Has'), ('hasnt', 'Has Not')], max_length=15, verbose_name='Warehouse')),
                ('name', models.CharField(max_length=100, verbose_name='نام')),
                ('phone_number', models.CharField(max_length=11, unique=True, verbose_name='Phone Number')),
                ('description', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('code', models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Code')),
                ('datetime_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date and Time of Creation')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='dashboard.city', verbose_name='City')),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='dashboard.district', verbose_name='District')),
                ('province', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers', to='dashboard.province', verbose_name='Province')),
                ('sub_district1', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers_sub_district1', to='dashboard.subdistrict', verbose_name='Sub-District1')),
                ('sub_district2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers_sub_district2', to='dashboard.subdistrict', verbose_name='Sub-District2')),
                ('sub_district3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers_sub_district3', to='dashboard.subdistrict', verbose_name='Sub-District3')),
            ],
            options={
                'ordering': ('-datetime_created',),
            },
        ),
        migrations.AddField(
            model_name='task',
            name='buyer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks', to='dashboard.buyer', verbose_name='Buyer'),
        ),
        migrations.AlterField(
            model_name='visit',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='visits', to='dashboard.buyer', verbose_name='Buyer'),
        ),
        migrations.DeleteModel(
            name='Customer',
        ),
    ]

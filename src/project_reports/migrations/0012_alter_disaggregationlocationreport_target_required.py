# Generated by Django 4.0.6 on 2024-07-11 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0011_alter_projectmonthlyreport_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disaggregationlocationreport',
            name='target_required',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Required Target'),
        ),
    ]

# Generated by Django 4.0.10 on 2023-08-29 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0006_remove_activityplan_facility_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetlocation',
            name='activity_plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rh.activityplan'),
        ),
    ]
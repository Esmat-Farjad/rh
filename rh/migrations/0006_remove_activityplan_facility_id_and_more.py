# Generated by Django 4.0.10 on 2023-07-30 05:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0005_remove_activityplan_age_desegregation_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activityplan',
            name='facility_id',
        ),
        migrations.RemoveField(
            model_name='activityplan',
            name='facility_lat',
        ),
        migrations.RemoveField(
            model_name='activityplan',
            name='facility_long',
        ),
        migrations.RemoveField(
            model_name='activityplan',
            name='facility_monitoring',
        ),
        migrations.RemoveField(
            model_name='activityplan',
            name='facility_name',
        ),
        migrations.RemoveField(
            model_name='activityplan',
            name='facility_type',
        ),
        migrations.RemoveField(
            model_name='activityplan',
            name='old_id',
        ),
    ]
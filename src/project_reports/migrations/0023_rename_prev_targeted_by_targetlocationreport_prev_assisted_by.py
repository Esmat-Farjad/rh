# Generated by Django 5.1 on 2024-12-12 06:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_reports', '0022_remove_activityplanreport_beneficiary_status_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='targetlocationreport',
            old_name='prev_targeted_by',
            new_name='prev_assisted_by',
        ),
    ]
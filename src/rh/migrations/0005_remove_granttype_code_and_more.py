# Generated by Django 4.0.6 on 2024-03-17 10:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0004_delete_reporttype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='granttype',
            name='code',
        ),
        migrations.RemoveField(
            model_name='implementationmodalitytype',
            name='code',
        ),
        migrations.RemoveField(
            model_name='packagetype',
            name='code',
        ),
        migrations.RemoveField(
            model_name='transfercategory',
            name='code',
        ),
        migrations.RemoveField(
            model_name='transfermechanismtype',
            name='code',
        ),
        migrations.AlterField(
            model_name='beneficiarytype',
            name='country',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'Country'}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='rh.location'),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='countries',
            field=models.ManyToManyField(blank=True, limit_choices_to={'type': 'Country'}, to='rh.location'),
        ),
        migrations.AlterField(
            model_name='donor',
            name='countries',
            field=models.ManyToManyField(blank=True, limit_choices_to={'type': 'Country'}, to='rh.location'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='countries',
            field=models.ManyToManyField(blank=True, limit_choices_to={'type': 'Country'}, to='rh.location'),
        ),
    ]
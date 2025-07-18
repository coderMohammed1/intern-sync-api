# Generated by Django 4.2.21 on 2025-06-22 06:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_alter_applications_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='application_deadline',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='jobs',
            name='posted_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='jobs',
            name='end',
            field=models.CharField(max_length=12, null=True),
        ),
    ]

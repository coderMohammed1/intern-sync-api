# Generated by Django 5.2.3 on 2025-06-20 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_jobs_work_mode_jobs_work_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='status',
            field=models.CharField(default='pending', max_length=50),
        ),
    ]

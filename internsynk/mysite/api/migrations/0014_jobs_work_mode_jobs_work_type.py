# Generated by Django 5.2.3 on 2025-06-20 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_jobs_status_alter_applications_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobs',
            name='work_mode',
            field=models.CharField(choices=[('On-Site', 'On-Site'), ('Remote', 'Remote'), ('Hybrid', 'Hybrid')], default='On-Site', max_length=10),
        ),
        migrations.AddField(
            model_name='jobs',
            name='work_type',
            field=models.CharField(choices=[('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time')], default='Full-Time', max_length=10),
        ),
    ]

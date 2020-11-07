# Generated by Django 3.1.2 on 2020-11-07 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0005_auto_20201107_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agencyemployee',
            name='role',
            field=models.CharField(choices=[('M', 'Manager'), ('S', 'Sales staff'), ('A', 'Agency administrator')], default='S', max_length=1, verbose_name="Employee's Role"),
        ),
    ]

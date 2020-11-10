# Generated by Django 3.1.2 on 2020-11-10 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('agency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='agency.agency')),
            ],
        ),
    ]

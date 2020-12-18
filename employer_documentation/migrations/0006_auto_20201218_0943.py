# Generated by Django 3.1.4 on 2020-12-18 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employer_documentation', '0005_employerdocserviceagreement_c5_1_2_refund_within_days'),
    ]

    operations = [
        migrations.AddField(
            model_name='employerdocmaidstatus',
            name='date_of_application_for_transfer',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='employerdocmaidstatus',
            name='fdw_work_commencement_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='employerdocmaidstatus',
            name='employer_doc_base',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rn_employerdocmaidstatus', to='employer_documentation.employerdocbase'),
        ),
    ]

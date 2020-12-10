# Generated by Django 3.1.2 on 2020-12-10 07:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('agency', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Maid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_number', models.CharField(max_length=255, verbose_name='Reference Number')),
                ('maid_type', models.CharField(choices=[('NEW', 'No Experience'), ('TRF', 'Transfer'), ('SGE', 'Singapore Experience'), ('OVE', 'Overseas Experience')], default='NEW', max_length=3, verbose_name='Maid Type')),
                ('salary', models.PositiveIntegerField()),
                ('loan_amount', models.PositiveIntegerField()),
                ('days_off', models.PositiveIntegerField()),
                ('passport_status', models.BooleanField(choices=[(0, 'Not Ready'), (1, 'Ready')], default=0, max_length=1, verbose_name='Passport status')),
                ('repatraition_airport', models.CharField(max_length=100, verbose_name='Repatraition airport')),
                ('remarks', models.CharField(max_length=255, verbose_name='Remarks')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('updated_on', models.DateTimeField(auto_now=True, verbose_name='Updated on')),
                ('complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('biodata_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('family_details_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('infant_child_care_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('elderly_care_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('disabled_care_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('general_housework_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('cooking_complete', models.BooleanField(blank=True, default=False, editable=False)),
                ('published', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maid', to='agency.agency')),
            ],
        ),
        migrations.CreateModel(
            name='MaidWorkDuty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('H', 'Housework'), ('H_HDB', 'Housework (HDB)'), ('H_CON', 'Housework (Condo)'), ('H_PLP', 'Housework (Landed Property)'), ('CO', 'Cooking'), ('CO_C', 'Cooking (Chinese Food)'), ('CO_I', 'Cooking (Indian Food)'), ('CO_M', 'Cooking (Malay Food)'), ('CA_IC', 'Infant child care'), ('CA_E', 'Elderly care'), ('CA_D', 'Disabled care'), ('CA_P', 'Pet care')], max_length=5, verbose_name="Maid's work duties")),
            ],
        ),
        migrations.CreateModel(
            name='MaidStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipa_arroved', models.BooleanField(default=False, verbose_name='IPA approved')),
                ('bond_date', models.DateField(null=True, verbose_name='Bond Date')),
                ('sip_date', models.DateField(null=True, verbose_name='SIP Date')),
                ('thumbprint_date', models.DateField(null=True, verbose_name='Thumbprint Date')),
                ('deployment_date', models.DateField(null=True, verbose_name='Deployment Date')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='status', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidInfantChildCare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.IntegerField(choices=[(1, 'Least preferred'), (2, 'Less preferred'), (3, 'No preference'), (4, 'More preferred'), (5, 'Most preferred')], default=3, verbose_name='Infant child care preference')),
                ('willingness', models.BooleanField(choices=[(True, 'Willing'), (False, 'Not willing')], default=True, verbose_name='Willingness for infant child care')),
                ('experience', models.BooleanField(choices=[(True, 'Experience'), (False, 'No experience')], default=True, verbose_name='Experience with infant child care')),
                ('remarks', models.CharField(choices=[('OC', 'Experience in own country'), ('OV', 'Experience in overseas'), ('SG', 'Experience in Singapore'), ('OC_SG', 'Experience in own country and Singapore'), ('OC_O', 'Experience in own country and overseas'), ('OC_O_SG', 'Experience in own country, overseas and Singapore'), ('NE', 'No experience, but willing to learn'), ('NW', 'Not willing to care for infants/children'), ('OTH', 'Other remarks (Please specify)')], max_length=7, null=True, verbose_name='Remarks for infant child care')),
                ('other_remarks', models.TextField(blank=True, verbose_name='Other remarks for infant child care')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='infant_child_care', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidGeneralHousework',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.IntegerField(choices=[(1, 'Least preferred'), (2, 'Less preferred'), (3, 'No preference'), (4, 'More preferred'), (5, 'Most preferred')], default=3, verbose_name='General housework preference')),
                ('willingness', models.BooleanField(choices=[(True, 'Willing'), (False, 'Not willing')], default=True, verbose_name='Willingness for general housework')),
                ('experience', models.BooleanField(choices=[(True, 'Experience'), (False, 'No experience')], default=True, verbose_name='Experience with general housework')),
                ('remarks', models.CharField(choices=[('CAN', 'Able to do all general housework'), ('OTH', 'Other remarks (Please specify)')], max_length=7, null=True, verbose_name='Remarks for general housework')),
                ('other_remarks', models.TextField(blank=True, verbose_name='Other remarks for general housework')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='general_housework', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidFoodHandlingPreference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.CharField(choices=[('P', 'No pork'), ('C', 'No chicken'), ('B', 'No beef'), ('S', 'No seafood')], default='P', max_length=1, verbose_name='Food preference')),
                ('maid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='food_handling_preferences', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidFamilyDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marital_status', models.CharField(choices=[('S', 'Single'), ('M', 'Married'), ('W', 'Widowed'), ('SP', 'Single Parent'), ('D', 'Divorced')], default='S', max_length=2, verbose_name='Marital Status')),
                ('number_of_children', models.PositiveIntegerField(default=0)),
                ('age_of_children', models.CharField(default='N.A', max_length=50, verbose_name='Age of children')),
                ('number_of_siblings', models.PositiveIntegerField(default=0)),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='family_details', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidEmploymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(verbose_name="Maid employment's start date")),
                ('end_date', models.DateTimeField(verbose_name="Maid employment's end date")),
                ('country', models.CharField(choices=[('SG', 'SINGAPORE')], max_length=3, verbose_name='Country of employment')),
                ('work_duration', models.DurationField(blank=True, editable=False, verbose_name='Employment duration')),
                ('maid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employment_history', to='maid.maid')),
                ('work_duties', models.ManyToManyField(to='maid.MaidWorkDuty')),
            ],
        ),
        migrations.CreateModel(
            name='MaidElderlyCare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.IntegerField(choices=[(1, 'Least preferred'), (2, 'Less preferred'), (3, 'No preference'), (4, 'More preferred'), (5, 'Most preferred')], default=3, verbose_name='Elderly care preference')),
                ('willingness', models.BooleanField(choices=[(True, 'Willing'), (False, 'Not willing')], default=True, verbose_name='Willingness for elderly care')),
                ('experience', models.BooleanField(choices=[(True, 'Experience'), (False, 'No experience')], default=True, verbose_name='Experience with elderly care')),
                ('remarks', models.CharField(choices=[('OC', 'Experience in own country'), ('OV', 'Experience in overseas'), ('SG', 'Experience in Singapore'), ('OC_SG', 'Experience in own country and Singapore'), ('OC_O', 'Experience in own country and overseas'), ('OC_O_SG', 'Experience in own country, overseas and Singapore'), ('NE', 'No experience, but willing to learn'), ('NW', 'Not willing to care for elderly'), ('OTH', 'Other remarks (Please specify)')], max_length=7, null=True, verbose_name='Remarks for elderly care')),
                ('other_remarks', models.TextField(blank=True, verbose_name='Other remarks for elderly care')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='elderly_care', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidDisabledCare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.IntegerField(choices=[(1, 'Least preferred'), (2, 'Less preferred'), (3, 'No preference'), (4, 'More preferred'), (5, 'Most preferred')], default=3, verbose_name='Disabled care preference')),
                ('willingness', models.BooleanField(choices=[(True, 'Willing'), (False, 'Not willing')], default=True, verbose_name='Willingness for disabled care')),
                ('experience', models.BooleanField(choices=[(True, 'Experience'), (False, 'No experience')], default=True, verbose_name='Experience with disabled care')),
                ('remarks', models.CharField(choices=[('OC', 'Experience in own country'), ('OV', 'Experience in overseas'), ('SG', 'Experience in Singapore'), ('OC_SG', 'Experience in own country and Singapore'), ('OC_O', 'Experience in own country and overseas'), ('OC_O_SG', 'Experience in own country, overseas and Singapore'), ('NE', 'No experience, but willing to learn'), ('NW', 'Not willing to care for disabled'), ('OTH', 'Other remarks (Please specify)')], max_length=7, null=True, verbose_name='Remarks for disabled care')),
                ('other_remarks', models.TextField(blank=True, verbose_name='Other remarks for disabled care')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='disabled_care', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidDietaryRestriction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restriction', models.CharField(choices=[('P', 'No pork'), ('C', 'No chicken'), ('B', 'No beef'), ('S', 'No seafood')], default='P', max_length=1, verbose_name='Dietary restriction')),
                ('maid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dietary_restrictions', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidCooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preference', models.IntegerField(choices=[(1, 'Least preferred'), (2, 'Less preferred'), (3, 'No preference'), (4, 'More preferred'), (5, 'Most preferred')], default=3, verbose_name='Cooking preference')),
                ('willingness', models.BooleanField(choices=[(True, 'Willing'), (False, 'Not willing')], default=True, verbose_name='Willingness for cooking')),
                ('experience', models.BooleanField(choices=[(True, 'Experience'), (False, 'No experience')], default=True, verbose_name='Experience with cooking')),
                ('remarks', models.CharField(choices=[('OC', "Able to cook own country's cuisine"), ('C', 'Able to cook chinese cuisine'), ('I', 'Able to cook indian cuisine'), ('W', 'Able to cook western cuisine'), ('OC_C', "Able to cook own country's and chinese cuisine"), ('OC_I', "Able to cook own country's and indian cuisine"), ('OC_W', "Able to cook own country's and western cuisine"), ('C_I', 'Able to cook chinese and indian cuisine'), ('C_W', 'Able to cook chinese and western cuisine'), ('I_W', 'Able to cook indian and western cuisine'), ('OC_C_I', "Able to cook own country's, chinese and indian cuisine"), ('OC_C_W', "Able to cook own country's, chinese and western cuisine"), ('OC_I_W', "Able to cook own country's, indian and western cuisine"), ('C_I_W', 'Able to cook chinese, indian and western cuisine'), ('OC_C_I_W', "Able to cook own country's, chinese, indian and western cuisine"), ('OTH', 'Other remarks (Please specify)')], max_length=8, null=True, verbose_name='Remarks for cooking')),
                ('other_remarks', models.TextField(blank=True, verbose_name='Other remarks for cooking')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cooking', to='maid.maid')),
            ],
        ),
        migrations.CreateModel(
            name='MaidBiodata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Name')),
                ('age', models.IntegerField(null=True, verbose_name='Age')),
                ('country_of_origin', models.CharField(choices=[('BGD', 'Bangladesh'), ('KHM', 'Cambodia'), ('IND', 'India'), ('IDN', 'Indonesia'), ('MMR', 'Myanmar'), ('PHL', 'Philippines (the)'), ('LKA', 'Sri Lanka'), ('OTH', 'Others')], max_length=3, null=True, verbose_name='Country of Origin')),
                ('height', models.PositiveIntegerField(null=True, verbose_name='Height (in cm)')),
                ('weight', models.PositiveIntegerField(null=True, verbose_name='Weight (in kg)')),
                ('place_of_birth', models.CharField(max_length=25, null=True, verbose_name='Place of birth')),
                ('address_1', models.CharField(max_length=100, null=True, verbose_name='Address 1')),
                ('address_2', models.CharField(max_length=100, null=True, verbose_name='Address 2')),
                ('religion', models.CharField(choices=[('B', 'Buddhist'), ('M', 'Muslim'), ('H', 'Hindu'), ('CH', 'Christain'), ('CA', 'Catholic'), ('S', 'Sikh'), ('OTH', 'Others'), ('NONE', 'None')], default='NONE', max_length=4, verbose_name='Religion')),
                ('maid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='biodata', to='maid.maid')),
            ],
        ),
    ]

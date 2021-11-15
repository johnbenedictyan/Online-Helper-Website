import uuid

from accounts.models import PotentialEmployer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from enquiry.models import GeneralEnquiry, ShortlistedEnquiry
from maid.models import (Maid, MaidCooking, MaidDietaryRestriction,
                         MaidDisabledCare, MaidElderlyCare,
                         MaidEmploymentHistory, MaidFoodHandlingPreference,
                         MaidGeneralHousework, MaidInfantChildCare,
                         MaidLanguage, MaidLanguageProficiency,
                         MaidLoanTransaction, MaidResponsibility)
from onlinemaid.constants import EMPLOYERS
from rest_framework import serializers
from rest_framework.fields import IntegerField, SerializerMethodField, UUIDField
from rest_framework.serializers import CharField, ModelSerializer


class MaidLanguageSerializer(ModelSerializer):
    language = CharField(source='get_language_display')

    class Meta:
        model = MaidLanguage
        fields = ['language']


class MaidResponsibilitySerializer(ModelSerializer):
    name = CharField(source='get_name_display')

    class Meta:
        model = MaidResponsibility
        fields = ['name']


class MaidCookingSerializer(ModelSerializer):
    willingness = CharField(source='get_willingness_display')
    experience = CharField(source='get_experience_display')
    remarks = CharField(source='get_remarks_display')

    class Meta:
        model = MaidCooking
        exclude = ['id', 'maid']


class MaidDisabledCareSerializer(ModelSerializer):
    willingness = CharField(source='get_willingness_display')
    experience = CharField(source='get_experience_display')
    remarks = CharField(source='get_remarks_display')

    class Meta:
        model = MaidDisabledCare
        exclude = ['id', 'maid']


class MaidElderlyCareSerializer(ModelSerializer):
    willingness = CharField(source='get_willingness_display')
    experience = CharField(source='get_experience_display')
    remarks = CharField(source='get_remarks_display')

    class Meta:
        model = MaidElderlyCare
        exclude = ['id', 'maid']


class MaidGeneralHouseworkSerializer(ModelSerializer):
    willingness = CharField(source='get_willingness_display')
    experience = CharField(source='get_experience_display')
    remarks = CharField(source='get_remarks_display')

    class Meta:
        model = MaidGeneralHousework
        exclude = ['id', 'maid']


class MaidInfantChildCareSerializer(ModelSerializer):
    willingness = CharField(source='get_willingness_display')
    experience = CharField(source='get_experience_display')
    remarks = CharField(source='get_remarks_display')

    class Meta:
        model = MaidInfantChildCare
        exclude = ['id', 'maid']


class MaidLanguageProficiencySerializer(ModelSerializer):
    english = CharField(source='get_english_display')
    malay = CharField(source='get_malay_display')
    mandarin = CharField(source='get_mandarin_display')
    chinese_dialect = CharField(source='get_chinese_dialect_display')
    hindi = CharField(source='get_hindi_display')
    tamil = CharField(source='get_tamil_display')

    class Meta:
        model = MaidLanguageProficiency
        exclude = ['id', 'maid']


class MaidFoodHandlingPreferenceSerializer(ModelSerializer):
    preference = CharField(source='get_preference_display')

    class Meta:
        model = MaidFoodHandlingPreference
        exclude = ['id', 'maid']


class MaidDietaryRestrictionSerializer(ModelSerializer):
    restriction = CharField(source='get_restriction_display')

    class Meta:
        model = MaidDietaryRestriction
        exclude = ['id', 'maid']


class MaidEmploymentHistorySerializer(ModelSerializer):
    class Meta:
        model = MaidEmploymentHistory
        exclude = ['id', 'maid']


class MaidLoanTransactionSerializer(ModelSerializer):
    class Meta:
        model = MaidLoanTransaction
        exclude = ['id', 'maid']


class MaidSerializer(ModelSerializer):
    maid_type = CharField(source='get_maid_type_display')
    marital_status = CharField(source='get_marital_status_display')
    country_of_origin = CharField(source='get_country_of_origin_display')
    religion = CharField(source='get_religion_display')
    education_level = CharField(source='get_education_level_display')
    languages = MaidLanguageSerializer(read_only=True, many=True)
    responsibilities = MaidResponsibilitySerializer(read_only=True, many=True)
    infant_child_care = MaidInfantChildCareSerializer(read_only=True)
    elderly_care = MaidElderlyCareSerializer(read_only=True)
    disabled_care = MaidDisabledCareSerializer(read_only=True)
    general_housework = MaidGeneralHouseworkSerializer(read_only=True)
    cooking = MaidCookingSerializer(read_only=True)
    language_proficiency = MaidLanguageProficiencySerializer(read_only=True)
    food_handling_preferences = MaidFoodHandlingPreferenceSerializer(
        read_only=True, many=True)
    dietary_restrictions = MaidDietaryRestrictionSerializer(
        read_only=True, many=True)
    employment_history = MaidEmploymentHistorySerializer(
        read_only=True, many=True)
    loan_transactions = MaidLoanTransactionSerializer(
        read_only=True, many=True)
    age = IntegerField(read_only=True)

    class Meta:
        model = Maid
        fields = [
            'pk', 'reference_number', 'name', 'photo', 'maid_type', 'age',
            'marital_status', 'number_of_children', 'age_of_children',
            'number_of_siblings', 'country_of_origin', 'expected_salary',
            'expected_days_off', 'date_of_birth', 'height', 'weight',
            'place_of_birth', 'address_1', 'address_2', 'repatriation_airport',
            'religion', 'contact_number', 'education_level', 'about_me',
            'email', 'languages', 'responsibilities', 'infant_child_care',
            'elderly_care', 'disabled_care', 'general_housework', 'cooking',
            'language_proficiency', 'food_handling_preferences',
            'dietary_restrictions', 'employment_history', 'loan_transactions'
        ]


class SlimMaidSerializer(ModelSerializer):
    maid_type = CharField(source='get_maid_type_display')
    marital_status = CharField(source='get_marital_status_display')
    country_of_origin = CharField(source='get_country_of_origin_display')
    age = IntegerField(read_only=True)

    class Meta:
        model = Maid
        fields = [
            'pk', 'name', 'photo', 'maid_type', 'marital_status',
            'country_of_origin', 'age'
        ]


class PKMaidSerializer(ModelSerializer):
    class Meta:
        model = Maid
        fields = ['pk']


class MaidResponsibilityModelSerializer(ModelSerializer):
    class Meta:
        model = MaidResponsibility
        fields = ['name']


class MaidLanguageModelSerializer(ModelSerializer):
    class Meta:
        model = MaidLanguage
        fields = ['language']


class GeneralEnquiryModelSerializer(ModelSerializer):
    maid_responsibility = MaidResponsibilityModelSerializer(many=True)
    languages_spoken = MaidLanguageModelSerializer(many=True)
    potential_employer = UUIDField(required=False)

    class Meta:
        model = GeneralEnquiry
        fields = '__all__'

    def create(self, validated_data):
        maid_responsibilities = validated_data.pop('maid_responsibility')
        languages_spoken = validated_data.pop('languages_spoken')
        potential_employer = validated_data.pop('potential_employer')

        # TODO: CHANGE THIS INEFFICIENT PSEUDO DE-HASH CODE
        pe_pk = None
        try:
            for i in PotentialEmployer.objects.all():
                if uuid.uuid5(
                    uuid.UUID(settings.API_ACCOUNT_UUID_NAMESPACE),
                    str(i.user.pk)
                ) == potential_employer:
                    pe_pk = i.user.pk
        except Exception as e:
            raise Exception(e)
        else:
            if pe_pk:
                instance = PotentialEmployer.objects.get(
                    user__pk=pe_pk
                )
                validated_data.update({
                    'potential_employer': instance
                })

        instance = GeneralEnquiry.objects.create(**validated_data)

        for i in maid_responsibilities:
            selected_maid_responsibilities = MaidResponsibility.objects.get(
                name=i['name']
            )
            instance.maid_responsibility.add(selected_maid_responsibilities)

        for i in languages_spoken:
            selected_maid_language = MaidLanguage.objects.get(
                language=i['language']
            )
            instance.languages_spoken.add(selected_maid_language)

        return instance


class ShortlistedEnquiryModelSerializer(ModelSerializer):
    maids = PKMaidSerializer(many=True, read_only=True)
    potential_employer = UUIDField()

    class Meta:
        model = ShortlistedEnquiry
        fields = '__all__'

    def create(self, validated_data):
        maids = validated_data.pop('custom_maids')
        potential_employer = validated_data.pop('potential_employer')

        # TODO: CHANGE THIS INEFFICIENT PSEUDO DE-HASH CODE
        pe_pk = None
        try:
            for i in PotentialEmployer.objects.all():
                if uuid.uuid5(
                    uuid.UUID(settings.API_ACCOUNT_UUID_NAMESPACE),
                    str(i.user.pk)
                ) == potential_employer:
                    pe_pk = i.user.pk
        except Exception as e:
            raise Exception(e)
        else:
            if pe_pk:
                instance = PotentialEmployer.objects.get(
                    user__pk=pe_pk
                )
                validated_data.update({
                    'potential_employer': instance
                })

        instance = ShortlistedEnquiry.objects.create(**validated_data)

        for i in maids:
            selected_maid = Maid.objects.get(
                pk=i['pk']
            )
            instance.maids.add(selected_maid)

        return instance


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']


class PotentialEmployerModelSerializer(ModelSerializer):
    user = UserModelSerializer()

    class Meta:
        model = PotentialEmployer
        fields = '__all__'

    def create(self, validated_data):
        user_details = validated_data.pop('user')
        try:
            new_user = get_user_model().objects.create_user(
                email=user_details.get('email'),
                password=user_details.get('password')
            )
        except Exception:
            pass
        else:
            potential_employer_group = Group.objects.get(
                name=EMPLOYERS
            )
            potential_employer_group.user_set.add(
                new_user
            )
            instance = PotentialEmployer.objects.create(
                user=new_user
            )
            return instance

    def auth(self, data):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(
                email=data.get('email')
            )
        except user_model.DoesNotExist as e:
            raise Exception(e)
        else:
            flag = user.check_password(data.get('password'))
            if flag:
                return str(uuid.uuid5(
                    uuid.UUID(settings.API_ACCOUNT_UUID_NAMESPACE),
                    str(user.pk)
                ))
            else:
                raise Exception('Wrong Password')


# class AgencyUserSerializer(serializers.Serializer):
#     agency_license_number = CharField()
#     email = EmailField()
#     password = CharField()

#     def identify(self, email):
#         try:
#             pe = PotentialEmployer.objects.get(
#                 email=email
#             )
#         except PotentialEmployer.DoesNotExist as e:
#             print(e)
#         else:
#             return pe

#     def create(self, validated_data):
#         try:
#             new_user = get_user_model().objects.create_user(
#                 email=validated_data.get('email'),
#                 password=validated_data.get('password')
#             )
#         except Exception:
#             pass
#         else:
#             potential_employer_group = Group.objects.get(
#                 name=EMPLOYERS
#             )
#             potential_employer_group.user_set.add(
#                 new_user
#             )
#             instance = PotentialEmployer.objects.create(
#                 user=new_user
#             )
#             return instance

#     def auth(self, validated_data):
#         pe = self.identify(validated_data.get('email'))
#         if pe:
#             flag = pe.user.check_password(validated_data.get('password'))
#             if flag:
#                 return uuid.uuid5(settings.API_ACCOUNT_UUID_NAMESPACE, pe.pk)

from maid.models import (Maid, MaidCooking, MaidDietaryRestriction,
                         MaidDisabledCare, MaidElderlyCare,
                         MaidEmploymentHistory, MaidFoodHandlingPreference,
                         MaidGeneralHousework, MaidInfantChildCare,
                         MaidLanguage, MaidLanguageProficiency,
                         MaidLoanTransaction, MaidResponsibility)
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

    class Meta:
        model = Maid
        fields = [
            'pk', 'reference_number', 'name', 'photo', 'maid_type',
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

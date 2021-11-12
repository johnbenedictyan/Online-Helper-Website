from maid.models import (Maid, MaidCooking, MaidDisabledCare, MaidElderlyCare,
                         MaidGeneralHousework, MaidInfantChildCare,
                         MaidLanguage, MaidLanguageProficiency,
                         MaidResponsibility)
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
    class Meta:
        model = MaidCooking
        fields = ['__all__']


class MaidDisabledCareSerializer(ModelSerializer):
    class Meta:
        model = MaidDisabledCare
        fields = ['__all__']


class MaidElderlyCareSerializer(ModelSerializer):

    class Meta:
        model = MaidElderlyCare
        fields = ['__all__']


class MaidGeneralHouseworkSerializer(ModelSerializer):

    class Meta:
        model = MaidGeneralHousework
        fields = ['__all__']


class MaidInfantChildCareSerializer(ModelSerializer):

    class Meta:
        model = MaidInfantChildCare
        fields = ['__all__']


class MaidLanguageProficiencySerializer(ModelSerializer):

    class Meta:
        model = MaidLanguageProficiency
        fields = ['__all__']


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
            'elderly_care', 'disabled_care', 'general_housework', 'cooking'
        ]

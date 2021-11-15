import random
from datetime import timedelta

from accounts.models import PotentialEmployer
from django.utils import timezone
from enquiry.models import GeneralEnquiry, ShortlistedEnquiry
from maid.constants import (MaidLanguageChoices, MaidNationalityChoices,
                            MaidResponsibilityChoices, TypeOfMaidChoices)
from maid.models import Maid, MaidLanguage, MaidResponsibility
from onlinemaid.constants import MaritalStatusChoices
from rest_framework.generics import (GenericAPIView, ListAPIView,
                                     ListCreateAPIView, RetrieveAPIView,
                                     get_object_or_404)
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey

from .serializers import (GeneralEnquiryModelSerializer, MaidSerializer,
                          PotentialEmployerModelSerializer,
                          ShortlistedEnquiryModelSerializer,
                          SlimMaidSerializer)


class MaidRetrieveAPIView(RetrieveAPIView):
    permission_classes = [HasAPIKey]
    queryset = Maid.objects.all()
    serializer_class = MaidSerializer


class SimilarMaidListAPIView(ListAPIView):
    permission_classes = [HasAPIKey]
    queryset = Maid.objects.all()
    serializer_class = SlimMaidSerializer
    maid_id = None

    def dispatch(self, request, *args, **kwargs):
        self.maid_id = kwargs.pop('pk')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        api_auth_id = self.request.META.get('HTTP_AGENCY_AUTH_ID', None)
        if api_auth_id:
            qs = self.queryset.filter(agency__api_auth_id=api_auth_id)
            try:
                target_maid = Maid.objects.get(
                    pk=self.maid_id
                )
            except Maid.DoesNotExist as e:
                print(e)
                return qs
            else:
                languages = target_maid.languages.all()
                country_of_origin = target_maid.country_of_origin
                qs = qs.filter(
                    country_of_origin=country_of_origin,
                    languages__in=languages
                ).exclude(
                    pk=self.maid_id
                ).distinct()
                if qs.count() <= 4:
                    return qs
                else:
                    return random.choices(qs, k=4)
        else:
            return None


class MaidListAPIView(ListAPIView):
    permission_classes = [HasAPIKey]
    queryset = Maid.objects.all()
    serializer_class = SlimMaidSerializer

    def get_queryset(self):
        api_auth_id = self.request.META.get('HTTP_AGENCY_AUTH_ID', None)
        if api_auth_id:
            qs = self.queryset.filter(agency__api_auth_id=api_auth_id)
            if self.request.query_params:
                query_params = self.request.query_params
                # NP
                maid_type = query_params.get("type")
                if maid_type != 'NP':
                    maid_type_map = {
                        'N': TypeOfMaidChoices.NEW,
                        'T': TypeOfMaidChoices.TRANSFER,
                        'S': TypeOfMaidChoices.SINGAPORE_EXPERIENCE,
                        'O': TypeOfMaidChoices.OVERSEAS_EXPERIENCE,
                    }
                    qs = qs.filter(
                        maid_type=maid_type_map[maid_type]
                    )

                maid_nationality = query_params.get("nationality")
                if maid_nationality != 'NP':
                    maid_nationality_map = {
                        'Filipino': MaidNationalityChoices.PHILIPPINES,
                        'Indonesian': MaidNationalityChoices.INDONESIA,
                        'Myanmarese': MaidNationalityChoices.MYANMAR,
                        'Indian': MaidNationalityChoices.INDIA,
                        'Cambodian': MaidNationalityChoices.CAMBODIA,
                        'SriLankan': MaidNationalityChoices.SRI_LANKA
                    }
                    qs = qs.filter(
                        country_of_origin=maid_nationality_map[
                            maid_nationality]
                    )

                maid_marital_status = query_params.get("marital_status")
                if maid_marital_status != 'NP':
                    maid_marital_status_map = {
                        'single': MaritalStatusChoices.SINGLE,
                        'married': MaritalStatusChoices.MARRIED,
                        'divorced': MaritalStatusChoices.DIVORCED,
                        'widowed': MaritalStatusChoices.WIDOWED,
                        'separated': MaritalStatusChoices.SEPARATED,
                        'single-parent': MaritalStatusChoices.SINGLE_PARENT
                    }
                    qs = qs.filter(
                        marital_status=maid_marital_status_map[
                            maid_marital_status]
                    )

                maid_min_age = query_params.get("min_age")
                maid_max_age = query_params.get("max_age")

                time_now = timezone.now()
                start_date = time_now - timedelta(
                    365 * int(int(maid_max_age) + 1) +
                    int(int(maid_max_age) // 4)
                )
                end_date = time_now - timedelta(
                    365 * int(int(maid_min_age)) + int(int(maid_min_age) // 4)
                )
                qs = qs.filter(
                    date_of_birth__range=(
                        start_date,
                        end_date
                    )
                )

                language_list = []
                maid_sl_english = query_params.get("sl_english")
                if maid_sl_english:
                    language_list.append(MaidLanguage.objects.get(
                        language=MaidLanguageChoices.ENGLISH))
                maid_sl_mandarin = query_params.get("sl_mandarin")
                if maid_sl_mandarin:
                    language_list.append(MaidLanguage.objects.get(
                        language=MaidLanguageChoices.MANDARIN))
                maid_sl_chinese_dialect = query_params.get(
                    "sl_chinese_dialect")
                if maid_sl_chinese_dialect:
                    language_list.append(MaidLanguage.objects.get(
                        language=MaidLanguageChoices.CHINESE_DIALECT))
                maid_sl_malay = query_params.get("sl_malay")
                if maid_sl_malay:
                    language_list.append(MaidLanguage.objects.get(
                        language=MaidLanguageChoices.MALAY))
                maid_sl_tamil_hindi = query_params.get("sl_tamil_hindi")
                if maid_sl_tamil_hindi:
                    language_list.append(MaidLanguage.objects.get(
                        language=MaidLanguageChoices.HINDI_TAMIL))

                if language_list:
                    qs = qs.filter(
                        languages__in=language_list
                    )
                responsibility_list = []
                maid_resp_GEH = query_params.get("resp_GEH")
                if maid_resp_GEH:
                    responsibility_list.append(MaidResponsibility.objects.get(
                        name=MaidResponsibilityChoices.MAID_RESP_GENERAL_HOUSEWORK))

                maid_resp_COK = query_params.get("resp_COK")
                if maid_resp_COK:
                    responsibility_list.append(MaidResponsibility.objects.get(
                        name=MaidResponsibilityChoices.MAID_RESP_COOKING))

                maid_resp_CFI = query_params.get("resp_CFI")
                if maid_resp_CFI:
                    responsibility_list.append(MaidResponsibility.objects.get(
                        name=MaidResponsibilityChoices.MAID_RESP_CARE_FOR_INFANTS_CHILDREN))

                maid_resp_CFE = query_params.get("resp_CFE")
                if maid_resp_CFE:
                    responsibility_list.append(MaidResponsibility.objects.get(
                        name=MaidResponsibilityChoices.MAID_RESP_CARE_FOR_ELDERLY))

                maid_resp_CFD = query_params.get("resp_CFD")
                if maid_resp_CFD:
                    responsibility_list.append(MaidResponsibility.objects.get(
                        name=MaidResponsibilityChoices.MAID_RESP_CARE_FOR_DISABLED))

                if responsibility_list:
                    qs = qs.filter(
                        responsibilities__in=responsibility_list
                    )
            return qs
        else:
            return None


class GeneralEnquiryListCreateAPIView(ListCreateAPIView):
    queryset = GeneralEnquiry.objects.all()
    serializer_class = GeneralEnquiryModelSerializer


class ShortlistedEnquiryListCreateAPIView(ListCreateAPIView):
    queryset = ShortlistedEnquiry.objects.all()
    serializer_class = ShortlistedEnquiryModelSerializer


class PotentialEmployerListCreateAPIView(ListCreateAPIView):
    queryset = PotentialEmployer.objects.all()
    serializer_class = PotentialEmployerModelSerializer


class PotentialEmployerLoginAPIView(GenericAPIView):
    queryset = PotentialEmployer.objects.all()
    serializer_class = PotentialEmployerModelSerializer
    lookup_field = 'user__email'

    def get_object(self, email):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.

        filter_kwargs = {self.lookup_field: email}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def post(self, request, *args, **kwargs):
        user_details = request.data.get('user')
        instance = self.get_object(user_details.get('email'))
        serializer = self.get_serializer(instance)
        try:
            res = serializer.auth(data=user_details)
        except Exception:
            res = {
                'message': 'Unsuccessful Login'
            }
            return Response(res, status=400)
        else:
            return Response(res, status=200)

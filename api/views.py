import random

from django.db.models import query
from rest_framework.response import Response

from enquiry.models import GeneralEnquiry
from maid.models import Maid
from accounts.models import PotentialEmployer
from rest_framework.generics import (CreateAPIView, GenericAPIView, ListAPIView,
                                     ListCreateAPIView, RetrieveAPIView, get_object_or_404)
from rest_framework_api_key.permissions import HasAPIKey

from .serializers import (GeneralEnquiryModelSerializer, MaidSerializer,
                          PotentialEmployerModelSerializer, SlimMaidSerializer)


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
            return self.queryset.filter(agency__api_auth_id=api_auth_id)
        else:
            return None


class GeneralEnquiryListCreateAPIView(ListCreateAPIView):
    queryset = GeneralEnquiry.objects.all()
    serializer_class = GeneralEnquiryModelSerializer


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
            res = serializer.auth()
        except Exception as e:
            raise Exception(e)
            res = {
                'message': 'Unsuccessful Login'
            }
            return Response(res, status=400)
        else:
            return Response(res, status=200)

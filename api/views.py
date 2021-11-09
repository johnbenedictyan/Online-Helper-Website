from rest_framework.generics import ListAPIView, RetrieveAPIView
from maid.models import Maid
from rest_framework_api_key.permissions import HasAPIKey

from .serializers import MaidSerializer


class MaidRetrieveAPIView(RetrieveAPIView):
    queryset = Maid.objects.all()
    serializer_class = MaidSerializer


class MaidListAPIView(ListAPIView):
    permission_classes = [HasAPIKey]
    queryset = Maid.objects.all()
    serializer_class = MaidSerializer

    def get_queryset(self):
        api_auth_id = self.request.META.get('HTTP_AGENCY_AUTH_ID', None)
        if api_auth_id:
            return self.queryset.filter(agency__api_auth_id=api_auth_id)
        else:
            return None

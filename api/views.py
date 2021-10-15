from maid.models import Maid
from rest_framework import viewsets
from rest_framework_api_key.permissions import HasAPIKey

from .serializers import MaidSerializer


class MaidViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [HasAPIKey]
    serializer_class = MaidSerializer
    queryset = Maid.objects.all()

    def get_queryset(self):
        api_auth_id = self.request.META.get('HTTP_AGENCY_AUTH_ID', None)
        if api_auth_id:
            return self.queryset.filter(agency__api_auth_id=api_auth_id)
        else:
            return None

from rest_framework import routers

from .views import MaidViewSet

router = routers.DefaultRouter()
router.register(r'maids', MaidViewSet)

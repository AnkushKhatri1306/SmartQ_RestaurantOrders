from rest_framework import routers
from .views import *

router = routers.SimpleRouter()

router.register(r'rest', OrderDetailViewset)

urlpatterns = router.urls
from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = router.urls
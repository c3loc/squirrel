from django.urls import include, path
from rest_framework import routers
from squirrel.api import views

router = routers.DefaultRouter()
router.register(r"products", views.ProductViewSet)

urlpatterns = [path("", include(router.urls))]

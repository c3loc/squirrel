from rest_framework import permissions, viewsets
from squirrel.api.serializers import ProductSerializer
from squirrel.orders.models import Product


class ProductViewSet(viewsets.ModelViewSet):
    """
    Read-Only API endpoint for products
    """

    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

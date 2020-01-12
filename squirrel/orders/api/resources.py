from orders.models import Product
from tastypie.resources import ModelResource

from . import SquirrelDjangoAuthorization


class ProductResource(ModelResource):
    class Meta:
        queryset = Product.objects.all()
        allowed_methods = ["get"]
        authorization = SquirrelDjangoAuthorization()

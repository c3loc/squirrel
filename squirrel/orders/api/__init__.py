"""We need to override the Django-Admin-like behavior that change permission is needed to read"""
from tastypie.authorization import DjangoAuthorization


class SquirrelDjangoAuthorization(DjangoAuthorization):
    READ_PERM_CODE = "view"

from django.contrib import admin
from squirrel.accounts.models import Account, Transaction

admin.site.register(Account)
admin.site.register(Transaction)

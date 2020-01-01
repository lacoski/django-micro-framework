from django.contrib import admin

from micro_framework.jwt_auth.models import Policy

# Register your models here.

class PolicyAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Policy, PolicyAdmin)

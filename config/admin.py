from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from decouple import config

class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        tenant_code = request.db_alias
        return redirect(f'/{config("ADMIN_URL")}/{tenant_code}/')


custom_admin_site = CustomAdminSite(name='custom_admin')

from django.contrib.admin import AdminSite
from django.shortcuts import redirect
from decouple import config

class TenantAdminSite(AdminSite):
    def __init__(self, tenant_code, *args, **kwargs):
        self.tenant_code = tenant_code
        super().__init__(*args, **kwargs)

    def index(self, request, extra_context=None):
        return redirect(f'/{config("ADMIN_URL")}/{self.tenant_code}/')

admin_default = TenantAdminSite('default', name='admin_default')
admin_test = TenantAdminSite('test', name='admin_test')
admin_fixbazi = TenantAdminSite('fix-bazi', name='admin_fixbazi')

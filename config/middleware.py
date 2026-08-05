from django.utils.deprecation import MiddlewareMixin
from threading import local

_tenant_local = local()

class TenantDatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant_code = request.headers.get('X-Tenant-ID')

        tenant_mapping = {
            'fix-bazi': 'fix-bazi',
        }

        db_name = tenant_mapping.get(tenant_code)

        if db_name:
            _tenant_local.db = db_name
            request.db_alias = db_name
        else:
            _tenant_local.db = 'default'
            request.db_alias = 'default'

    def process_response(self, request, response):
        if hasattr(_tenant_local, 'db'):
            del _tenant_local.db
        return response

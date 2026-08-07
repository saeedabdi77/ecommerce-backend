from decouple import config
from django.utils.deprecation import MiddlewareMixin
from threading import local

_tenant_local = local()

class TenantDatabaseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant_code = request.headers.get('X-Tenant-ID')

        if not tenant_code:
            path = request.path
            if path.startswith(f'/{config("ADMIN_URL")}/default/'):
                tenant_code = 'default'
            elif path.startswith(f'/{config("ADMIN_URL")}/test/'):
                tenant_code = 'test'
            elif path.startswith(f'/{config("ADMIN_URL")}/fix-bazi/'):
                tenant_code = 'fix-bazi'

        tenant_mapping = {
            'default': 'default',
            'test': 'default',
            'fix-bazi': 'repair_console_db',
        }

        db_name = tenant_mapping.get(tenant_code)

        print('mmmmmmmmmmmmmmmmmmmmmmmm')
        print(request.path)
        print(request.headers)
        print(db_name)
        print('mmmmmmmmmmmmmmmmmmmmmmmm')

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

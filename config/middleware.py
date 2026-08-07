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


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/firing-bowl/"):
            print("-------------")
            print("path:", request.path)
            print("router db:", getattr(_tenant_local, "db", None))
            print("user:", request.user)
            print("is_authenticated:", request.user.is_authenticated)
            print("is_staff:", request.user.is_staff)
            print("is_superuser:", request.user.is_superuser)
            print("backend:", request.session.get("_auth_user_backend"))
            print("session:", request.session.get("_auth_user_id"))
        return self.get_response(request)
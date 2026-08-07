from config.middleware import _tenant_local


class SessionRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'sessions':
            print('sssssssssssssssss')
            print(getattr(_tenant_local, 'db', 'default'))
            print('sssssssssssss')
            return getattr(_tenant_local, 'db', 'default')
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'sessions':
            return getattr(_tenant_local, 'db', 'default')
        return None


class TenantDatabaseRouter:

    def _get_db(self):
        print('rrrrrrrrrrrrrrrrrr')
        print(getattr(_tenant_local, 'db', 'default'))
        print('rrrrrrrrrrrrrrrrrr')
        return getattr(_tenant_local, 'db', 'default')

    def db_for_read(self, model, **hints):
        return self._get_db()

    def db_for_write(self, model, **hints):
        return self._get_db()

    def allow_relation(self, obj1, obj2, **hints):
        db1 = getattr(obj1, '_state', None) and obj1._state.db
        db2 = getattr(obj2, '_state', None) and obj2._state.db
        if db1 and db2 and db1 != db2:
            return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db in ['default', 'repair_console_db']

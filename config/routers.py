from threading import local

_thread_local = local()


class TenantDatabaseRouter:

    def _get_db(self):
        return getattr(_thread_local, 'db', 'default')

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

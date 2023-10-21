class DefaultDBRouter:
    route_app_labels = {
        "auth", "contenttypes", "admin", "sessions", "messages",
        "staticfiles", "rest_framework", "drf_yasg", "storages",
        "corsheaders"
        }

    def db_for_read(self, model, **hints):
        return "default" if model._meta.app_label in self.route_app_labels else None

    def db_for_write(self, model, **hints):
        return "default" if model._meta.app_label in self.route_app_labels else None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default" if app_label in self.route_app_labels else None


class SharedDBRouter:
    def db_for_read(self, model, **hints):
        return "shared_db"

    def db_for_write(self, model, **hints):
        return "shared_db"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return False

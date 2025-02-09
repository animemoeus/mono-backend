class WaifuAppRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "waifu":
            return "tidb"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "waifu":
            return "tidb"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "waifu":
            return db == "tidb"
        return None

import os
import sys


class TwitterDownloadAppRouter:
    # TODO: Fix this later to make sure we can use TiDB
    # The current problem is we not using TiDB for this app models
    # But the app still trying to migrate the models on TiDB server 💀
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if os.environ.get("PYTEST_CURRENT_TEST") or "test" in sys.argv:
            return db == "default"
        return None

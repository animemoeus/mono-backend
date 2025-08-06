from nz_store.tests import factories


def run():
    # factories.ProductFactory.create_batch(20)
    # factories.AccountStockFactory.create_batch(20)
    factories.TelegramUserFactory.create_batch(20)

import threading
import logging
from app.utils import functions


class AppThread(threading.Thread):
    app = None
    manager = None

    def __init__(self, app, manager):
        super().__init__()
        self.app = app
        self.manager = manager
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        pass

    pass


class Initer(AppThread):
    file = None

    def __init__(self, app, file, botmanager):
        super().__init__(app, botmanager)
        self.file = file
        pass

    def run(self):
        self.logger.debug('Running threads.Initer()')
        try:
            with self.app.app_context():
                functions.initialise_bot_from_file(
                    self.file,
                    self.manager
                )
        except Exception as e:
            self.logger.warning("threads.Initer() finished with fail:", e)
            return
        self.logger.debug('threads.Initer() finished with success')

    pass


class Loader(AppThread):
    def __init__(self, app, bot_manager):
        super().__init__(app, bot_manager)
        pass

    def run(self) -> None:
        print('Running threads.Loader()')
        try:
            success = False
            with self.app.app_context():
                success = self.manager.init_bots()
            print('threads.Loader() finished with success')
        except Exception as e:
            print('threads.Loader() finished with fail:', e)
            pass
        return success
        pass


class Worker(AppThread):
    def __init__(self, app, bot_manager, num_followers, priority = 3):
        super().__init__(app, bot_manager)
        self.num_followers = num_followers
        self.priority = priority
        pass

    def run(self) -> None:
        self.logger.info('Running threads.Worker()')
        try:
            with self.app.app_context():
                public_only = True if self.priority == 3 or self.priority == 1 else False
                private_only = True if self.priority == 3 or self.priority == 2 else False

                self.manager.start(self.num_followers, public_only, private_only)
                pass
        except Exception as e:
            self.logger.info('threads.Worker() finished with fail:', e)
            return
        self.logger.info('Finished threads.Worker() with success')
        pass

    pass

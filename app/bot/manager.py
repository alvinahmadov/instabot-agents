import logging
import logging.handlers
import threading
from datetime import date

from app.bot.worker import Worker
from app.bot.filter import Filter
from app.utils import functions


class Manager:
    filters: Filter
    loaded = False

    def __init__(self, database):
        self.workers = dict()
        self.comment = str()
        self._config = dict()
        self.timer = threading.Timer(10.0, self._check_work_state)
        self.timer.start()
        self.timer.join()
        from app.database import manager
        self.database: manager.Database = database
        self.logger = logging.getLogger('botmanager')
        self.logger.setLevel(logging.DEBUG)
        pass

    def __len__(self):
        return len(self.workers)

    def __bool__(self):
        return self.__len__() != 0

    def __getitem__(self, item):
        return self.workers[item]

    def _check_work_state(self):
        for worker in self.workers.values():
            if worker.state != Worker.State.ACTIVE:
                worker.logout()
            pass
        pass

    def init_bots(self):
        count = 0
        try:
            bots_data = self.database.retrieve_bots()
            if bots_data is None:
                return False

            self._config = self.database.load_config()
            self.filters = Filter(**self._config)
            for i, bot_data in enumerate(bots_data):
                targets = self.database.load_users(is_target = True)
                # load targets from database
                if targets is None:
                    continue
                bot_data['targets'] = ','.join([target['username'] for target in targets if bot_data['id'] == target['assignee']])
                self.create_bot(**bot_data)
                count += i + 1
        except Exception as e:
            print('Exception in BotManager.init_bots():', e)
        print('Loaded %i bots' % count)
        self.loaded = True
        return True
        pass

    def create_bot(self, **kwargs) -> bool:
        # Initialise bot
        logged_in, bot = functions.check_account(
            self.database.db,
            self.config,
            **kwargs
        )
        if logged_in:
            info = bot.get_user_info(bot.user_id, False)
            kwargs['id'] = bot.user_id
            kwargs['profile_pic_url'] = info['profile_pic_url']
            pass
        else:
            return False
        data = self.database.create_bot(bot, **kwargs)
        data['targets'] = kwargs['targets']
        return self._create(bot, **data)

    def _create(self, bot, **kwargs) -> bool:
        try:
            worker_name = kwargs['username']
            worker = Worker(self.config, bot, **kwargs)
            worker.profile_pic_url = bot.get_user_info(bot.user_id)["profile_pic_url"]

            stats = self.database.create_or_load_stats(
                worker.id,
                self.comment
            )
            worker.stats = Worker.Statistics(
                comment = stats["last_comment"],
                skiplist = stats["skiplist"],
                followlist = stats["followlist"]
            )
            self.workers[worker_name] = worker
            print("Bot %s created and added to Bot Manager" % worker_name)
            self.database.create_targets(bot, kwargs['targets'])
            return True
        except Exception as e:
            print("bot.manager._create():", e)
            return False

    def update_bot(self, bot, **kwargs):
        """
        Update here
        :param bot Bot which needs to be updated
        Parameters:
            username,
            password,
            fullname,
            proxy,
            external_url,
            profile_pic_url,
            biography,
            private
        """

        if 'targets' in kwargs:
            self.database.create_targets(bot, kwargs['targets'])
            pass
        data = self.database.update_bot(**kwargs)
        username = data['username']
        if username in self.workers.keys():
            worker = self.workers[username]
            worker.update(**data)
            worker.login()
            print('Bot %s updated' % username)
        else:
            print('Bot %s not updated, not loaded.' % username)
            pass
        pass

    def load_bot(self, username) -> dict or None:
        data = self.database.load_bot(username)
        return data

    def get_bots(self) -> list or None:
        bots = self.database.retrieve_bots()
        return bots

    def start(self,
              num_followers = 3,
              public_only = False,
              private_only = False):
        try:
            for name, worker in self.workers.items():
                worker.filter = self.filters.update(**self.database.load_config())
                worker.stats.comment = self.comment

                if worker.login():
                    worker.state = Worker.State.ACTIVE
                    if worker.stats.created_on is None:
                        worker.stats.created_on = date.today()
                        pass
                    pass
                else:
                    worker.state = Worker.State.INACTIVE
                    continue
                    pass

                self._parse_targets(worker)
                worker.parse(num_followers, public_only, private_only)
                self._save_followers(worker)
                worker.action(public = public_only, private = private_only)
                self._save_statistics(worker)
                if worker.state != Worker.State.INACTIVE:
                    worker.logout()
                    worker.state = Worker.State.FINISHED
        except Exception as e:
            self.logger.info('Exception in BotManager.start():', e)
        pass

    def _parse_targets(self, worker):
        self.logger.info('Parse targets')
        target_dict_list = self.database.load_users(True)
        for target_dict in target_dict_list:
            if target_dict is not None:
                assignee_id: int = target_dict['assignee']
                if assignee_id == worker.id:
                    target_name = target_dict['username']
                    worker.add_target(target_name)
                    pass
                pass
            pass
        pass

    def _save_followers(self, worker):
        try:
            for follower_list in worker.targets.values():
                self.logger.info("_save_followers", follower_list)
                for follower in follower_list:
                    if follower not in worker.stats.skiplist:
                        self.logger.info("Adding to database", follower)
                        self.database.create_accounts(worker.id, follower)
                    pass
                pass
        except Exception as e:
            self.logger.info("Exception in _save_followers:", e)
        pass

    def _save_statistics(self, worker):
        self.logger.info("BotManager._save_statistics(), ", worker.stats)
        self.database.update_stats(
            bot_id = worker.id,
            parsed_count = worker.stats.parsed,
            ignored_count =worker.stats.ignored,
            follow_request_count = worker.stats.follows_sent,
            comment_count = worker.stats.comment_count,
            last_comment = worker.comment,
            skiplist = worker.stats.skiplist,
            followlist = worker.stats.followlist
        )
        pass

    def stop(self):
        for worker in self.workers.values():
            worker.logout()
        pass

    def add_targets(self, bot_id, target_names = None):
        if target_names is not None:
            for target_name in target_names:
                self.workers[bot_id].add_target(target_name)
                pass
            pass
        pass

    def get_targets(self) -> list:  # list(dict)
        return self.database.load_users(True)

    def get_followers(self) -> list:
        return self.database.load_users(False)

    def get_state(self, bot_id):
        for bot in self.workers.values():
            if bot.key == bot_id:
                return True
        return False

    def get_nfollowers(self):
        sm = 0
        for bt in self.workers.values():
            sm += bt.bot_account.num_followers()
        return sm

    def get_nfollowing(self):
        sm = 0
        for bt in self.workers.values():
            sm += bt.bot_account.num_following()
        return sm

    def follow_user(self, target_name):
        for baccount in self.workers.values():
            baccount.request_to_follow(baccount.user_account_from_name(target_name))
        pass

    def get_stats(self):
        """
        Parse data from workers to items
        [{
        'id': 1,
        'bot_id': 31461774784,
        'parsed_count': 15,
        'ignored_count': 5,
        'follow_request_count': 0,
        'comment_count': 0,
        'last_comment': '',
        'skiplist': ['32536504186', '32505508350', '9464280686', '32279397733', '29799914633'],
        'created_on': datetime.date(2020, 4, 12)
        }]
        """
        parsed_count = 0
        ignored_count = 0
        follow_request_count = 0
        comment_count = 0
        data = []
        for worker in self.workers.values():
            data.append(self.database.load_stats(worker.id))
        return data

    @property
    def config(self):
        self._config = self.database.load_config()
        return self._config

    @property
    def num_active(self):
        return self._count_state(Worker.State.ACTIVE)

    @property
    def num_inactive(self):
        return self._count_state(Worker.State.INACTIVE)

    @property
    def num_waiting(self):
        return self._count_state(Worker.State.WAITING)

    @property
    def num_finished(self):
        return self._count_state(Worker.State.FINISHED)

    def _count_state(self, state):
        sm = 0
        for worker in self.workers.values():
            if worker.state == state:
                sm += 1
        return sm

    pass

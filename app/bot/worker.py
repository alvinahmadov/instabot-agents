import logging
import time
from datetime import date

from app.account import Account
from app.bot.filter import Filter
from app.bot.user import User
from app.utils.functions import gender_from_string
from instabot import Bot


class Worker(Account):
    filter = None

    def __init__(self, config, bot: Bot, **kwargs):
        Account.__init__(self)
        self._bot: Bot = bot
        self.stats = None
        self.id = kwargs['id']
        self.username = kwargs['username']
        self.fullname = kwargs['fullname']
        self.private = kwargs['private']
        self.biography = kwargs['biography']
        self.external_url = kwargs['external_url']
        self.profile_pic_url = kwargs.get('profile_pic_url', '')
        self._email = kwargs['email']
        self._password = kwargs['password']
        self._gender: int = gender_from_string(kwargs['gender'])
        self._proxy: str = kwargs['proxy']
        self._config = config
        self._is_logged_in = bot.api.is_logged_in
        self.state = Worker.State.WAITING if self.is_logged_in else Worker.State.INACTIVE
        self.filter: Filter
        self.boot_time = time.monotonic()
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())

    class State:
        ACTIVE = 0,
        INACTIVE = 1,
        WAITING = 2,
        FINISHED = 3
        pass

    class Statistics:
        targets: dict = dict()

        def __init__(self,
                     comment = '',
                     parsed = 0,
                     ignored = 0,
                     follows_sent = 0,
                     comment_count = 0,
                     created_on = None,
                     skiplist = None,
                     followlist = None):
            self.comment: str = comment
            self.parsed: int = parsed
            self.ignored: int = ignored
            self.follows_sent: int = follows_sent
            self.comment_count: int = comment_count
            self.created_on = created_on
            self.skiplist: set = set() if skiplist is None else skiplist
            self.followlist: set = set() if followlist is None else followlist
            pass

        def __repr__(self):
            return "<Statistics(parsed={parsed}, ignored={ignored}, follows_sent={follows_sent}, comment_count={comment_count}, " \
                   "created_on={created_on}, skiplist={skiplist}, followlist={followlist})>"\
                .format(parsed = self.parsed, ignored=self.ignored, follows_sent=self.follows_sent, comment_count=self.comment_count,
                        created_on=self.created_on, skiplist=self.skiplist, followlist=self.followlist)
            pass

        def stats(self):
            return {
                "parsed": self.parsed,
                "ignored": self.ignored,
                "follow_requests": self.follows_sent,
                "comment_count": self.comment_count,
                "last_comment": self.comment,
                "date": self.created_on,
                "targets": ','.join([target for target in self.targets.keys()]),
                "skiplist": ','.join(str(item) for item in self.skiplist),
                "followlist": ','.join(str(item) for item in self.followlist)
            }

        def update(self, **kwargs):
            self.parsed += kwargs.get('parsed_count', 0)
            self.ignored += kwargs.get('ignored_count', 0)
            self.follows_sent += kwargs.get('follows_sent', 0)
            self.comment_count += kwargs.get('comment_count', 0)
            self.comment = kwargs.get('last_comment', 0)
            self.skiplist += kwargs.get('skiplist', set())
            self.followlist += kwargs.get('followlist', set())
            pass

        pass

    def __repr__(self):
        return "<BotAccount(id={id}, username={username}, password={password}, " \
               "proxy={proxy}, external_url={external_url})>" \
            .format(
                id = self.id,
                username = self.username,
                password = self.password,
                proxy = self.proxy,
                external_url = self.external_url
            )
        pass

    @property
    def status_text(self):
        if self.state == Worker.State.ACTIVE:
            return 'active'
        elif self.state == Worker.State.INACTIVE:
            return 'inactive'
        elif self.state == Worker.State.WAITING:
            return 'waiting'
        else:
            return 'finished'
        pass

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, e):
        if self._check_value(e):
            self._email = e
        pass

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if self._check_value(password):
            self._password = password
        pass

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, g):
        self._gender = g

    @property
    def proxy(self):
        return self._proxy

    @proxy.setter
    def proxy(self, proxy):
        if self._check_value(proxy):
            self._proxy = proxy
        pass

    def add_target(self, target_name):
        """
        Before any action there must be added unique target
        :param target_name name of target
        """
        try:
            self.logger.info('Adding target %s to worker list' % target_name)
            self.stats.targets[target_name] = None
        except Exception as e:
            self.logger.info('Error in Worker.add_target():', e)
        pass

    @property
    def bot(self) -> Bot:
        return self._bot

    def login(self) -> bool:
        if self.is_logged_in:
            self.logger.info("Worker %s is already logged in" % self.username)
            self.state = Worker.State.WAITING
            return True
        self._is_logged_in = self.bot.login(
            username = self.username,
            password = self.password,
            proxy = self.proxy,
            is_threaded = True
        )

        if self.is_logged_in:
            self.logger.info("Worker %s is logged in" % self.username)
            self.state = Worker.State.WAITING
            return True
        else:
            self.logger.info("Worker %s can not logged in" % self.username)
            self.state = Worker.State.INACTIVE
            return False
        pass

    def logout(self):
        if self._is_logged_in:
            self.bot.logout()
            self.state = Worker.State.INACTIVE
            self._is_logged_in = False
            self.logger.info("Worker %s successfuly logged out" % self.username)
        else:
            self.logger.info("Worker %s is already logged out" % self.username)
        pass

    def update(self, **kwargs):
        self.proxy = kwargs.get('proxy')
        if self.is_logged_in:
            self.logout()
            self.bot.proxy = self.proxy
        if not self.is_logged_in:
            self.login()
            pass
        new_password = kwargs['password']
        if new_password is not None:
            if new_password != self.password:
                self.logger.info("Worker %s changed password from %s to %s"
                    % (self.username, self.password, new_password))
                self.bot.api.change_password(new_password)
                pass
            self.password = new_password
            pass

        self.fullname = kwargs.get('fullname', self.fullname)
        self.biography = kwargs.get('biography', self.biography)
        self.profile_pic_url = kwargs.get('profile_pic_url', self.profile_pic_url)
        self.email = kwargs.get('email', self.email)
        self.external_url = kwargs.get('external_url', self.external_url)

        # profile_data = {
        #     'username': self.username,
        #     'full_name': self.fullname.replace(' ', '+'),
        #     'external_url': self.external_url,
        #     'phone_number': "",
        #     'biography': self.biography.replace(' ', '+'),
        #     'email': self.email,
        #     'gender': gender_from_string(self.gender),
        #     'private': self.private
        # }
        # self._edit(profile_data)
        pass

    def _edit(self, profile_data):
        """
        Edit account
        """
        if profile_data['private'] != self.private:
            if self.private:
                self.bot.api.set_private_account()
            else:
                self.bot.api.set_public_account()
                pass
            pass
        self.login()
        url: str = str(profile_data['external_url'])
        first_name: str = str(profile_data['fullname'].replace(' ', '+'))
        bio: str = str(profile_data['biography'].replace(' ', '+'))
        email: str = str(profile_data['email'])
        gender = str(self.gender)
        # self.logger.info(','.join([url, first_name, bio, email, gender]))
        self.logger.info("Worker %s changed data in Instagram" % self.username)
        self.bot.api.edit_profile(
            url = url,
            phone = "",
            first_name = first_name,
            biography = bio,
            email = email,
            gender = gender
        )
        pass

    def approve_pending(self) -> bool:
        return self.bot.approve_pending_follow_requests()

    def reject_pending(self) -> bool:
        return self.bot.reject_pending_follow_requests()

    def ignore_parsed(self, user_id: str):
        for target_account in self.targets.values():
            if int(target_account.id) == int(user_id):
                return True
            pass
        pass
        return False

    def parse(self, number_of_followers = None,
              public = False, private = False):
        """
        Parse user for followers and then save them to the database
        for next actions for likes of media_amount count

        :param number_of_followers limit for parsing followers
        :type number_of_followers int

        :param public Parse only public accounts
        :param private Parse only private accounts

        """
        if number_of_followers == 0:
            number_of_followers = None
            pass

        self.logger.info("Worker %s is %s" % (self.username, self.status_text))
        for target_name in self.targets.keys():
            follower_ids = self.bot.get_user_followers(
                self.bot.get_user_id_from_username(target_name),
                number_of_followers
            )
            self.logger.info("Worker %s is parsing target %s" % (self.username, target_name))

            follower_accounts = list()

            for follower_id in follower_ids:
                follower = self.bot.get_user_info(follower_id)
                follower_account = User(**follower)
                is_private = follower_account.private

                if self.filter.eval(follower_account):
                    if public and private:
                        self.logger.info('Parsing all', follower_account)
                        follower_accounts.append(follower_account)
                    elif not is_private and public:
                        self.logger.info('Parsing only public', follower_account)
                        follower_accounts.append(follower_account)
                        pass
                    elif is_private and private:
                        self.logger.info('Parsing only private', follower_account)
                        follower_accounts.append(follower_account)
                        pass
                else:
                    self.stats.ignored += 1
                    self.stats.skiplist.add(follower_account.id)
                    self.logger.info("Worker %s: follower %s of %s doesn't match filters" %
                        (self.username, follower_account.username, target_name))
                    pass
            pass
            self.stats.targets[target_name] = follower_accounts
        pass

    def action(self,
               amount = 3,
               public = False,
               private = False):
        """
        Combine all actions (e.g. follow, like, comment) here
        """
        self.logger.info('Worker %s is running action' % self.username)
        try:
            for accounts in self.targets.values():
                if accounts is None:
                    return False
                for account in accounts:
                    if account.id in self.stats.skiplist:
                        continue
                    if public:
                        if not private:
                            if not account.private:
                                self.logger.info('Worker %s is running action only for public account %s'
                                    % (self.username, account.username))
                                self.post_comment_and_likes(account, amount)
                                self.stats.parsed += 1
                                pass
                        pass
                    if private:
                        if not public:
                            if account.private:
                                self.logger.info('Worker %s is running action only for private account %s'
                                    % (self.username, account.username))
                                if account.id not in self.stats.followlist:
                                    if self.request_to_follow(account):
                                        self.stats.parsed += 1
                                pass
                        pass
                    if public and private:
                        self.logger.info('Worker %s is running action for public and private accounts'
                            % self.username)
                        if not account.private:
                            self.post_comment_and_likes(account, amount)
                            self.stats.parsed += 1
                            self.logger.info('Worker %s is posting comment and likes to %s'
                                % (self.username, account.username))
                        else:
                            self.request_to_follow(account)
                            self.logger.info('Worker %s is going to follow %s'
                                % (self.username, account.username))
                            self.stats.parsed += 1
                            pass
                        pass
                pass
        except Exception as e:
            self.state = Worker.State.WAITING
            self.logger.info("Exiting Worker.action(): with fail:", e)
            return
        self.state = Worker.State.FINISHED
        pass

    def request_to_follow(self, account):
        self.logger.info("Following ", account)
        user_id = account.id if isinstance(account, User) else self.bot.convert_to_user_id(account)
        if user_id in self.stats.followlist:
            return False
        followed = self.bot.follow(user_id, False)
        if followed:
            self.stats.follows_sent += 1
            self.stats.followlist.add(user_id)
            self.logger.info('Worker %s is going to follow %s'
                % (self.username, account.username))
            return True
        return False

    def request_to_unfollow(self, account):
        user_id = account.id if isinstance(account, User) else self.bot.convert_to_user_id(account)
        unfollowed = self.bot.unfollow(user_id)
        if unfollowed:
            if self.stats.follows_sent != 0:
                self.stats.follows_sent -= 1
                pass
            if user_id in self.stats.followlist:
                self.stats.followlist.remove(user_id)
            self.logger.info('Worker %s is going to unfollow %s'
                % (self.username, account.username))
            return True
        return False

    def post_comment_and_likes(self, account, amount = 3):
        try:
            if self.stats.skiplist is not None:
                if account.id in self.stats.skiplist:
                    self.logger.info("In skiplist")
                    return

            medias = self.bot.get_last_user_medias(account.username, amount)
            if medias is None:
                return
            if len(medias) >= amount:
                self.logger.info('Worker %s is going to like %i media for user %s' % (self.username, amount, account.username))
                self.bot.like_medias(medias[:amount],
                                     check_media = False,
                                     username = account.username)
                self.logger.info('Worker %s is going to post comment for account %s'
                    % (self.username, account.username))
                commented = self.bot.comment(medias[0], self.stats.comment)
                if commented:
                    self.stats.comment_count += 1
        except Exception as e:
            self.state = Worker.State.INACTIVE
            self.logger.info('Error in Worker.post_comment_and_likes():', e)
        pass

    def get_target_account(self, user_id):
        for account in self.targets:
            if self.bot.get_user_id_from_username(account.username) == user_id:
                return account
            else:
                return -1
            pass
        pass

    def get_worktime(self):
        return time.monotonic() - self.bot.start_time

    def remove_target_account(self, user_id):
        for i in self.targets:
            if i.id() == user_id:
                self.targets.__delitem__(i)
                return True
        return False

    def user_account_from_name(self, username):
        user_id = self.bot.get_user_id_from_username(username)
        user_info = self.bot.get_user_info(user_id)
        return User(**user_info)

    @property
    def is_logged_in(self):
        self._is_logged_in = self.bot.api.is_logged_in
        return self._is_logged_in

    @property
    def comment(self):
        return self.stats.comment

    @comment.setter
    def comment(self, comment):
        self.stats.comment = comment
        pass

    @property
    def targets(self):
        return self.stats.targets

    @property
    def skiplist(self):
        return self.stats.skiplist

    @property
    def target_names(self):
        return [target for target in self.stats.targets.keys()]

    @property
    def followers(self):
        return [follower.username for follower in self.statistics.targets.values()]

    pass

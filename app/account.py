import enum


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AccountType(enum.Enum):
    DEFAULT = 0
    BUSINESS = 1


class Account:
    def __init__(self):
        self._id = 0
        self._username = ''
        self._fullname = ''
        self._biography = ''
        self._profile_pic_url = ''
        self._external_url = ''
        self._account_type = None
        self._is_private = False
        self._is_business = False
        self._num_followers = 0
        self._num_following = 0

    def __repr__(self):
        return '<Account(id: {id}, username: {username}, fullname: {fullname})>' \
            .format(id = self.id,
                    username = self.username,
                    fullname = self.fullname)

    @staticmethod
    def _check_value(value):
        return True if value is not None and not len(value) == 0 else False

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, user_id):
        self._id = user_id
        pass

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        if self._check_value(username):
            self._username = username
        pass

    @property
    def fullname(self):
        return self._fullname

    @fullname.setter
    def fullname(self, fullname):
        if self._check_value(fullname):
            self._fullname = fullname
        pass

    @property
    def biography(self):
        return self._biography

    @biography.setter
    def biography(self, desc):
        if self._check_value(desc):
            self._biography = desc
        pass

    @property
    def external_url(self):
        return self._external_url

    @external_url.setter
    def external_url(self, url):
        if self._check_value(url):
            self._external_url = url
        pass

    @property
    def account_type(self):
        return self._account_type

    @account_type.setter
    def account_type(self, account_type):
        self._account_type = account_type
        pass

    @property
    def profile_pic_url(self):
        return self._profile_pic_url

    @profile_pic_url.setter
    def profile_pic_url(self, pic_url):
        if self._check_value(pic_url):
            self._profile_pic_url = pic_url
        pass

    @property
    def private(self):
        return self._is_private

    @private.setter
    def private(self, is_private):
        self._is_private = is_private
        pass

    @property
    def business(self):
        return self._is_business

    pass

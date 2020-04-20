from app.account import Account, Singleton


class User(Account):
    def __init__(self, **kwargs):
        Account.__init__(self)
        self.id = kwargs['pk']
        self.username = kwargs['username']
        self.fullname = kwargs['full_name']
        self.private = kwargs['is_private']
        self.profile_pic_url = kwargs['profile_pic_url']
        self.biography = kwargs['biography']
        self.external_url = kwargs['external_url']
        self._stats = User.Stats(num_followers = kwargs['follower_count'],
                                 num_following = kwargs['following_count'],
                                 num_media = kwargs['media_count'],
                                 )
        pass

    class Stats:
        __metaclass__ = Singleton

        def __init__(self, num_followers = 0, num_following = 0, num_media = 0):
            self._num_followers = num_followers
            self._num_following = num_following
            self._num_media = num_media
            pass

        @property
        def num_followers(self):
            return self._num_followers
        pass

        @property
        def num_following(self):
            return self._num_following
        pass

        @property
        def num_media(self):
            return self._num_media
        pass

    @property
    def num_followers(self):
        return self._stats.num_followers

    @property
    def num_following(self):
        return self._stats.num_following

    @property
    def num_media(self):
        return self._stats.num_media

    pass

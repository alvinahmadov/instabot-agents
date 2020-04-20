import logging

from app.bot.user import User

from app.utils.functions import (
    get_attr_bool,
    get_attr_int
)


class Filter:
    def __init__(self, **kwargs):
        # maybe None if we choose both private and public accounts
        self.filter_users = get_attr_bool('filter_users', **kwargs)
        self.filter_business_accounts = get_attr_bool('filter_business_accounts', **kwargs)
        self.filter_users_without_profile_photo = get_attr_bool('filter_users_without_profile_photo', **kwargs)
        self.filter_users_with_external_url = get_attr_bool('filter_users_with_external_url', **kwargs)
        self.max_followers_to_follow = get_attr_int('max_followers_to_follow', **kwargs)
        self.min_followers_to_follow = get_attr_int('min_followers_to_follow', **kwargs)
        self.max_following_to_follow = get_attr_int('max_following_to_follow', **kwargs)
        self.min_following_to_follow = get_attr_int('min_following_to_follow', **kwargs)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        pass

    def __repr__(self):
        return '<Filter(filter_users={},filter_business_accounts={},filter_users_without_profile_photo={}, ' \
               'filter_users_with_external_url={})>' \
            .format(self.filter_users, self.filter_business_accounts, self.filter_users_without_profile_photo,
                    self.filter_users_with_external_url)

    def update(self, **kwargs):
        self.filter_users = kwargs.get('filter_users', self.filter_users)
        self.filter_business_accounts = kwargs.get('filter_business_accounts', self.filter_business_accounts)
        self.filter_users_without_profile_photo = kwargs.get('filter_users_without_profile_photo', self.filter_users_without_profile_photo)
        self.filter_users_with_external_url = kwargs.get('filter_users_with_external_url', self.filter_users_with_external_url)
        self.max_followers_to_follow = kwargs.get('max_followers_to_follow', self.max_followers_to_follow)
        self.min_followers_to_follow = kwargs.get('min_followers_to_follow', self.min_followers_to_follow)
        self.max_following_to_follow = kwargs.get('max_following_to_follow', self.max_following_to_follow)
        self.min_following_to_follow = kwargs.get('min_following_to_follow', self.min_following_to_follow)
        return self

    def set_followers_range(self, nmin, nmax):
        assert 0 <= nmin < nmax
        self.min_followers_to_follow = nmin
        self.max_followers_to_follow = nmax
        pass

    def set_following_range(self, nmin, nmax):
        assert 0 <= nmin < nmax
        self.min_following_to_follow = nmin
        self.max_following_to_follow = nmax
        pass

    def eval(self, user_account: User):
        has_external_url = self.eval_external_url(user_account.external_url)
        matches_followers_range = self.eval_followers_range(user_account.num_followers)
        matches_following_range = self.eval_following_range(user_account.num_following)
        is_business = self.eval_business(user_account.business)
        result = has_external_url and matches_followers_range \
            and matches_following_range and is_business
        return result

    def eval_business(self, is_business: bool) -> bool:
        if self.filter_business_accounts:
            if not is_business:
                return True
        return False

    def eval_external_url(self, url):
        has_external_url = len(url) > 0 or url != ''
        if self.filter_users_with_external_url:
            if not has_external_url:
                return True
            pass
        return False

    def eval_followers_range(self, count):
        return self.min_followers_to_follow <= count <= self.max_followers_to_follow

    def eval_following_range(self, count):
        return self.min_following_to_follow <= count <= self.max_following_to_follow

    pass

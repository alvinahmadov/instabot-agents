from datetime import date

import settings
from app.database import db


class Settings(db.Model):
    __table_args__ = {"schema": settings.SQLALCHEMY_DATABASE_SCHEMA}
    __tablename__ = "settings"
    id = db.Column(db.Integer(), primary_key = True)
    max_likes_per_day = db.Column(db.Integer(), default = 600)
    max_unlikes_per_day = db.Column(db.Integer(), default = 600)
    max_follows_per_day = db.Column(db.Integer(), default = 350)
    max_unfollows_per_day = db.Column(db.Integer(), default = 200)
    max_comments_per_day = db.Column(db.Integer(), default = 100)
    max_likes_to_like = db.Column(db.Integer(), default = 2000)
    filter_users = db.Column(db.Boolean(), default = 1)
    filter_business_accounts = db.Column(db.Boolean(), default = 1)
    filter_verified_accounts = db.Column(db.Boolean(), default = 1)
    filter_users_without_profile_photo = db.Column(db.Boolean(), default = 1)
    filter_users_with_external_url = db.Column(db.Boolean(), default = 1)
    max_followers_to_follow = db.Column(db.Integer(), default = 5000)
    min_followers_to_follow = db.Column(db.Integer(), default = 10)
    max_following_to_follow = db.Column(db.Integer(), default = 2000)
    min_following_to_follow = db.Column(db.Integer(), default = 10)
    max_followers_to_following_ratio = db.Column(db.Integer(), default = 10)
    max_following_to_followers_ratio = db.Column(db.Integer(), default = 2)
    min_media_count_to_follow = db.Column(db.Integer(), default = 3)
    max_following_to_block = db.Column(db.Integer(), default = 2000)
    like_delay = db.Column(db.Integer(), default = 30)
    unlike_delay = db.Column(db.Integer(), default = 30)
    follow_delay = db.Column(db.Integer(), default = 30)
    unfollow_delay = db.Column(db.Integer(), default = 30)
    comment_delay = db.Column(db.Integer(), default = 30)

    def __repr__(self):
        from app.utils.functions import config_to_dict
        self_dict = config_to_dict(self)
        msg = [k + '=' + str(v) for k, v in self_dict.items()]
        return ','.join(msg)

    pass


class Stats(db.Model):
    __table_args__ = {"schema": settings.SQLALCHEMY_DATABASE_SCHEMA}  # public
    __tablename__ = "stats"
    id = db.Column(db.Integer, primary_key = True)
    bot_id = db.Column(db.BigInteger, nullable = False)
    parsed_count = db.Column(db.Integer, default = 0)
    ignored_count = db.Column(db.Integer, default = 0)
    follow_request_count = db.Column(db.Integer, default = 0)
    comment_count = db.Column(db.Integer, default = 0)
    last_comment = db.Column(db.Text, nullable = True)
    followlist = db.Column(db.Text, default = '')
    skiplist = db.Column(db.Text, default = '')
    whitelist = db.Column(db.Text, default = '')
    blacklist = db.Column(db.Text, default = '')
    created_on = db.Column(db.Date, default = date.today())

    def __repr__(self):
        return "<Stats(bot_id={bot_id}, parsed_count={parsed_count}, ignored_count={ignored_count}, " \
               "follow_request_count={follow_request_count}, comment_count={comment_count}, " \
               "skiplist={skiplist}, followlist={followlist})>"\
            .format(
                bot_id = self.bot_id,
                parsed_count = self.parsed_count,
                ignored_count = self.ignored_count,
                follow_request_count = self.follow_request_count,
                comment_count = self.comment_count,
                skiplist = self.skiplist,
                followlist = self.followlist
            )
        pass

    pass


class Bots(db.Model):
    __table_args__ = {"schema": settings.SQLALCHEMY_DATABASE_SCHEMA}
    __tablename__ = "bots"
    id = db.Column(db.BigInteger(), primary_key = True, autoincrement = False)
    username = db.Column(db.String(255), nullable = False)
    fullname = db.Column(db.String(255), default = '')
    email = db.Column(db.Text, nullable = False)
    password = db.Column(db.String(64), nullable = False)
    proxy = db.Column(db.String(64), nullable = True)
    profile_pic_url = db.Column(db.Text, nullable = False)
    external_url = db.Column(db.String(64), nullable = True)
    biography = db.Column(db.Text, nullable = True)
    gender = db.Column(db.String(10), nullable = True)
    private = db.Column(db.Boolean, nullable = False, default = False)
    checkpoint = db.Column(db.LargeBinary(), nullable = True)
    created_on = db.Column(db.Date, default = date.today())
    updated_on = db.Column(db.Date,
                           default = date.today(),
                           onupdate = date.today())

    def __repr__(self):
        return "<Bot(username={username}, fullname={fullname}, email={email}, password={password}, " \
               "proxy={proxy}, external_url={external_url}, gender={gender}, is_private={private})>" \
            .format(
                username = self.username,
                fullname = self.fullname,
                email = self.email,
                password = self.password,
                proxy = self.proxy,
                external_url = self.external_url,
                gender = self.gender,
                private = bool(self.private)
            )

    pass


class Users(db.Model):
    __table_args__ = {"schema": settings.SQLALCHEMY_DATABASE_SCHEMA}
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key = True)
    username = db.Column(db.String(64), nullable = False)
    fullname = db.Column(db.String(64), nullable = False)
    profile_pic_url = db.Column(db.String(255), nullable = False)
    external_url = db.Column(db.String(64), nullable = True)
    biography = db.Column(db.Text, nullable = True)
    is_business = db.Column(db.Boolean, nullable = False, default = False)
    is_private = db.Column(db.Boolean, nullable = False, default = False)
    is_target = db.Column(db.Boolean, nullable = False, default = False)
    num_media = db.Column(db.Integer, default = 0)
    num_followers = db.Column(db.Integer, default = 0)
    num_following = db.Column(db.Integer, default = 0)
    assignee = db.Column(db.BigInteger, nullable = False)
    created_on = db.Column(db.Date,
                           nullable = False,
                           default = date.today())

    def __repr__(self):
        user_type = "Target" if self.is_target else "Follower"
        if self.is_target:
            return "<{type}(id={id}, assignee={assignee}, username={username}, fullname={fullname}, " \
                   "external_url={url}, is_business={is_business}, is_private={is_private}, is_target={is_target})>" \
                .format(
                    type = user_type,
                    id = self.id,
                    assignee = self.assignee,
                    username = self.username,
                    fullname = self.fullname,
                    url = self.external_url,
                    is_business = self.is_business,
                    is_private = self.is_private,
                    is_target = self.is_target
                )
        pass

    pass

import logging
from datetime import date

from app.database.models import (
    Bots as BotModel,
    Stats as StatModel,
    Users as UserModel,
    Settings as SettingModel
)
from app.utils.functions import (
    bot_to_dict,
    stats_to_dict,
    user_to_dict,
    config_to_dict
)


class Database:
    db = None

    def __init__(self, database):
        self.db = database
        self.logger = logging.getLogger(__name__)
        pass

    def truncate(self, tablename):
        self.db.session.execute('TRUNCATE TABLE %s' % tablename)
        self.db.session.commit()
        pass

    # begin configuration operations

    def save_config(self, config: dict):
        print("Running db_manager.save_config()")
        if not self.db.session.query(
                SettingModel
        ).count():
            cmodel = SettingModel()
            self.db.session.add(cmodel)
        else:
            cmodel = self.db.session.query(SettingModel).first()
            cmodel.max_likes_per_day = config.get("max_likes_per_day", cmodel.max_likes_per_day)
            cmodel.max_unlikes_per_day = config.get("max_unlikes_per_day", cmodel.max_unlikes_per_day)
            cmodel.max_follows_per_day = config.get("max_follows_per_day", cmodel.max_follows_per_day)
            cmodel.max_unfollows_per_day = config.get("max_unfollows_per_day", cmodel.max_unfollows_per_day)
            cmodel.max_comments_per_day = config.get("max_comments_per_day", cmodel.max_comments_per_day)
            cmodel.max_likes_to_like = config.get("max_likes_to_like", cmodel.max_likes_to_like)
            cmodel.filter_users = config.get("filter_users", cmodel.filter_users)
            cmodel.filter_business_accounts = config.get("filter_business_accounts", cmodel.filter_business_accounts)
            cmodel.filter_verified_accounts = config.get("filter_verified_accounts", cmodel.filter_verified_accounts)
            cmodel.filter_users_without_profile_photo = config.get("filter_users_without_profile_photo",
                                                                   cmodel.filter_users_without_profile_photo)
            cmodel.filter_users_with_external_url = config.get("filter_users_with_external_url",
                                                               cmodel.filter_users_with_external_url)
            cmodel.max_followers_to_follow = config.get("max_followers_to_follow", cmodel.max_followers_to_follow)
            cmodel.min_followers_to_follow = config.get("min_followers_to_follow", cmodel.min_followers_to_follow)
            cmodel.max_following_to_follow = config.get("max_following_to_follow", cmodel.max_following_to_follow)
            cmodel.min_following_to_follow = config.get("min_following_to_follow", cmodel.min_following_to_follow)
            cmodel.max_followers_to_following_ratio = config.get("max_followers_to_following_ratio",
                                                                 cmodel.max_followers_to_following_ratio)
            cmodel.max_following_to_followers_ratio = config.get("max_following_to_followers_ratio",
                                                                 cmodel.max_following_to_followers_ratio)
            cmodel.min_media_count_to_follow = config.get("min_media_count_to_follow", cmodel.min_media_count_to_follow)
            cmodel.max_following_to_block = config.get("max_following_to_block", cmodel.max_following_to_block)
            cmodel.like_delay = config.get("like_delay", cmodel.like_delay)
            cmodel.unlike_delay = config.get("unlike_delay", cmodel.unlike_delay)
            cmodel.follow_delay = config.get("follow_delay", cmodel.follow_delay)
            cmodel.unfollow_delay = config.get("unfollow_delay", cmodel.unfollow_delay)
            cmodel.comment_delay = config.get("comment_delay", cmodel.comment_delay)
            self.db.session.commit()
            pass
        print("Exiting db_manager.save_config() with success")
        pass

    def load_config(self) -> dict:
        configm: SettingModel = self.db.session.query(SettingModel).first()
        return config_to_dict(configm)

    # end configuration operations
    # begin bot operations

    def create_bot(self, bot, **kwargs) -> dict or None:
        """
        Adds target ids to worker's targets
        :returns updated bot data model
        """
        try:
            print("Running db_manager.create_bot():1")
            botm = self.db.session.query(
                BotModel
            ).filter(
                BotModel.id == kwargs['id']
            ).one()
            return bot_to_dict(botm)
        except Exception as e:
            print('DatabaseManager.create_bot()1: no bot in database: %s' % e)
            pass

        try:
            print("Running DatabaseManager.create_bot():2")
            bid = kwargs.get('id')
            username = kwargs.get('username')
            fullname = kwargs.get('fullname')
            email = kwargs.get('email')
            password = kwargs.get('password')
            proxy = kwargs.get('proxy')
            external_url = kwargs.get('external_url')
            profile_pic_url = kwargs.get('profile_pic_url')
            biography = kwargs.get('biography', '')
            private = kwargs.get('private', False)
            gender = kwargs.get('gender')
            if bot.api.is_logged_in:
                botm = BotModel(
                    id = bid,
                    username = username,
                    fullname = fullname,
                    email = email,
                    password = password,
                    proxy = proxy,
                    external_url = external_url,
                    gender = gender,
                    biography = biography,
                    private = private,
                    profile_pic_url = profile_pic_url
                )
                self.db.session.add(botm)
                self.db.session.commit()
                results = bot_to_dict(botm)
                print("Exiting DatabaseManager.create_bot():2 with success")
                return results
            else:
                raise ValueError("No such user in Instagram")
        except Exception as e:
            print('DatabaseManager:create_bot() %s' % e)
            return None
        pass

    def update_bot(self, **kwargs):
        """
        When data loaded from file, we need to check if data exists in
        database. If it exists and differs from file specified then
        change it else return

        :param kwargs new data for bot
        :param bot initialised bot with old data
        """
        bmodel = self.db.session.query(
            BotModel
        ).filter(
            BotModel.username == kwargs['username']
        ).one()
        bmodel.password = kwargs.get('password', bmodel.password)
        bmodel.fullname = kwargs.get('fullname', bmodel.fullname)
        bmodel.email = kwargs.get('email', bmodel.email)
        bmodel.proxy = kwargs.get('proxy', bmodel.proxy)
        bmodel.external_url = kwargs.get('external_url', '')
        bmodel.gender = kwargs.get('gender', bmodel.gender)
        bmodel.profile_pic_url = kwargs.get('profile_pic_url', bmodel.profile_pic_url)
        bmodel.biography = kwargs.get('biography', '')
        bmodel.private = kwargs.get('private', bmodel.private)
        self.db.session.commit()
        return bot_to_dict(bmodel)
        pass

    def load_bot(self, bot_name) -> dict or None:
        """
        Get bot data from database
        :param bot_name name of the bot's account
        :type bot_name str

        :returns bot data dict or None
        """
        print('Running db_manager.load_bot()')
        try:
            bmodel = self.db.session.query(
                BotModel
            ).filter(
                BotModel.username == bot_name
            ).one()
            kwargs = bot_to_dict(bmodel)
            print('Exiting db_manager.load_bot() with success')
            return kwargs
        except Exception as e:
            print('Exiting db_manager.load_bot() with fail', e)
            pass
        return None

    def retrieve_bots(self) -> dict or None:
        """
        Get bot data from database

        :returns bot data dict or None
        """
        try:
            bmodel_list = self.db.session.query(
                BotModel
            ).all()
            return [bot_to_dict(bmodel) for bmodel in bmodel_list]
        except Exception as e:
            print('database.manager.retrieve_bots():', e)
            return None
        pass

    # end bot operations
    # begin user operations

    def create_users(self, **kwargs):
        """
        Called from db_manager.create_bot or from bot_account.parse
        """
        try:
            user = self.db.session.query(
                UserModel
            ).filter(UserModel.id == kwargs['pk'])\
                .one()
            return
        except Exception as e:
            pass

        try:
            user = UserModel(
                id = kwargs['pk'],
                username = kwargs['username'],
                fullname = kwargs['full_name'],
                profile_pic_url = kwargs['profile_pic_url'],
                external_url = kwargs['external_url'],
                biography = kwargs['biography'],
                is_business = kwargs['is_business'],
                is_private = kwargs['is_private'],
                is_target = kwargs.get('is_target', False),
                num_media = kwargs['media_count'],
                num_followers = kwargs['follower_count'],
                num_following = kwargs['following_count'],
                assignee = kwargs['assignee']
            )
            self.db.session.add(user)
            self.db.session.commit()
            print('Created user %s, which is %s' % (user.username, 'target' if user.is_target else 'follower'))
        except Exception:
            print('Cannot create user %s:' % kwargs['username'])
            pass
        pass

    def create_accounts(self,
                        assignee,
                        account,
                        is_target = False):
        """
        Called from db_manager.create_bot or from bot_account.parse
        """
        try:
            self.db.session.query(
                UserModel
            ).filter(
                assignee == UserModel.assignee
            ).filter(
                is_target = UserModel.is_target
            ).one()
            return
        except Exception:
            print("User %s doesn't exist in database" % account.username)
            pass

        try:
            user = UserModel(
                id = account.id,
                username = account.username,
                fullname = account.fullname,
                profile_pic_url = account.profile_pic_url,
                external_url = account.external_url,
                biography = account.biography,
                is_business = account.business,
                is_private = account.private,
                is_target = is_target,
                num_media = account.num_media,
                num_followers = account.num_followers,
                num_following = account.num_following,
                assignee = assignee
            )
            self.db.session.add(user)
            self.db.session.commit()
            print('Created user %s, which is %s' % (user.username, 'target' if user.is_target else 'follower'))
        except Exception as e:
            print('Cannot create user %s: %s' % (account.username, e))
            pass
        pass

    def load_users(self, is_target = False) -> list or None:
        try:
            users: list = self.db.session.query(
                UserModel
            ).filter(
                UserModel.is_target == is_target
            ).all()
            result = []
            if len(users) > 0:
                for user in users:
                    result.append(user_to_dict(user))
            print('Exiting db_manager.load_users() with success')
            return result
        except Exception as e:
            print('Exiting db_manager.load_users() with fail', e)
            pass
        return None
        pass

    def create_targets(self, bot, targets):
        """
        Create targets in create_bot and update_bot

        :param targets comma separated list of targets to parse or single target
        :param bot
        """

        try:
            assignee = bot.user_id
            target_names = targets.split(',') if ',' in targets else [targets]
            for target_name in target_names:
                target_info = bot.get_user_info(
                        bot.get_user_id_from_username(target_name.strip(' ')),
                        use_cache = False)
                if target_info is not None:
                    if isinstance(target_info, dict):
                        target_info['is_target'] = True
                        target_info['assignee'] = assignee
                        self.create_users(**target_info)
                        pass
                    pass
                pass
        except Exception as e:
            print("No target %s: %s" % (target_name, e))
            pass
        pass

    def load_targets(self, assignee_id):
        try:
            is_target = True
            targets = self.db.session.query(
                UserModel
            ).filter(
                UserModel.is_target == is_target
            ).filter(
                UserModel.assignee == assignee_id
            ).all()
            return user_to_dict(targets)
        except Exception as e:
            self.logger.info("No target: %s" % e)
            pass
        pass

    # end user operations
    # begin statistics operations

    def create_or_load_stats(self, bot_id, comment):
        # Load if there's one to update for current day
        try:
            stats = self.db.session.query(
                StatModel
            ).filter(
                StatModel.bot_id == bot_id
            ).filter(
                StatModel.created_on == date.today()
            ).one()
            return stats_to_dict(stats)
        except Exception as e:
            self.logger.info('Exception in Database.create_or_load_stats():', e)
            pass

        # Or create a new one
        try:
            stats = StatModel(
                bot_id = bot_id,
                last_comment = comment
            )
            self.db.session.add(stats)
            self.db.session.commit()
            return stats_to_dict(stats)
        except Exception as e:
            self.logger.info('Exception in Database.create_or_load_stats():', e)
        pass

    pass

    def update_stats(self,
                     bot_id,
                     parsed_count,
                     ignored_count,
                     follow_request_count,
                     comment_count,
                     last_comment,
                     skiplist,
                     followlist):
        stats: StatModel
        current_date = date.today()
        try:
            stats = self.db.session.query(
                StatModel
            ).filter(
                StatModel.created_on == current_date
            ).filter(
                StatModel.bot_id == bot_id
            ).one()
        except Exception as e:
            self.logger.info('Error in update_stats():', e)
            stats = StatModel(bot_id = bot_id, created_on = current_date)
            pass
        stats.parsed_count = parsed_count
        stats.ignored_count = ignored_count
        stats.follow_request_count = follow_request_count
        stats.comment_count = comment_count
        stats.last_comment = last_comment
        if len(stats.skiplist) > 0:
            stats.skiplist += ',' + ','.join([str(skiped) for skiped in skiplist if str(skiped) not in stats.skiplist])
        else:
            stats.skiplist = ','.join([str(skiped) for skiped in skiplist if str(skiped) not in stats.skiplist])
        if len(stats.followlist) > 0:
            stats.followlist += ',' + ','.join([str(follow) for follow in followlist if str(follow) not in stats.followlist])
        else:
            stats.followlist = ','.join([str(follow) for follow in followlist if str(follow) not in stats.followlist])
        self.db.session.commit()
        return True

    def load_stat(self, bot_id) -> dict or None:
        current_date = date.today()
        try:
            stats = self.db.session.query(
                StatModel
            ).filter(
                StatModel.bot_id == bot_id
            ).filter(
                StatModel.created_on == current_date
            ).one()
            self.logger.info('DatabaseManager.load_stat():', stats)
            return stats_to_dict(stats)
        except Exception as e:
            self.logger.info('Error in DatabaseManager.load_stat():', e)
            return None
        pass

    def load_stats(self, bot_id) -> list or None:
        try:
            stats = self.db.session.query(
                StatModel
            ).filter(
                StatModel.bot_id == bot_id
            ).all()
            self.logger.info('DatabaseManager.load_stats():', stats)
            return [stats_to_dict(stat) for stat in stats]
        except Exception as e:
            self.logger.info('Error in DatabaseManager.load_stats_all():', e)
            return None
        pass

    # begin statistics operations

    pass

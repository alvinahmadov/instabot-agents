import settings
from app.utils import spreadsheet
from app.database import models


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS


# Initialisers begin
def initialise_bot_from_config(config: dict, db):
    from instabot import Bot
    return Bot(proxy = config.get('proxy', None),
               max_likes_per_day = config['max_likes_per_day'],
               max_unlikes_per_day = config['max_unlikes_per_day'],
               max_follows_per_day = config['max_follows_per_day'],
               max_unfollows_per_day = config['max_unfollows_per_day'],
               max_comments_per_day = config['max_comments_per_day'],
               max_likes_to_like = config['max_likes_to_like'],
               filter_users = config['filter_users'],
               filter_users_without_profile_photo = config['filter_users_without_profile_photo'],
               filter_business_accounts = config['filter_business_accounts'],
               filter_verified_accounts = config['filter_verified_accounts'],
               max_followers_to_follow = config['max_followers_to_follow'],
               min_followers_to_follow = config['min_followers_to_follow'],
               max_following_to_follow = config['max_following_to_follow'],
               min_following_to_follow = config['min_following_to_follow'],
               max_followers_to_following_ratio = config['max_followers_to_following_ratio'],
               max_following_to_followers_ratio = config['max_following_to_followers_ratio'],
               min_media_count_to_follow = config['min_media_count_to_follow'],
               max_following_to_block = config['max_following_to_block'],
               like_delay = config['like_delay'],
               unlike_delay = config['unlike_delay'],
               follow_delay = config['follow_delay'],
               unfollow_delay = config['unfollow_delay'],
               comment_delay = config['comment_delay'],
               stop_words = tuple(),
               blacklist_hashtags = list(),
               verbosity = False,
               device = "samsung_galaxy_s7",
               save_logfile = False,
               loglevel_file = 0,
               loglevel_stream = 20,
               log_follow_unfollow = False,
               db = db)
    pass


def initialise_bot_from_file(file, botman):
    try:
        file_copy = file
        csvman = spreadsheet.Manager()
        params = csvman.read(file_copy)
        columns = settings.COLNAMES
        size = len(params[settings.COLNAMES[0]])
        botman.database.truncate('users')
        for i in range(size):
            kwargs = {
                "username": params[columns[0]][i],
                "targets": params[columns[1]][i],
                "fullname": params[columns[2]][i],
                "email": params[columns[3]][i],
                "password": params[columns[4]][i],
                "biography": params[columns[5]][i],
                "external_url": params[columns[6]][i],
                "gender": params[columns[7]][i],
                "private": params[columns[8]][i],
                "proxy": params[columns[9]][i]
            }
            data = botman.load_bot(kwargs['username'])
            if data is None:
                # Bot data is not in database, then create a new one
                botman.create_bot(**kwargs)
                # botman.workers[bot_id].login()
                print('Bot %s created and added to database' % kwargs['username'])
                pass
            else:
                # data is in database, so check that data in database is updated
                logged_in, bot = check_account(botman.database, botman.config, **data)
                if logged_in:
                    botman.update_bot(bot, **kwargs)
                    print('Bot %s loaded from database' % kwargs['username'])
            pass
        print("Exiting utils.initialise_bot_from_file() with success")
        return params
    except ValueError as ve:
        print("Exiting utils.initialise_bot_from_file() with fail:", ve)
        pass
    pass


def check_account(db, config, **kwargs):
    """
    Check details of account to verify
    """
    try:
        from instabot.bot import Bot
        bot = initialise_bot_from_config(config, db)
        username = kwargs.get('username')
        password = kwargs.get('password')
        proxy = kwargs.get('proxy', None)
        logged_in = bot.login(username = username,
                              password = password,
                              proxy = proxy,
                              use_cookie = True,
                              use_uuid = True,
                              cookie_fname = None,
                              ask_for_code = True,
                              set_device = True,
                              generate_all_uuids = True,
                              is_threaded = True)
        return logged_in, bot
    except Exception as e:
        print('check_account:', e)
        pass
    return False, None
    pass


# Database utils
def get_not_none(data, default):
    return data if data is not None else default


def check_data_changed(data, model: models.Bots):
    return data["external_url"] == model.external_url \
           and data["full_name"] == model.fullname \
           and data["biography"] == model.biography \
           and data["gender"] == model.gender
    pass


def collect_stats(stats_list: list):
    result = {
        "parsed_count": 0,
        "ignored_count": 0,
        "follow_request_count": 0,
        "comment_count": 0,
        "last_comment": ""
    }
    for stats_dict in stats_list:
        result["parsed_count"] = stats_dict["parsed_count"]
        pass
    pass


# Converters
def bot_to_dict(model: models.Bots):
    return {
        "id": model.id,
        "username": model.username,
        "fullname": model.fullname,
        "email": model.email,
        "password": model.password,
        "proxy": model.proxy,
        "external_url": model.external_url,
        "profile_pic_url": model.profile_pic_url,
        "biography": model.biography,
        "gender": model.gender,
        "private": model.private
    }


def stats_to_dict(model: models.Stats):
    skiplist = set()
    followlist = set()
    if model.skiplist is not None:
        skiplist = set(model.skiplist) if ',' not in model.skiplist else model.skiplist.split(',')
    if model.followlist is not None:
        followlist = set(model.followlist) if ',' not in model.followlist else model.followlist.split(',')
    return {
        "id": model.id,
        "bot_id": model.bot_id,
        "parsed_count": model.parsed_count,
        "ignored_count": model.ignored_count,
        "follow_request_count": model.follow_request_count,
        "comment_count": model.comment_count,
        "last_comment": model.last_comment,
        "skiplist": skiplist,
        "followlist": followlist,
        "created_on": model.created_on
    }


def user_to_dict(user: models.Users):
    return {
        "id": user.id,
        "assignee": user.assignee,
        "username": user.username,
        "fullname": user.fullname,
        "external_url": user.external_url,
        "profile_pic_url": user.profile_pic_url,
        "biography": user.biography,
        "private": user.is_private,
        "is_target": user.is_target,
        "num_media": user.num_media,
        "num_followers": user.num_followers,
        "num_following": user.num_following
    }


def config_to_dict(model: models.Settings):
    return {
        "max_likes_per_day": model.max_likes_per_day,
        "max_unlikes_per_day": model.max_unlikes_per_day,
        "max_follows_per_day": model.max_follows_per_day,
        "max_unfollows_per_day": model.max_unfollows_per_day,
        "max_comments_per_day": model.max_comments_per_day,
        "max_likes_to_like": model.max_likes_to_like,
        "filter_users": model.filter_users,
        "filter_business_accounts": model.filter_business_accounts,
        "filter_verified_accounts": model.filter_verified_accounts,
        "filter_users_with_external_url": model.filter_users_with_external_url,
        "filter_users_without_profile_photo": model.filter_users_without_profile_photo,
        "max_followers_to_follow": model.max_followers_to_follow,
        "min_followers_to_follow": model.min_followers_to_follow,
        "max_following_to_follow": model.max_following_to_follow,
        "min_following_to_follow": model.min_following_to_follow,
        "max_followers_to_following_ratio": model.max_followers_to_following_ratio,
        "max_following_to_followers_ratio": model.max_following_to_followers_ratio,
        "min_media_count_to_follow": model.min_media_count_to_follow,
        "max_following_to_block": model.max_following_to_block,
        "like_delay": model.like_delay,
        "unlike_delay": model.unlike_delay,
        "follow_delay": model.follow_delay,
        "unfollow_delay": model.unfollow_delay,
        "comment_delay": model.comment_delay
    }
    pass


def get_attr(key, tp = bool, **kwargs):
    if tp is bool:
        value = False
    else:
        value = 0
    return kwargs.pop(key) if not None else value


def get_attr_int(key, **kwargs):
    return kwargs.pop(key) if kwargs.get(key) is not None else 0


def get_attr_bool(key, **kwargs):
    return kwargs.pop(key) if kwargs.get(key) is not None else False


def get_attr_str(key, **kwargs):
    return kwargs.pop(key) if kwargs.get(key) is not None else ''


# Bot related utils


def gender_from_string(gender_str) -> int:
    if isinstance(gender_str, str):
        if gender_str == 'male':
            return 1
        elif gender_str == 'female':
            return 2
        else:
            return 3
    else:
        if isinstance(gender_str, int):
            return 3
        return gender_str
    pass

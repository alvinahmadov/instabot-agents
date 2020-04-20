from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    make_response
)

# from flask_socketio import SocketIO, emit

import settings
from app.utils import functions
from app.database import manager, db, reset_database, models
from app.bot.manager import Manager
from app.utils import spreadsheet, threads

flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# flask_app.logger.disabled = True
# flask_app.debug = True
# log = logging.getLogger('werkzeug')
# log.disabled = True\

manager = Manager(manager.Database(db))
# socketio = SocketIO(flask_app)


def check_loaded_bots():
    if manager.loaded:
        print('Loaded')
        worker_name = set([key for key in manager.workers.keys()])
        # socketio.emit('loaded', {"data": worker_name})
    pass


@flask_app.before_first_request
def init_db():
    db.init_app(flask_app)
    db.create_all()
    if db.session.query(models.Settings).count() == 0:
        config_model = models.Settings()
        db.session.add(config_model)
        db.session.commit()
        pass
    it = threads.Loader(flask_app, manager)
    it.start()
    it.join(1.0)
    # socketio.start_background_task(target = check_loaded_bots)
    pass


@flask_app.route("/")
def index():
    manager.get_stats()
    return render_template('index.html.jinja2',
                           bot_manager = manager)


@flask_app.route("/login")
def login():
    return render_template("login.html.jinja2")


@flask_app.route("/download_bots")
def download_bots():
    bots = manager.get_bots()
    if bots is None:
        redirect('/multibot')
    csv_man = spreadsheet.Manager()
    file = csv_man.write(bots, fn = manager.database.load_users, args = (True,))
    response = make_response(file)
    response.headers['Content-Type'] = settings.ALLOWED_MIMETYPES['xlsx']
    response.headers['Content-Disposition'] = "inline; filename=bots.xlsx"
    return response


@flask_app.route("/download_stats/<bot_name>")
def download_statistic(bot_name):
    stat = manager.database.load_stat(bot_name)
    if stat is None or len(stat) < 0:
        redirect('/statistics')
        pass

    csv_man = spreadsheet.Manager()
    file = csv_man.write(stat, fn = manager.database.load_stat,
                         args = (bot_name,))
    response = make_response(file)
    response.headers['Content-Type'] = settings.ALLOWED_MIMETYPES['xlsx']
    response.headers['Content-Disposition'] = "inline; filename={filename}_stats.xlsx".format(filename=bot_name)
    return response


@flask_app.route('/multibot', methods = ['GET', 'POST'])
def multibot():
    config = manager.config
    return render_template('multibot.html.jinja2',
                           bot_manager = manager,
                           config = config)


@flask_app.route('/configure_filters', methods = ['POST'])
def set_filters():
    def ontob(v):
        return True if v == 'on' else False

    config = {
        'filter_users_without_profile_photo': ontob(request.form.get('filter_users_without_profile_photo')),
        'filter_business_accounts': ontob(request.form.get('filter_business_accounts')),
        'filter_users_with_external_url': ontob(request.form.get('filter_users_with_external_url')),
        'max_followers_to_follow': int(request.form.get('max_followers_to_follow')),
        'min_followers_to_follow': int(request.form.get('min_followers_to_follow')),
        'max_following_to_follow': int(request.form.get('max_following_to_follow')),
        'min_following_to_follow': int(request.form.get('min_following_to_follow'))
    }
    manager.database.save_config(config)
    manager.filters.update(**config)
    return redirect('/multibot')


@flask_app.route('/configure_limits', methods = ['POST'])
def set_limits():
    manager.database.save_config({
        'max_likes_per_day': int(request.form.get('max_likes_per_day')),
        'max_follows_per_day': int(request.form.get('max_follows_per_day')),
        'max_comments_per_day': int(request.form.get('max_comments_per_day')),
        'like_delay': int(request.form.get('like_delay')),
        'follow_delay': int(request.form.get('follow_delay')),
        'comment_delay': int(request.form.get('comment_delay')),
    })
    return redirect('/multibot')


@flask_app.route('/start_action_followers', methods = ['GET', 'POST'])
def start_action_followers():
    if request.method == 'POST':
        manager.comment = str(request.form.get('comment', ''))
        num_followers = int(request.form.get('num_followers'))
        priority = int(request.form.get('pubpriv', 3))
        wt = threads.Worker(flask_app, manager, num_followers, priority)
        wt.start()
        wt.join(2.0)
    return redirect('/')


@flask_app.route('/start_follow_users', methods = ['POST'])
def start_follow_users():
    usernames: str = request.form.get('follow_users')
    follow = True if request.form.get('followButton') is not None else False

    def follow_or_unfollow(workers_: dict, user_: str, follow_: bool):
        for worker_ in workers_.values():
            if follow_:
                worker_.request_to_follow(user_)
            else:
                worker_.request_to_unfollow(user_)
        pass

    if ',' in usernames:
        for user in usernames.split(','):
            follow_or_unfollow(manager.workers, user, follow)
            pass
        pass
    else:
        follow_or_unfollow(manager.workers, usernames, follow)
        pass

    return redirect('/')


@flask_app.route('/reset')
def reset_db():
    reset_database()
    return redirect('/')


@flask_app.route('/upload_bots', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file and functions.allowed_file(file.filename):
            t = threads.Initer(flask_app, file, manager)
            t.start()
            t.join(1)
    return redirect('/')


@flask_app.route('/about')
def about():
    return render_template('about.html.jinja2')


@flask_app.route('/show_targets')
def show_targets():
    return render_template('show_targets.html.jinja2',
                           bot_manager = manager)


@flask_app.route('/show_followers')
def show_followers():
    manager.get_stats()
    return render_template('show_followers.html.jinja2',
                           bot_manager = manager)


@flask_app.route('/statistics')
def statistics():
    return render_template('statistics.html.jinja2',
                           bot_manager = manager)


if __name__ == "__main__":
    # socketio.run(flask_app, host = '127.0.0.1', port = 5000, debug = True)
    flask_app.run(host = '127.0.0.1', port = 5000)

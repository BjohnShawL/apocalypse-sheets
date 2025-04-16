from http.client import HTTPResponse

from devtools import debug
from flask import render_template, Blueprint, redirect, url_for, flash, session, request, current_app
from passlib.hash import sha256_crypt

from .character_form import CharacterForm
from .user_form import RegistrationForm, LoginForm
from .util import login_required, generate_page_urls
from ..models import Character, CharacterItem, Stat, Playbook
from ..extensions import db
from ..models.user import User, UserItem


main = Blueprint('main', __name__)


def get_current_score(form: CharacterForm, attr: str, max_score: int):
    current_score = max_score
    attr_fields = [form._fields[field].data for field in form._fields.keys() if field.startswith(attr)]
    for field in attr_fields:
        if field:
            current_score -= 1
    return current_score


@main.route('/')
@login_required
def index():
    pass


@main.route('/<string:userid>/characters/new', methods=['GET', 'POST'])
@login_required
def new_character(userid: str):
    character_form = CharacterForm()
    p = generate_page_urls("a")
    if character_form.validate_on_submit():
        character = Character(
            name=character_form.name.data,
            playbook_id=character_form.playbook_id.data.id,
            user_id=userid,
        )
        db.session.add(character)
        charm = Stat("Charm", character_form.stats.form.charm_field.data, character.id)
        cool = Stat("Cool", character_form.stats.form.cool_field.data, character.id)
        sharp = Stat("Sharp", character_form.stats.form.sharp_field.data, character.id)
        tough = Stat("Tough", character_form.stats.form.tough_field.data, character.id)
        weird = Stat("Weird", character_form.stats.form.weird_field.data, character.id)

        luck = 0
        debug(character_form.luck.form.__dict__)
        # for box in character_form.luck.form._fields:
        #     debug(box)

        db.session.add(cool)
        db.session.add(sharp)
        db.session.add(tough)
        db.session.add(weird)
        db.session.add(charm)
        db.session.flush()
        db.session.commit()

    return render_template('pages/character_form.html.j2',
                           page_title="New Character",
                           form=character_form,
                           pages=p,
                           selected="New Character",
                           )


@main.route('/<string:userid>/characters/<string:characterid>/edit', methods=['GET', 'POST'])
@login_required
def edit_character(userid: str, characterid: int):
    character_query = db.select(Character).where(Character.id == characterid, Character.user_id == userid)
    character = db.session.execute(character_query).scalar()
    form = CharacterForm()
    form.set_data(character)
    # if form.validate_on_submit():
    #     character.name = form.name.data
    #     # character.stats
    p = generate_page_urls("a")
    if form.validate_on_submit():
        pass
    return render_template('pages/character_form.html.j2', page_title=f"Edit {character.name}", form=form, pages=p,
                           selected="Character List")

@main.route('/playbooks', methods=['GET'])
def playbook():
    playbook_id = request.args.get('playbook_id')
    playbook_query = db.select(Playbook).where(Playbook.id == playbook_id)
    selected_playbook = db.session.execute(playbook_query).scalar()
    return f"{selected_playbook.description}" , 200


@main.route('/<string:userid>/characters/list', methods=['GET'])
@login_required
def character_list(userid: str):
    page_title = "Character List"
    query = db.select(Character).where(Character.user_id == userid)
    characters = db.session.execute(query).scalars()
    c_list = []
    for c in characters:
        character_item = CharacterItem.from_alchemy(c)
        c_list.append(character_item)
    p = generate_page_urls("")
    return render_template(
        'pages/character_list.html.j2',
        characters=c_list,
        page_title=page_title,
        pages=p,
        selected="Character List"

    )


@main.route('/login', methods=['GET', 'POST'])
def login():
    page_title = "Login"
    try:
        form = LoginForm()
        p = generate_page_urls("login")
        if form.validate_on_submit():
            user = db.session.query(User).filter(User.email == form.email.data).scalar()
            if user and sha256_crypt.verify(form.password.data, user.password):
                session['current_user'] = UserItem.from_alchemy(user)
                session['logged_in'] = True
                flash(f"Hi {user.username}! You are now logged in!.")
                return redirect(url_for('main.new_character', userid=user.id))

        return render_template('login.html.j2', form=form, pages=p, page_title=page_title, selected="Log In")

    except Exception as e:
        return str(e)


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session['current_user'] = None
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    page_title = "Register"
    try:
        form = RegistrationForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data

            password = sha256_crypt.encrypt(form.password.data)
            existing_username = db.session.query(User).filter_by(username=username).scalar()
            if existing_username:
                flash("That username is already taken, please choose another")
                return render_template('register.html.j2', form=form)

            db.session.add(User(username=username, email=email, password=password))
            db.session.commit()
            return redirect(url_for('main.login'))

        return render_template('register.html.j2', form=form, page_title=page_title, selected="Register",
                               pages=generate_page_urls(""))
    except Exception as error:
        return str(error)

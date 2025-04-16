from devtools import debug
from flask import render_template, redirect, url_for, Blueprint

from application.models import Playbook, PlaybookItem, Move
from application.models import db
from application.views import PlaybookForm, MoveForm
from application.views.util import login_required, generate_page_urls

playbooks = Blueprint('playbooks', __name__, url_prefix='/playbooks')


@playbooks.route('/<string:userid>/new', methods=['GET', 'POST'])
@login_required
def new_playbook(userid: str):
    form = PlaybookForm()
    page_title = 'New Playbook'
    if form.validate_on_submit():
        playbook_name = form.name.data
        playbook_description = form.description.data
        playbook = Playbook(name=playbook_name, description=playbook_description)
        playbook.owning_user_id = userid
        db.session.add(playbook)
        db.session.commit()
        return redirect(url_for('playbooks.playbook_list', userid=userid))

    return render_template('pages/playbook_form.html.j2',
                           page_title=page_title, form=form, pages=generate_page_urls("New Playbook"),
                           selected=page_title)


@playbooks.route('/<string:userid>/list/<string:playbookid>/edit', methods=['GET', 'POST'])
@login_required
def edit_character(userid: str, playbookid: int):
    playbook_query = db.select(Playbook).where(Playbook.id == playbookid, Playbook.owning_user_id == userid)
    playbook = db.session.execute(playbook_query).scalar()
    form = PlaybookForm()
    form.set_data(playbook)
    # if form.validate_on_submit():
    #     character.name = form.name.data
    #     # character.stats
    p = generate_page_urls("a")
    if form.validate_on_submit():
        pass
    return render_template('pages/playbook_form.html.j2', page_title=f"Edit {playbook.name}", form=form, pages=p,
                           selected="Playbook List")


@playbooks.route('/<string:userid>/list', methods=['GET'])
def playbook_list(userid: str):
    page_title = "Playbook List"
    playbook_query: object = db.select(Playbook).where(Playbook.owning_user_id == userid)
    playbooks_result = db.session.execute(playbook_query).scalars()
    p_list = []
    for p in playbooks_result:
        playbook_item = PlaybookItem.from_alchemy(p)
        p_list.append(playbook_item)
    p = generate_page_urls("")
    return render_template(
        'pages/playbook_list.html.j2',
        playbooks=p_list,
        page_title=page_title,
        pages=p,
        selected="Playbook List"

    )


@playbooks.route('/<string:userid>/list/<string:playbookid>/delete', methods=['POST'])
def delete_playbook(userid: str, playbookid: int):
    playbook_query = db.select(Playbook).where(Playbook.id == playbookid, Playbook.owning_user_id == userid)
    playbook = db.session.execute(playbook_query).scalar()
    db.session.delete(playbook)
    db.session.commit()
    return redirect(url_for('playbooks.playbook_list', userid=userid))


@playbooks.route('/<string:userid>/moves/add', methods=['GET', 'POST'])
@login_required
def new_move(userid: str):
    form = MoveForm()
    p = generate_page_urls("a")
    if form.validate_on_submit():
        playbook_id_data = form.playbook_id.data
        debug(playbook_id_data)
        move = Move(name=form.name.data, description=form.details.data, playbook_id=playbook_id_data.id,
                    owning_user_id=userid)
        db.session.add(move)
        db.session.commit()
        return redirect(url_for('playbooks.playbook_list', userid=userid))

    return render_template('pages/move_form.html.j2',form=form, pages=p,selected="New Move")
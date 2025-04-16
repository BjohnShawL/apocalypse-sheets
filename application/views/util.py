from functools import wraps
from typing import Any

from devtools import debug
from flask import session, request, redirect, url_for

from application.models import MenuItem


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('current_user') is None:
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def generate_page_urls(selection: str) -> list[MenuItem]:
    user = session.get('current_user')
    if not user or not user.get('user_id'):
        return [
            MenuItem("Log In",False, url_for('main.login')),
            MenuItem("Register",False, url_for('main.register')),
        ]
    character_page_urls: list[MenuItem] = [
        MenuItem("New Character", False,
                 url_for('main.new_character',
                         userid=user.get('user_id')
                         )
                 ),
        MenuItem("Character List", False,
                 url_for('main.character_list', userid=user.get('user_id')
                         )
                 )
    ]

    playbook_page_urls = [
        MenuItem("New Playbook", False,
                 url_for('playbooks.new_playbook',userid=user.get('user_id')
                         )
                 ),
        MenuItem("Playbook List", False,
                 url_for('playbooks.playbook_list', userid=user.get('user_id')
                         )
                 ),
        MenuItem("New Move", False,url_for('playbooks.new_move',userid=user.get('user_id')))
    ]
    item_page_urls = []
    page_urls = [
        MenuItem("Characters",True,'#',character_page_urls,subitem_names=[item.name for item in character_page_urls]),
        MenuItem("Playbooks", True,'#',playbook_page_urls,subitem_names=[item.name for item in playbook_page_urls]),
        MenuItem("Items",True,'#',item_page_urls, subitem_names=[item.name for item in item_page_urls]),
    ]

    # page_urls = [
    #     {"name":"Characters", "category_item":True, 'url':'#', "items":[] }
    #     {"name": "New Character", "url": url_for('main.new_character', userid=user['user_id'])},
    #     {"name": "Character List", "url": url_for('main.character_list', userid=user['user_id'])},
    #     {"name":"New Playbook", "url": url_for('playbooks.new_playbook', userid=user['user_id'])},
    #     {"name": "Log Out", "url": url_for('main.logout')},
    # ]
    return page_urls
from devtools import debug

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.fields.form import FormField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField

from application.extensions import db
from application.models import Playbook, Character



class StatForm(FlaskForm):
    charm_field = IntegerField("Charm", validators=[DataRequired()],render_kw={'class':'circ-input'})
    cool_field = IntegerField("Cool", validators=[DataRequired()],render_kw={'class':'circ-input'})
    sharp_field = IntegerField("Sharp", validators=[DataRequired()],render_kw={'class':'circ-input'})
    tough_field = IntegerField("Tough", validators=[DataRequired()],render_kw={'class':'circ-input'})
    weird_field = IntegerField("Weird", validators=[DataRequired()],render_kw={'class':'circ-input'})


class HarmForm(FlaskForm):
    harm_1 = BooleanField("")
    harm_2 = BooleanField("")
    harm_3 = BooleanField("")
    harm_4 = BooleanField("")
    harm_5 = BooleanField("")
    harm_6 = BooleanField("")
    harm_7 = BooleanField("Dying")
    unstable_field = BooleanField("Unstable")


class LuckForm(FlaskForm):
    luck_1 = BooleanField("")
    luck_2 = BooleanField("")
    luck_3 = BooleanField("")
    luck_4 = BooleanField("")
    luck_5 = BooleanField("")
    luck_6 = BooleanField("")
    luck_7 = BooleanField("Doomed")



class ExpForm(FlaskForm):
    exp = BooleanField("")



class CharacterForm(FlaskForm):
    # identity
    name = StringField("Name", description="Enter a character name.", validators=[DataRequired()])
    look= TextAreaField("Look", description="Enter a brief description of the character's physical appearance.",render_kw={'cols':50})
    hx_dict= {"hx-get":'/playbooks',"hx-trigger":"change","hx-target":"#playbook-desc"}
    playbook_id = QuerySelectField("Playbook", blank_text="Select your character's playbook.", query_factory=lambda: db.session.execute(
        db.select(Playbook).order_by(Playbook.name)
    ).scalars(), get_label="name", allow_blank=True, render_kw=hx_dict)

    # stats
    stats = FormField(StatForm)
    luck = FormField(LuckForm)
    harm = FormField(HarmForm)
    exp = FormField(ExpForm)

    submit = SubmitField()

    @staticmethod
    def validate_playbook_field(_form, field):
        if field.data is None:
            raise ValidationError("Please select a playbook")

    char_validate = {"playbook_field": validate_playbook_field}

    def validate_on_submit(self, extra_validators=None):
        return super().validate_on_submit(extra_validators=self.char_validate)

    @staticmethod
    def generate_form_data(character: Character) -> dict:

        form_data = {"name": character.name,
                     "charm_field": character.stats_dict.get("charm",0),
                     "cool_field": character.stats_dict.get("cool",0),
                     "sharp_field": character.stats_dict.get("sharp",0),
                     "tough_field": character.stats_dict.get("tough",0),
                     "weird_field": character.stats_dict.get("charm",0),
                     }
        return form_data

    def set_data(self, character: Character):
        form_data = self.generate_form_data(character)

        self.name.data = form_data["name"]
        self.playbook_id.data = character.playbook
        self.stats.form.charm_field.data = form_data["charm_field"]
        self.stats.form.cool_field.data = form_data["cool_field"]
        self.stats.form.sharp_field.data = form_data["sharp_field"]
        self.stats.form.tough_field.data = form_data["tough_field"]
        self.stats.form.weird_field.data = form_data["weird_field"]

class PlaybookForm(FlaskForm):
    name = StringField("Name", description="Enter the Playbook Name", validators=[DataRequired()])
    description = TextAreaField("Description", description= "Enter the Playbook Description",validators=[DataRequired()],render_kw={'cols':50})
    submit = SubmitField()

    def set_data(self, playbook: Playbook):
        form_data = {"name": playbook.name, "description": playbook.description,}
        self.name.data = form_data["name"]
        self.description.data = form_data["description"]

class MoveForm(FlaskForm):
    name = StringField("Name", description="Enter the name of the move.", validators=[DataRequired()])
    details = TextAreaField("Details", description= "Enter the details for the move.", validators=[DataRequired()],render_kw={'cols':50})
    playbook_id = QuerySelectField("Playbook", blank_text="Select the playbook this move is for.", query_factory=lambda: db.session.execute(
        db.select(Playbook).order_by(Playbook.name)
    ).scalars(), get_label="name", allow_blank=True)
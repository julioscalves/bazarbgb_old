from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired


STATES = [
        ('AC'), ('AL'), ('AP'), ('AM'), ('BA'),
        ('CE'), ('ES'), ('GO'), ('MA'), ('MT'),
        ('MS'), ('MG'), ('PA'), ('PB'), ('PR'),
        ('PI'), ('RJ'), ('RN'), ('RS'), ('RO'),
        ('RR'), ('SC'), ('SP'), ('SE'), ('TO'),
        ('DF'),
    ]

OFFER = [
    ('Troca', 'Troca'), ('Venda', 'Venda'), ('Procura', 'Procura')
]


class LinkForm(FlaskForm):
    offer  = SelectField('Tipo', choices=OFFER)
    links  = TextAreaField('Links', validators=[InputRequired()])
    city   = StringField('Cidade', validators=[InputRequired()])
    state  = SelectField('Estado', choices=STATES)
    submit = SubmitField('Enviar')
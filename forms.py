from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired


STATES = [
        ('AC'), ('AL'), ('AP'), ('AM'), ('BA'),
        ('CE'), ('DF'), ('ES'), ('GO'), ('MA'), 
        ('MT'), ('MS'), ('MG'), ('PA'), ('PB'), 
        ('PR'), ('PI'), ('RJ'), ('RN'), ('RS'), 
        ('RO'), ('RR'), ('SC'), ('SP'), ('SE'), 
        ('TO'),
    ]

OFFER = [
    ('Venda', 'Venda'), ('Troca', 'Troca'), ('Procura', 'Procura')
]


class LinkForm(FlaskForm):
    offer   = SelectField('Tipo', choices=OFFER)
    city    = StringField('Cidade', validators=[InputRequired()])
    state   = SelectField('Estado', choices=STATES)
    links   = TextAreaField('Links', validators=[InputRequired()])
    details = TextAreaField('Detalhes')
    submit  = SubmitField('Enviar')

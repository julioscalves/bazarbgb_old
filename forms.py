from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length


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
    # pay attention to FieldList
    offer   = SelectField('Tipo', choices=OFFER)
    city    = StringField('Cidade', validators=[InputRequired()])
    state   = SelectField('Estado', choices=STATES)
    links   = StringField('Link', validators=[InputRequired()])
    details = StringField('Detalhes', validators=[Length(max=50)])
    prices  = StringField('Preço', validators=[Length(max=10)])
    submit  = SubmitField('Enviar')

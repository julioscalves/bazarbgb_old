from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, TextAreaField, StringField, SelectField, SubmitField
from wtforms.validators import InputRequired, Length


STATES = [
        ('AC'), ('AL'), ('AP'), ('AM'), ('BA'),
        ('CE'), ('DF'), ('ES'), ('GO'), ('MA'), 
        ('MT'), ('MS'), ('MG'), ('PA'), ('PB'), 
        ('PR'), ('PI'), ('RJ'), ('RN'), ('RS'), 
        ('RO'), ('RR'), ('SC'), ('SP'), ('SE'), 
        ('TO'), ('PE'),
    ]

OFFER = [
    ('Apenas Venda'), ('Apenas Troca'), ('Venda ou Troca'), ('Leilão'), ('Procura')
]

class BoardGameForm(FlaskForm):
    offer       = SelectField('Tipo', choices=OFFER)
    boardgame   = StringField('Nome', validators=[InputRequired()])
    details     = StringField('Detalhes sobre o item', validators=[Length(max=80)])
    price       = StringField('Preço', validators=[Length(max=8)])
    submit      = SubmitField('Enviar')

class MainForm(FlaskForm):
    boardgames      = FieldList(FormField(BoardGameForm), min_entries=1, max_entries=50)
    city            = StringField('Cidade', validators=[InputRequired()])
    state           = SelectField('Estado', choices=STATES)
    general_details = TextAreaField('Detalhes sobre o anúncio', render_kw={"rows": 4, "cols": 4}, validators=[Length(max=600)])

import os
import re
from flask.globals import request
from flask_sqlalchemy import SQLAlchemy
from forms import BoardGameForm, MainForm
from flask import Flask, render_template, jsonify


app = Flask(__name__)

try:
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
except KeyError:
    app.config['SECRET_KEY'] = "KyYourv5FvgMikpw0yHYhJXvJtUM4YxcsRjoicvv"

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///names.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
db.init_app(app)

class Names(db.Model):
    __tablename__ = "boardgames"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String)


def unpack_exceptions(content):
    # unpacks the exceptions listed in the 'exceptions.txt'
    # and returns them in a dictionary

    tag_exceptions = {}
    content = [line for line in content if len(line) > 1]

    for line in content:
        split = line.strip().split('|')
        tag_exceptions[split[0]] = split[1]

    return tag_exceptions


def get_tag_exceptions():
    # opens the file where the exceptions are stored, 
    # calls the unpack functions and returns the tags
    # into a dictionary    

    filename = 'exceptions.txt'

    with open(filename, encoding='utf8') as tags:
        content = tags.readlines()
        tag_exceptions = unpack_exceptions(content)

    return tag_exceptions


def remove_parenthesis(string):
    # cleans parenthesis from a string

    pattern = re.compile('[\(\[].*?[\)\]]')
    cleaned_string = re.sub(pattern, '', string)

    return cleaned_string


def remove_non_number(string):
    # cleans non number characters from a 
    # string

    pattern = re.compile('[^0-9,.]')
    cleaned_string = re.sub(pattern, '', string)

    return cleaned_string


def format_name(name):
    # remove and replace any special characters 
    # from a string

    name = remove_parenthesis(name)
    name = name.replace('?', '')
    name = name.replace('"', '')
    name = name.replace("'", '')
    name = name.replace('!', '')
    name = name.replace(',', '')
    name = name.replace(' ', '')
    name = name.replace('&', 'N')
    name = name.replace('–', ' #')
    name = name.replace(':', ' #')  
    name = name.replace('-', '')   
    name = name.replace('/', ' #')   
    name = name.replace('\\', ' #')   
    name = name.replace('.', '') 
    name = name.replace('?', '') 
    name = name.replace('¿', '') 
    
    name = f'#{name}'   

    return name
    

def assemble_message(adtype, text_list, output):
    # groups and assemble each message into 
    # the output

    if len(text_list) > 0:        
        if adtype == 'Venda':
            output += "VENDO\n\n"
        
        elif adtype == 'Troca':
            output += "#TROCO\n\n"

        else:
            output += "#PROCURO\n\n"
        
        for ad in text_list:
            output += f'{ad}\n\n'

    return output


def handle_data(data, int_keys):
    # this is the main function, which is
    # responsible for handling the data and
    # calls the helper functions to get the
    # boardgames' names, assemble the messages
    # and returns them into a string

    sell = []
    trade = []
    search = []

    for index in int_keys:
        boardgame = data[index].get('boardgame')
        formatted_name = format_name(boardgame)

        data[index]['name'] = formatted_name
        formatted_name = data[index]['name']
        offer = data[index]['offer']
        details = data[index]['details']

        if formatted_name in tag_exceptions.keys():
            formatted_name = tag_exceptions[formatted_name]

        if offer == 'Venda':
            price = remove_non_number(data[index]["price"])
            message = f'\t\t{formatted_name} por R$ {price}\n\t\t{details}'.rstrip()
            sell.append(message)

        elif offer == 'Troca':
            message = f'\t\t{formatted_name}\n\t\t{details}'.rstrip()
            trade.append(message)

        else:
            message = f'\t\t{formatted_name}\n\t\t{details}'.rstrip()
            search.append(message)

    output = ''

    for adtype, text_list in zip(['Venda', 'Troca', 'Procura'], [sell, trade, search]):
        output = assemble_message(adtype, text_list, output)

    city = data["city"].title().replace("-", "").replace(" ", "")
    state = data["state"]

    output += f'#{city} #{state}'

    return output


def repack(form_data):
    # repacks the request form into a dictionary

    data = {}
    data['city'] = form_data.city.data
    data['state'] = form_data.state.data

    index = 1

    for games in form_data.boardgames.data:            
        data[index] = {
            'boardgame' : games['boardgame'],
            'offer'     : games['offer'],
            'name'      : '',
            'price'     : games['price'],
            'details'   : games['details'],
        }
        index += 1

    int_keys = list(filter(lambda i: type(i) == int, data.keys()))

    return data, int_keys


@app.route('/bgsearch')
def searchbg():
    name = request.args.get('bgquery')
    dbquery = Names.query.filter(Names.name.like(f'%{name}%')).all()
    results = [result.name for result in dbquery][:10]
    
    return jsonify(bglist=results)


@app.route("/", methods=['GET', 'POST'])
def home(data=None):
    form = MainForm()
    template_form = BoardGameForm(prefix='boardgames-_-')

    if form.validate_on_submit(): 
        ads, int_keys = repack(form)
        data = handle_data(ads, int_keys)

    return render_template('home.html', form=form, data=data, _template=template_form)


tag_exceptions = get_tag_exceptions()

if __name__ == "__main__":
    app.run()

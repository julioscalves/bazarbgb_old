import os
import re
import json
import requests
from bs4 import BeautifulSoup
from forms import BoardGameForm, MainForm
from flask import Flask, flash, render_template


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


def unpack_exceptions(content):
    tag_exceptions = {}
    content = [line for line in content if len(line) > 1]

    for line in content:
        split = line.strip().split('|')
        tag_exceptions[split[0]] = split[1]

    return tag_exceptions


def get_tag_exceptions():
    filename = 'exceptions.txt'

    with open(filename) as tags:
        content = tags.readlines()
        tag_exceptions = unpack_exceptions(content)

    return tag_exceptions


def get_source(link):
    source = link.split('//')
    source = source[1].split('.')

    if 'www' in source:
        return source[1]
    
    return source[0]


def validate_source(source):
    valid_sources = [
        'comparajogos', 'boardgamegeek'
    ]

    return source in valid_sources


def get_comparajogos_slug(link):
    slug = link.split('/')[-1]

    return slug


def get_comparajogos_data(link):
    url = 'https://api.comparajogos.com.br/v1/graphql'
    slug = get_comparajogos_slug(link)
    query = f'{{ product(where: {{slug: {{_eq: "{slug}"}}}}) {{ name }} }}'

    response = requests.post(url, json={'query': query})
    json_data = json.loads(response.text)
    name = json_data['data']['product'][0]['name']

    return name


def build_boardgamegeek_api_link(link):
    link = link.split('/')
    link.insert(3, 'xmlapi')
    link = '/'.join(link)

    return link


def get_boardgamegeek_data(link):
    try:
        url = build_boardgamegeek_api_link(link)
        request = requests.get(url)
        soup = BeautifulSoup(request.text, 'lxml')
        boardgame = soup.find('name', attrs={'primary': 'true'}).text

        return boardgame

    except:
        flash(f'ocorreu um erro. verifique se o link informado está \
                dentro dos padrões esperados e tente novamente')


def router(link, source):
    if source == 'comparajogos':
        return get_comparajogos_data(link)

    elif source == 'boardgamegeek':
        return get_boardgamegeek_data(link)


def remove_parenthesis(string):
    pattern = re.compile('[\(\[].*?[\)\]]')
    cleaned_string = re.sub(pattern, '', string)

    return cleaned_string


def remove_non_number(string):
    pattern = re.compile('[^0-9,.]')
    cleaned_string = re.sub(pattern, '', string)

    return cleaned_string


def format_name(name):
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

    name = f'#{name}'   

    return name


def assemble_message(adtype, text_list, output):
    if len(text_list) > 0:        
        if adtype == 'Venda':
            output += "#VENDO\n\n"
        
        elif adtype == 'Troca':
            output += "#TROCO\n\n"

        else:
            output += "#PROCURO\n\n"
        
        for ad in text_list:
            output += f'{ad}\n\n'

    return output


def handle_data(data, int_keys):
    sell = []
    trade = []
    search = []

    for index in int_keys:
        link = data[index].get('link')
        source = get_source(link)

        if validate_source(source):
            name = format_name(router(link, source))
            data[index]['name'] = name

            formatted_name = data[index]["name"]
            offer = data[index]['offer']
            details = data[index]['details']

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
    data = {}
    data['city'] = form_data.city.data
    data['state'] = form_data.state.data

    index = 1
    for games in form_data.boardgames.data:            
        data[index] = {
            'link'      : games['link'],
            'offer'     : games['offer'],
            'name'      : '',
            'price'     : games['price'],
            'details'   : games['details'],
        }
        index += 1

    int_keys = list(filter(lambda i: type(i) == int, data.keys()))

    return data, int_keys


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
    app.run(debug=True)

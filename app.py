import os
import re
import json
import requests
from bs4 import BeautifulSoup
from forms import LinkForm
from flask import Flask, flash, redirect, render_template, url_for


app = Flask(__name__)
app.config['SECRET_KEY'] = 'avb-jgm845tjv-a0mwtg8we0mcge5-c8' #os.environ['SECRET_KEY']


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


def assemble_tags(boardgames):
    tags = []
    
    for boardgame in boardgames:
        boardgame = remove_parenthesis(boardgame)
        boardgame = boardgame.replace('?', '')
        boardgame = boardgame.replace('!', '')
        boardgame = boardgame.replace(',', '')
        boardgame = boardgame.replace(' ', '')
        boardgame = boardgame.replace('&', 'N')
        boardgame = boardgame.replace('–', ' #')
        boardgame = boardgame.replace(':', ' #')  
        boardgame = boardgame.replace('-', '')      

        tags.append(f'#{boardgame}')

    return tags

def parse_data(offer, links, city, state):
    output = []
    links = links.split('\r')

    if len(links) > 20:
        links = links[:20]

    if offer == 'Troca':
        output.append('#TROCO')
    elif offer == 'Venda':
        output.append('#VENDO')
    else:
        output.append('#PROCURO')

    boardgames = []

    for link in links:
        source = get_source(link)
        
        if validate_source(source):
            boardgames.append(router(link, source))

    for tag in assemble_tags(boardgames):
        output.append(tag)

    output.append(f'#{city.title().replace(" ", "")} #{state}')

    return output


@app.route("/", methods=['GET', 'POST'])
def home(data=None):
    form = LinkForm()

    if form.validate_on_submit():
        offer   = form.offer.data
        links   = form.links.data.strip()
        city    = form.city.data
        state   = form.state.data
        details = form.details.data
        prices  = form.prices.data
        data    = parse_data(offer, links, city, state)
        
        redirect(url_for('home', data=data))

    return render_template('home.html', form=form, data=data)


if __name__ == "__main__":
    app.run(debug=True)
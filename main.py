from flask import Flask, render_template, request, redirect, url_for, session
import random
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Gacha Systems
GACHA_ODDS = {
    'N': 33,
    'N+': 25,
    'R': 20,
    'R+': 15,
    'SR': 5,
    'SR+': 2,
}

GACHA_11_ODDS = {
    'R': 57,
    'R+': 30,
    'SR': 10,
    'SR+': 3,
}

PREMIUM_GACHA_ODDS = {
    'N': 15,
    'N+': 10,
    'R': 20,
    'R+': 25,
    'SR': 15,
    'SR+': 15,
}

SR_PLUS_CHARACTERS = [f'SR+ (Character {i})' for i in range(1, 11)]


@app.template_filter('regex_split')
def regex_split(value):
    # Проверяем, содержит ли карта номер или нет
    match = re.match(r'([A-Za-z\+]+)\s*(\d+)?', value)
    if match:
        rarity = match.group(1)  # Редкость карты (например, R, N+)
        number = match.group(2) if match.group(
            2) else '1'  # Если номера нет, используем '1'
        return rarity, number
    return None


# Card Pulling Function (with system option)
def pull_card(odds, gacha_system='normal'):
    rand_val = random.randint(1, 100)
    cumulative = 0
    for rarity, chance in odds.items():
        cumulative += chance
        if rand_val <= cumulative:
            if rarity == 'SR+':
                character = random.choice(SR_PLUS_CHARACTERS)
                session['cards_pulled'].append(character)
                session['results'][
                    rarity] += 1  # just count rarity, not the full character
                return character
            session['cards_pulled'].append(rarity)
            session['results'][rarity] += 1
            return rarity
    return 'N'


# Initialization
def init_session():
    session['attempts'] = 0
    session['money_spent'] = 0
    session['results'] = {rarity: 0 for rarity in GACHA_ODDS.keys()}
    session['results']['SR+'] = 0
    session['cards_pulled'] = []  # Empty the list at the start


@app.route('/')
def index():
    if 'attempts' not in session:
        init_session()
    return render_template('index.html', session=session)


# Single Gacha
@app.route('/gacha', methods=['POST'])
def gacha():
    card = pull_card(GACHA_ODDS)
    session['attempts'] += 1
    session['money_spent'] += 100
    session['results'][card] += 1
    session['cards_pulled'].append(card)
    return redirect(url_for('index'))


# 11-Pull Gacha
@app.route('/gacha11', methods=['POST'])
def gacha11():
    for _ in range(10):
        card = pull_card(GACHA_11_ODDS)
        session['results'][card] += 1
        session['cards_pulled'].append(card)
    session['results']['SR'] += 1  # Guaranteed SR on the last pull
    session['cards_pulled'].append('SR')
    session['attempts'] += 11
    session['money_spent'] += 1000
    return redirect(url_for('index'))


# Premium Gacha
@app.route('/gacha_premium', methods=['POST'])
def gacha_premium():
    card = pull_card(PREMIUM_GACHA_ODDS, gacha_system='premium')
    session['attempts'] += 1
    session['money_spent'] += 200  # Example premium price
    session['results'][card] += 1
    session['cards_pulled'].append(card)
    return redirect(url_for('index'))


# Маршрут для отображения страницы с результатами
@app.route('/results')
def results():
    cards_pulled = session.get('cards_pulled', [])
    images = []
    for card in cards_pulled:
        rarity = card.split(' ')[0] if ' ' in card else card
        image_path = f'static/images/{rarity}/{rarity}1.jpg'  # Пример имени изображения
        images.append(image_path)
    return render_template('results.html', images=images)


# Reset Stats
@app.route('/reset', methods=['POST'])
def reset():
    init_session()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
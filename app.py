import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# НАША БАЗА ДАННЫХ ИГРЫ
PLAYERS = {
    "mcdavid": {"name": "Коннор Макдэвид", "attack": 50, "defense": 20, "image": "⚡"},
    "ovechkin": {"name": "Александр Овечкин", "attack": 45, "defense": 15, "image": "🏒"},
    "hedman": {"name": "Виктор Хедман", "attack": 20, "defense": 50, "image": "🛡️"}
}

ACTION_CARDS = {
    "attack_wrist": {"name": "Кистевой бросок", "bonus": 15, "type": "attack", "desc": "+15 к атаке"},
    "attack_office": {"name": "Щелчок из офиса", "bonus": 25, "type": "attack", "desc": "+25 к атаке"},
    "def_hit": {"name": "Силовой прием", "bonus": 20, "type": "defense", "desc": "+20 к защите"}
}

# Главная страница — теперь она загружает визуальный интерфейс
@app.route('/')
def home():
    return render_template('index.html')

# API для получения списка карт (чтобы интерфейс знал, кого показывать)
@app.route('/api/cards', methods=['GET'])
def get_cards():
    return jsonify({
        "players": PLAYERS,
        "actions": ACTION_CARDS
    })

# API для проведения дуэли
@app.route('/play', methods=['POST'])
def play_duel():
    data = request.json
    player_id = data.get('player_id')
    action_id = data.get('action_id')
    
    # Проверяем, всё ли выбрано
    if not player_id or not action_id:
        return jsonify({"error": "Выбери игрока и карту действия!"}), 400
        
    # Данные игрока
    p_hockeyist = PLAYERS[player_id]
    p_action = ACTION_CARDS[action_id]
    
    # Считаем общую силу игрока (база + бонус карты)
    # Если карта атакующая — качаем атаку, если защитная — защиту
    if p_action["type"] == "attack":
        player_total = p_hockeyist["attack"] + p_action["bonus"]
    else:
        player_total = p_hockeyist["defense"] + p_action["bonus"]
        
    # Бот выбирает своего хоккеиста и карту случайным образом
    bot_player_id = random.choice(list(PLAYERS.keys()))
    bot_action_id = random.choice(list(ACTION_CARDS.keys()))
    
    b_hockeyist = PLAYERS[bot_player_id]
    b_action = ACTION_CARDS[bot_action_id]
    
    if b_action["type"] == "attack":
        bot_total = b_hockeyist["attack"] + b_action["bonus"]
    else:
        bot_total = b_hockeyist["defense"] + b_action["bonus"]
        
    # Сравниваем силы
    if player_total > bot_total:
        result_text = f"ГОЛ! {p_hockeyist['name']} пробил оборону бота!"
    elif player_total < bot_total:
        result_text = f"СЕЙВ! Бот защитился силами {b_hockeyist['name']}."
    else:
        result_text = "НИЧЬЯ! Жесткий стык у бортика, шайба потеряна."
        
    return jsonify({
        "result": result_text,
        "player_score": player_total,
        "bot_score": bot_total,
        "bot_setup": f"{b_hockeyist['name']} + {b_action['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

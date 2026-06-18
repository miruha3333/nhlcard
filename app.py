import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# РАСШИРЕННЫЙ РОСТЕР ИГРОКОВ
PLAYERS = {
    "mcdavid": {"name": "Коннор Макдэвид", "attack": 55, "defense": 20, "image": "⚡"},
    "ovechkin": {"name": "Александр Овечкин", "attack": 50, "defense": 15, "image": "🏒"},
    "panarin": {"name": "Артемий Панарин", "attack": 48, "defense": 22, "image": "👑"},
    "kucherov": {"name": "Никита Кучеров", "attack": 52, "defense": 18, "image": "🪄"},
    "hedman": {"name": "Виктор Хедман", "attack": 25, "defense": 52, "image": "🛡️"},
    "makar": {"name": "Кейл Макар", "attack": 35, "defense": 48, "image": "🛹"}
}

# КАРТЫ С УЛУЧШЕННОЙ МАТЕМАТИКОЙ
ACTION_CARDS = {
    "attack_wrist": {"name": "Кистевой Панарина", "type": "attack", "mod_type": "add", "value": 15, "desc": "+15 к атаке"},
    "attack_office": {"name": "Офис Ови", "type": "attack", "mod_type": "add", "value": 25, "desc": "+25 к атаке"},
    "mcdavid_turbo": {"name": "Турбо Макдэвида", "type": "attack", "mod_type": "mult", "value": 1.5, "desc": "Умножает атаку на 1.5"},
    "def_hit": {"name": "Мельница Макара", "type": "defense", "mod_type": "add", "value": 20, "desc": "+20 к защите"},
    "vasilevskiy_wall": {"name": "Шпагат Василевского", "type": "defense", "mod_type": "add", "value": 30, "desc": "+30 к защите"},
    "shesterkin_flex": {"name": "Сейв Шестеркина", "type": "defense", "mod_type": "mult", "value": 1.6, "desc": "Умножает защиту на 1.6"}
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/cards', methods=['GET'])
def get_cards():
    return jsonify({"players": PLAYERS, "actions": ACTION_CARDS})

@app.route('/play', methods=['POST'])
def play_duel():
    data = request.json
    player_id = data.get('player_id')
    action_id = data.get('action_id')
    
    if not player_id or not action_id:
        return jsonify({"error": "Выбери игрока и карту!"}), 400
        
    p_hockeyist = PLAYERS[player_id]
    p_action = ACTION_CARDS[action_id]
    
    # 1. РАСЧЕТ СИЛЫ ИГРОКА
    base_power = p_hockeyist["attack"] if p_action["type"] == "attack" else p_hockeyist["defense"]
    if p_action["mod_type"] == "add":
        player_total = base_power + p_action["value"]
    else:  # если мультипликатор (mult)
        player_total = int(base_power * p_action["value"])
        
    # Добавляем хоккейный рандом (кубик от -10 до +10)
    p_random = random.randint(-10, 10)
    player_total += p_random

    # 2. ХОД БОТА (ИИ)
    bot_player_id = random.choice(list(PLAYERS.keys()))
    bot_action_id = random.choice(list(ACTION_CARDS.keys()))
    b_hockeyist = PLAYERS[bot_player_id]
    b_action = ACTION_CARDS[bot_action_id]
    
    bot_base = b_hockeyist["attack"] if b_action["type"] == "attack" else b_hockeyist["defense"]
    if b_action["mod_type"] == "add":
        bot_total = bot_base + b_action["value"]
    else:
        bot_total = int(bot_base * b_action["value"])
        
    b_random = random.randint(-10, 10)
    bot_total += b_random
        
    # 3. ОПРЕДЕЛЕНИЕ КТО ПОБЕДИЛ В ПЕРИОДЕ
    if player_total > bot_total:
        round_winner = "player"
        details = f"ГОЛ! {p_hockeyist['name']} забивает в этом периоде! (Удача: {p_random})"
    elif player_total < bot_total:
        round_winner = "bot"
        details = f"ПРОПУСТИЛИ. Бот забивает силами {b_hockeyist['name']}. (Удача бота: {b_random})"
    else:
        round_winner = "draw"
        details = "НИЧЬЯ в периоде! Вратари потащили мертвые шайбы."
        
    return jsonify({
        "winner": round_winner,
        "details": details,
        "player_score": player_total,
        "bot_score": bot_total,
        "bot_setup": f"{b_hockeyist['name']} + {b_action['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

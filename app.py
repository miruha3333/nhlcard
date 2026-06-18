import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# ОГРОМНЫЙ ПУЛ ЗВЕЗД НХЛ
FORWARDS = {
    "mcdavid": {"name": "К. Макдэвид", "attack": 55, "defense": 20, "image": "⚡"},
    "ovechkin": {"name": "А. Овечкин", "attack": 50, "defense": 15, "image": "🏒"},
    "panarin": {"name": "А. Панарин", "attack": 48, "defense": 22, "image": "👑"},
    "kucherov": {"name": "Н. Кучеров", "attack": 52, "defense": 18, "image": "🪄"},
    "mackinnon": {"name": "Н. Маккиннон", "attack": 54, "defense": 25, "image": "🚂"},
    "matthews": {"name": "О. Мэттьюс", "attack": 53, "defense": 28, "image": "🎯"}
}

DEFENDERS = {
    "hedman": {"name": "В. Хедман", "attack": 25, "defense": 52, "image": "🛡️"},
    "makar": {"name": "К. Макар", "attack": 35, "defense": 48, "image": " Skate"},
    "josi": {"name": "Р. Йоси", "attack": 33, "defense": 46, "image": "🦅"},
    "fox": {"name": "А. Фокс", "attack": 30, "defense": 47, "image": "🦊"},
    "hughes": {"name": "К. Хьюз", "attack": 38, "defense": 43, "image": "🚀"},
    "mcavoy": {"name": "Ч. Макэвой", "attack": 22, "defense": 50, "image": "🐻"}
}

ACTION_CARDS = {
    "att_wrist": {"name": "Кистевой бросок", "type": "attack", "mod_type": "add", "value": 15, "desc": "+15 к атаке"},
    "att_office": {"name": "Бросок из офиса", "type": "attack", "mod_type": "add", "value": 25, "desc": "+25 к атаке"},
    "att_turbo": {"name": "Турбо-рывок", "type": "attack", "mod_type": "mult", "value": 1.4, "desc": "Атака х1.4"},
    "att_onetimer": {"name": "Ван-таймер", "type": "attack", "mod_type": "add", "value": 20, "desc": "+20 к атаке"},
    
    "def_hit": {"name": "Силовой прием", "type": "defense", "mod_type": "add", "value": 20, "desc": "+20 к защите"},
    "def_poke": {"name": "Работа клюшкой", "type": "defense", "mod_type": "add", "value": 12, "desc": "+12 к защите"},
    "def_block": {"name": "Блокшот под шайбу", "type": "defense", "mod_type": "add", "value": 25, "desc": "+25 к защите"},
    "def_wall": {"name": "Автобус у ворот", "type": "defense", "mod_type": "mult", "value": 1.5, "desc": "Защита х1.5"}
}

@app.route('/')
def home():
    return render_template('index.html')

# API выдает полный набор, из которого фронтенд соберет случайную руку
@app.route('/api/init_deck', methods=['GET'])
def init_deck():
    return jsonify({
        "forwards": FORWARDS,
        "defenders": DEFENDERS,
        "actions": ACTION_CARDS
    })

@app.route('/play', methods=['POST'])
def play_duel():
    data = request.json
    player_id = data.get('player_id')
    action_id = data.get('action_id')
    fatigued_players = data.get('fatigued_players', []) # Список уставших ID

    # Ищем игрока в общем пуле
    all_players = {**FORWARDS, **DEFENDERS}
    p_hockeyist = all_players[player_id]
    p_action = ACTION_CARDS[action_id]
    
    # Расчет базы
    base_power = p_hockeyist["attack"] if p_action["type"] == "attack" else p_hockeyist["defense"]
    
    # ПРИМЕНЯЕМ УСТАЛОСТЬ (-30%), если хоккеист уже играл
    if player_id in fatigued_players:
        base_power = int(base_power * 0.7)
        
    # Математика карты
    if p_action["mod_type"] == "add":
        player_total = base_power + p_action["value"]
    else:
        player_total = int(base_power * p_action["value"])
        
    player_total += random.randint(-8, 8) # Хоккейный рандом

    # ХОД БОТА
    bot_player_id = random.choice(list(all_players.keys()))
    bot_action_id = random.choice(list(ACTION_CARDS.keys()))
    b_hockeyist = all_players[bot_player_id]
    b_action = ACTION_CARDS[bot_action_id]
    
    bot_base = b_hockeyist["attack"] if b_action["type"] == "attack" else b_hockeyist["defense"]
    if b_action["mod_type"] == "add":
        bot_total = bot_base + b_action["value"]
    else:
        bot_total = int(bot_base * b_action["value"])
    bot_total += random.randint(-8, 8)
        
    if player_total > bot_total:
        round_winner = "player"
        details = f"ГОЛ! {p_hockeyist['name']} забивает!"
    elif player_total < bot_total:
        round_winner = "bot"
        details = f"ПРОПУСТИЛИ. Бот забил через {b_hockeyist['name']}."
    else:
        round_winner = "draw"
        details = "НИЧЬЯ! Вратари совершили двойной сейв."
        
    return jsonify({
        "winner": round_winner, "details": details,
        "player_score": player_total, "bot_score": bot_total,
        "bot_setup": f"{b_hockeyist['name']} + {b_action['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

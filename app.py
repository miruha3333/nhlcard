import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# БАЗА ДАННЫХ ИГРЫ
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
    "makar": {"name": "К. Макар", "attack": 36, "defense": 48, "image": "⛸️"},
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
    "def_block": {"name": "Блокшот", "type": "defense", "mod_type": "add", "value": 25, "desc": "+25 к защите"},
    "def_wall": {"name": "Автобус у ворот", "type": "defense", "mod_type": "mult", "value": 1.5, "desc": "Защита х1.5"}
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/init_deck', methods=['GET'])
def init_deck():
    return jsonify({
        "forwards": FORWARDS,
        "defenders": DEFENDERS,
        "actions": ACTION_CARDS
    })

@app.route('/play', methods=['POST'])
def play_round():
    data = request.json
    player_id = data.get('player_id')
    action_id = data.get('action_id')
    round_idx = int(data.get('round_idx')) # 1, 2 или 3
    fatigued_players = data.get('fatigued_players', [])

    all_players = {**FORWARDS, **DEFENDERS}
    p_hockeyist = all_players[player_id]
    p_action = ACTION_CARDS[action_id]
    
    # 1. Считаем силу игрока в зависимости от карты тактики
    p_base = p_hockeyist["attack"] if p_action["type"] == "attack" else p_hockeyist["defense"]
    
    # Применяем штраф усталости
    if player_id in fatigued_players:
        p_base = int(p_base * 0.7)
        
    if p_action["mod_type"] == "add":
        player_total = p_base + p_action["value"]
    else:
        player_total = int(p_base * p_action["value"])
    player_total += random.randint(-6, 6) # Хоккейный рандом (отскок)

    # 2. Логика УМНОГО БОТА (ИИ подстраивается под тип раунда)
    if round_idx == 1:
        # Игрок атакует -> Бот профессионально обороняется
        bot_hockeyist = random.choice(list(DEFENDERS.values()))
        bot_action = random.choice([c for c in ACTION_CARDS.values() if c["type"] == "defense"])
        bot_total = bot_hockeyist["defense"]
    elif round_idx == 2:
        # Бот атакует -> Игрок должен обороняться
        bot_hockeyist = random.choice(list(FORWARDS.values()))
        bot_action = random.choice([c for c in ACTION_CARDS.values() if c["type"] == "attack"])
        bot_total = bot_hockeyist["attack"]
    else:
        # Раунд 3: Обоюдное вбрасывание, бот выбирает случайный стиль
        bot_hockeyist = random.choice(list(all_players.values()))
        bot_action = random.choice(list(ACTION_CARDS.values()))
        bot_total = bot_hockeyist["attack"] if bot_action["type"] == "attack" else bot_hockeyist["defense"]

    # Рассчитываем итоговую силу бота
    if bot_action["mod_type"] == "add":
        bot_total += bot_action["value"]
    else:
        bot_total = int(bot_total * bot_action["value"])
    bot_total += random.randint(-6, 6)

    # 3. ОПРЕДЕЛЕНИЕ ИСХОДА РАУНДА
    round_winner = "draw"
    details = ""

    if round_idx == 1: # Атака игрока
        if player_total > bot_total:
            round_winner = "player_goal"
            details = f"ГОООЛ! {p_hockeyist['name']} пробил оборону бота!"
        else:
            round_winner = "bot_saved"
            details = f"Сейв! Бот защитился силами {bot_hockeyist['name']}."
            
    elif round_idx == 2: # Атака бота
        if bot_total > player_total:
            round_winner = "bot_goal"
            details = f"Пропускаем... {bot_hockeyist['name']} забивает в наши ворота."
        else:
            round_winner = "player_saved"
            details = f"Красивый бэкчек! {p_hockeyist['name']} заблокировал атаку бота!"
            
    else: # Раунд 3: Свободный лед
        if player_total > bot_total:
            round_winner = "player_goal"
            details = f"Вбрасывание за нами! {p_hockeyist['name']} заколачивает шайбу!"
        elif bot_total > player_total:
            round_winner = "bot_goal"
            details = f"Бот выиграл борьбу на пятаке. Гол забивает {bot_hockeyist['name']}."
        else:
            round_winner = "draw"
            details = "Ничья на встречных курсах! Вратари потащили."

    return jsonify({
        "winner_type": round_winner,
        "details": details,
        "player_score": player_total,
        "bot_score": bot_total,
        "bot_setup": f"{bot_hockeyist['name']} ({bot_action['name']})"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

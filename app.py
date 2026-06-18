import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# БАЗА ИГРОКОВ
FORWARDS = {
    "mcdavid": {"name": "К. Макдэвид", "attack": 55, "defense": 20, "image": "⚡"},
    "kucherov": {"name": "Н. Кучеров", "attack": 52, "defense": 18, "image": "🪄"}
    # ... добавь остальных
}

DEFENDERS = {
    "hedman": {"name": "В. Хедман", "attack": 25, "defense": 52, "image": "🛡️"},
    "fox": {"name": "А. Фокс", "attack": 30, "defense": 47, "image": "🦊"}
    # ... добавь остальных
}

# БАЗА КАРТ С МЕХАНИКОЙ "КРИПТОНИТА" (counters)
ACTION_CARDS = {
    # Атакующие
    "att_onetimer": {"name": "Ван-таймер", "type": "attack", "value": 20, "counters": "def_wall", "desc": "+20 (Контрит Автобус)"},
    "att_wrist": {"name": "Кистевой в девятку", "type": "attack", "value": 15, "counters": "def_poke", "desc": "+15 (Контрит Клюшку)"},
    "att_office": {"name": "Бросок из офиса", "type": "attack", "value": 25, "counters": "none", "desc": "+25 (Без бонусов)"},
    
    # Защитные
    "def_block": {"name": "Жесткий Блокшот", "type": "defense", "value": 20, "counters": "att_onetimer", "desc": "+20 (Сжирает Ван-таймер)"},
    "def_poke": {"name": "Выбивание клюшкой", "type": "defense", "value": 15, "counters": "att_office", "desc": "+15 (Контрит Офис)"},
    "def_wall": {"name": "Автобус у ворот", "type": "defense", "value": 25, "counters": "att_wrist", "desc": "+25 (Сжирает Кистевой)"}
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
    p_action_id = data.get('action_id')
    round_idx = int(data.get('round_idx'))
    
    all_players = {**FORWARDS, **DEFENDERS}
    p_hockeyist = all_players[player_id]
    p_card = ACTION_CARDS[p_action_id]
    
    # --- 1. ТУМАН ВОЙНЫ И ИИ (Скрытый выбор бота) ---
    bot_hockeyist = None
    bot_action_id = None
    
    # Бот выбирает логичную роль под раунд
    if round_idx == 1: # Мы атакуем, бот защищается
        bot_hockeyist = random.choice(list(DEFENDERS.values()))
        bot_action_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "defense"])
    elif round_idx == 2: # Бот атакует
        bot_hockeyist = random.choice(list(FORWARDS.values()))
        bot_action_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "attack"])
    else: # Вбрасывание
        bot_hockeyist = random.choice(list(all_players.values()))
        bot_action_id = random.choice(list(ACTION_CARDS.keys()))
        
    bot_card = ACTION_CARDS[bot_action_id]

    # --- 2. БАЗОВЫЕ ОЧКИ ---
    p_base = p_hockeyist["attack"] if p_card["type"] == "attack" else p_hockeyist["defense"]
    bot_base = bot_hockeyist["attack"] if bot_card["type"] == "attack" else bot_hockeyist["defense"]
    
    player_total = p_base + p_card["value"]
    bot_total = bot_base + bot_card["value"]

    # --- 3. МЕХАНИКА "КРИПТОНИТА" (Камень-ножницы-бумага) ---
    kryptonite_msg = ""
    # Если карта игрока контрит карту бота
    if p_card.get("counters") == bot_action_id:
        bot_total -= 15
        kryptonite_msg = f" Твой '{p_card['name']}' законтрил тактику бота (-15 ИИ)!"
    # Если карта бота контрит карту игрока
    elif bot_card.get("counters") == p_action_id:
        player_total -= 15
        kryptonite_msg = f" Бот прочитал тебя! Его '{bot_card['name']}' сожрал твою тактику (-15 тебе)!"

    # --- 4. ХОККЕЙНЫЙ БОГ (Удача/Рандом от -8 до +8) ---
    p_luck = random.randint(-8, 8)
    b_luck = random.randint(-8, 8)
    player_total += p_luck
    bot_total += b_luck

    # --- 5. РЕЗУЛЬТАТЫ ---
    round_winner = "draw"
    details = ""

    if round_idx == 1: # Твоя Атака
        if player_total > bot_total:
            round_winner = "player_goal"
            details = f"ГООЛ! {p_hockeyist['name']} пробил бота."
        else:
            round_winner = "bot_saved"
            details = f"Сейв бота! Твоя атака захлебнулась."
    elif round_idx == 2: # Атака бота
        if bot_total > player_total:
            round_winner = "bot_goal"
            details = f"ГОЛ В НАШИ ВОРОТА. {bot_hockeyist['name']} забивает."
        else:
            round_winner = "player_saved"
            details = f"Отличный блок! Ты отбился от атаки бота."
    else: # Вбрасывание
        if player_total > bot_total:
            round_winner = "player_goal"
            details = "Забираем вбрасывание и забиваем!"
        elif bot_total > player_total:
            round_winner = "bot_goal"
            details = "Бот выиграл пятак и заколотил шайбу."
        else:
            round_winner = "draw"
            details = "Жесткая борьба у бортов. Ничья."

    # Добавляем инфу о Криптоните в детали, если он сработал
    details += kryptonite_msg

    return jsonify({
        "winner_type": round_winner,
        "details": details,
        "player_score": f"{player_total} (удача {p_luck:+d})",
        "bot_score": f"{bot_total} (удача {b_luck:+d})",
        "bot_setup": f"{bot_hockeyist['name']} + {bot_card['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

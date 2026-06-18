import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

PLAYERS = {
    "mcdavid": {"name": "К. Макдэвид", "attack": 55, "defense": 20, "image": "⚡", "tier": "Золото"},
    "kucherov": {"name": "Н. Кучеров", "attack": 52, "defense": 18, "image": "🪄", "tier": "Золото"},
    "bedard": {"name": "К. Бедард", "attack": 43, "defense": 15, "image": "🎯", "tier": "Серебро"},
    "michkov": {"name": "М. Мичков", "attack": 38, "defense": 12, "image": "🔥", "tier": "Бронза"},
    "celebrini": {"name": "М. Челебрини", "attack": 35, "defense": 10, "image": "👶", "tier": "Бронза"},
    
    "hedman": {"name": "В. Хедман", "attack": 25, "defense": 53, "image": "🛡️", "tier": "Золото"},
    "fox": {"name": "А. Фокс", "attack": 28, "defense": 48, "image": "🦊", "tier": "Золото"},
    "mintyukov": {"name": "П. Минтюков", "attack": 20, "defense": 41, "image": "🏒", "tier": "Серебро"},
    "levshunov": {"name": "А. Левшунов", "attack": 15, "defense": 34, "image": "🧱", "tier": "Бронза"}
}

ACTION_CARDS = {
    "att_onetimer": {"name": "Ван-таймер", "type": "attack", "value": 20, "beats": "def_poke", "desc": "+20 Атака (Бьет Выбивание)"},
    "att_wrist": {"name": "Кистевой", "type": "attack", "value": 15, "beats": "def_block", "desc": "+15 Атака (Бьет Блок)"},
    "att_office": {"name": "Из офиса", "type": "attack", "value": 25, "beats": "def_wall", "desc": "+25 Атака (Бьет Автобус)"},
    
    "def_block": {"name": "Жесткий Блок", "type": "defense", "value": 20, "beats": "att_onetimer", "desc": "+20 Защита (Бьет Ван-таймер)"},
    "def_poke": {"name": "Выбивание", "type": "defense", "value": 15, "beats": "att_office", "desc": "+15 Защита (Бьет Из офиса)"},
    "def_wall": {"name": "Автобус", "type": "defense", "value": 25, "beats": "att_wrist", "desc": "+25 Защита (Бьет Кистевой)"}
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/init_deck', methods=['GET'])
def init_deck():
    return jsonify({"players": PLAYERS, "actions": ACTION_CARDS})

@app.route('/buy_pack', methods=['POST'])
def buy_pack():
    roll = random.random()
    if roll < 0.15: target_tier = "Золото"
    elif roll < 0.50: target_tier = "Серебро"
    else: target_tier = "Бронза"
        
    tier_players = [k for k, v in PLAYERS.items() if v["tier"] == target_tier]
    dropped_player_id = random.choice(tier_players if tier_players else list(PLAYERS.keys()))
    dropped_card_id = random.choice(list(ACTION_CARDS.keys()))
    
    return jsonify({
        "player": {"id": dropped_player_id, "data": PLAYERS[dropped_player_id]},
        "card": {"id": dropped_card_id, "data": ACTION_CARDS[dropped_card_id]}
    })

@app.route('/play', methods=['POST'])
def play_round():
    data = request.json
    player_id, p_action_id, round_idx = data.get('player_id'), data.get('action_id'), int(data.get('round_idx'))
    
    p_hockeyist, p_card = PLAYERS[player_id], ACTION_CARDS[p_action_id]
    
    # Бот берет любого случайного игрока
    bot_player_id = random.choice(list(PLAYERS.keys()))
    bot_hockeyist = PLAYERS[bot_player_id]
    
    # Умный выбор бота в зависимости от фазы периода
    if round_idx == 1: 
        bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "defense"])
    elif round_idx == 2: 
        bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "attack"])
    else: 
        bot_card_id = random.choice(list(ACTION_CARDS.keys()))
        
    bot_card = ACTION_CARDS[bot_card_id]
    
    # Считаем базовые очки
    p_base = p_hockeyist["attack"] if p_card["type"] == "attack" else p_hockeyist["defense"]
    bot_base = bot_hockeyist["attack"] if bot_card["type"] == "attack" else bot_hockeyist["defense"]
    
    player_total = p_base + p_card["value"]
    bot_total = bot_base + bot_card["value"]
    
    # Система смертельных контр-пиков (-30 очков)
    kryptonite_msg = ""
    if p_card.get("beats") == bot_card_id:
        bot_total -= 30
        kryptonite_msg = " 🎯 Смертельный контр-пик! ИИ разгромлен (-30 очков ИИ)!"
    elif bot_card.get("beats") == p_action_id:
        player_total -= 30
        kryptonite_msg = " ❌ Бот полностью прочитал тебя (-30 очков тебе)!"
        
    # Случайность (Рандомный отскок шайбы)
    player_total += random.randint(-5, 5)
    bot_total += random.randint(-5, 5)
    
    is_win = player_total > bot_total if round_idx != 2 else player_total >= bot_total
    is_tie = player_total == bot_total and round_idx != 2
    
    if is_tie:
        details = "Ничья в раунде! Шайба застряла в ловушке вратаря."
    elif round_idx == 1:
        details = "ГООЛ! Красивая комбинация увенчалась взятием ворот!" if is_win else "Сейв! Вратарь ИИ парировал твой бросок."
    elif round_idx == 2:
        details = "Защита сработала! Ты заблокировал атаку." if is_win else "Гол! ИИ пробил твою оборону."
    else:
        details = "Чистая победа на вбрасывании!" if is_win else "ИИ забирает вбрасывание под свой контроль."
        
    details += kryptonite_msg
    
    return jsonify({
        "is_win": is_win,
        "is_tie": is_tie,
        "details": details,
        "player_score": player_total,
        "bot_score": bot_total,
        "bot_setup": f"{bot_hockeyist['name']} + {bot_card['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

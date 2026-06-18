import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# БАЗА ИГРОКОВ (Эмодзи вместо картинок для стабильности)
PLAYERS = {
    # ФОРВАРДЫ
    "mcdavid": {"name": "К. Макдэвид", "attack": 55, "defense": 20, "image": "⚡", "tier": "Золото"},
    "kucherov": {"name": "Н. Кучеров", "attack": 52, "defense": 18, "image": "🪄", "tier": "Золото"},
    "bedard": {"name": "К. Бедард", "attack": 43, "defense": 15, "image": "🎯", "tier": "Серебро"},
    "michkov": {"name": "М. Мичков", "attack": 38, "defense": 12, "image": "🔥", "tier": "Бронза"},
    "celebrini": {"name": "М. Челебрини", "attack": 35, "defense": 10, "image": "👶", "tier": "Бронза"},
    
    # ЗАЩИТНИКИ
    "hedman": {"name": "В. Хедман", "attack": 25, "defense": 53, "image": "🛡️", "tier": "Золото"},
    "fox": {"name": "А. Фокс", "attack": 28, "defense": 48, "image": "🦊", "tier": "Золото"},
    "mintyukov": {"name": "П. Минтюков", "attack": 20, "defense": 41, "image": "🏒", "tier": "Серебро"},
    "levshunov": {"name": "А. Левшунов", "attack": 15, "defense": 34, "image": "🧱", "tier": "Бронза"}
}

# БАЗА КАРТ ТАКТИКИ
ACTION_CARDS = {
    "att_onetimer": {"name": "Ван-таймер", "type": "attack", "value": 20, "counters": "def_block", "desc": "+20 Атака (Контрится Блоком)"},
    "att_wrist": {"name": "Кистевой", "type": "attack", "value": 15, "counters": "def_wall", "desc": "+15 Атака (Контрится Автобусом)"},
    "att_office": {"name": "Из офиса", "type": "attack", "value": 25, "counters": "def_poke", "desc": "+25 Атака (Контрится Клюшкой)"},
    
    "def_block": {"name": "Жесткий Блок", "type": "defense", "value": 20, "counters": "att_office", "desc": "+20 Защита (Бьет Офис)"},
    "def_poke": {"name": "Выбивание", "type": "defense", "value": 15, "counters": "att_onetimer", "desc": "+15 Защита (Бьет Ван-таймер)"},
    "def_wall": {"name": "Автобус", "type": "defense", "value": 25, "counters": "att_wrist", "desc": "+25 Защита (Бьет Кистевой)"}
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
    
    bot_player_id = random.choice([k for k in PLAYERS.keys() if k != player_id])
    bot_hockeyist = PLAYERS[bot_player_id]
    
    if round_idx == 1: bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "defense"])
    elif round_idx == 2: bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "attack"])
    else: bot_card_id = random.choice(list(ACTION_CARDS.keys()))
        
    bot_card = ACTION_CARDS[bot_card_id]
    
    p_base = p_hockeyist["attack"] if p_card["type"] == "attack" else p_hockeyist["defense"]
    bot_base = bot_hockeyist["attack"] if bot_card["type"] == "attack" else bot_hockeyist["defense"]
    
    player_total, bot_total = p_base + p_card["value"], bot_base + bot_card["value"]
    
    kryptonite_msg = ""
    if p_card.get("counters") == bot_card_id:
        bot_total -= 15
        kryptonite_msg = f" 🎯 Твоя тактика законтрила бота (-15)!"
    elif bot_card.get("counters") == p_action_id:
        player_total -= 15
        kryptonite_msg = f" ❌ Бот прочитал тебя (-15 тебе)!"
        
    p_luck, b_luck = random.randint(-5, 5), random.randint(-5, 5)
    player_total += p_luck
    bot_total += b_luck
    
    is_win = player_total > bot_total if round_idx != 2 else player_total >= bot_total
    is_tie = player_total == bot_total and round_idx != 2
    
    if is_tie:
        details = "Ничья в раунде! Вратари на высоте."
        is_win = False # Ничья не дает очка
    elif round_idx == 1:
        details = "ГООЛ! Ты пробил защиту!" if is_win else "Сейв! Бот отбился."
    elif round_idx == 2:
        details = "Сейв! Ты остановил атаку!" if is_win else "Гол в твои ворота!"
    else:
        # Вот здесь была та самая сломанная строка
        details = "Победа на вбрасывании!" if is_win else "Бот выиграл вбрасывание."
        
    details += kryptonite_msg
    
    return jsonify({
        "is_win": is_win,
        "is_tie": is_tie,
        "details": details,
        "player_score": player_total,
        "bot_score": bot_total,
        "bot_setup": f"{bot_hockeyist['name']} [{bot_hockeyist['tier']}] + {bot_card['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

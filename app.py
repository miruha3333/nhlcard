import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# ПОЛНАЯ БАЗА ИГРОКОВ (Разбита на Золото, Серебро и Бронзу)
# Вместо ломающихся картинок используем стабильные хоккейные эмодзи!
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

# ПОЛНАЯ БАЗА КАРТ С МЕХАНИКОЙ КРИПТОНИТА
ACTION_CARDS = {
    "att_onetimer": {"name": "Ван-таймер", "type": "attack", "value": 20, "counters": "def_block", "desc": "+20 Атака (Уязвима к Блокшоту)"},
    "att_wrist": {"name": "Кистевой в девятку", "type": "attack", "value": 15, "counters": "def_wall", "desc": "+15 Атака (Уязвима к Автобусу)"},
    "att_office": {"name": "Бросок из офиса", "type": "attack", "value": 25, "counters": "def_poke", "desc": "+25 Атака (Уязвима к Клюшке)"},
    
    "def_block": {"name": "Жесткий Блокшот", "type": "defense", "value": 20, "counters": "att_office", "desc": "+20 Защита (Уничтожает Офис)"},
    "def_poke": {"name": "Выбивание клюшкой", "type": "defense", "value": 15, "counters": "att_onetimer", "desc": "+15 Защита (Уничтожает Ван-таймер)"},
    "def_wall": {"name": "Автобус у ворот", "type": "defense", "value": 25, "counters": "att_wrist", "desc": "+25 Защита (Уничтожает Кистевой)"}
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/init_deck', methods=['GET'])
def init_deck():
    return jsonify({
        "players": PLAYERS,
        "actions": ACTION_CARDS
    })

@app.route('/buy_pack', methods=['POST'])
def buy_pack():
    # Шансы в паке: 50% Бронза, 35% Серебро, 15% Золото
    roll = random.random()
    if roll < 0.15:
        target_tier = "Золото"
    elif roll < 0.50:
        target_tier = "Серебро"
    else:
        target_tier = "Бронза"
        
    # Выбираем игрока выпавшего тира
    tier_players = [k for k, v in PLAYERS.items() if v["tier"] == target_tier]
    dropped_player_id = random.choice(tier_players if tier_players else list(PLAYERS.keys()))
    
    # Тактическая карта выпадает абсолютно любая случайная
    dropped_card_id = random.choice(list(ACTION_CARDS.keys()))
    
    return jsonify({
        "player": {"id": dropped_player_id, "data": PLAYERS[dropped_player_id]},
        "card": {"id": dropped_card_id, "data": ACTION_CARDS[dropped_card_id]}
    })

@app.route('/play', methods=['POST'])
def play_round():
    data = request.json
    player_id = data.get('player_id')
    p_action_id = data.get('action_id')
    round_idx = int(data.get('round_idx'))
    
    p_hockeyist = PLAYERS[player_id]
    p_card = ACTION_CARDS[p_action_id]
    
    # АСИММЕТРИЯ: Бот берет любого игрока из базы, КРОМЕ того, за кого играешь ты в этом раунде
    available_bot_players = [k for k in PLAYERS.keys() if k != player_id]
    bot_player_id = random.choice(available_bot_players)
    bot_hockeyist = PLAYERS[bot_player_id]
    
    # Умный выбор карт для ИИ в зависимости от типа раунда (Туман войны)
    if round_idx == 1: # Игрок атакует -> Бот защищается
        bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "defense"])
    elif round_idx == 2: # Бот атакует -> Игрок защищается
        bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "attack"])
    else: # Вбрасывание (Рандом)
        bot_card_id = random.choice(list(ACTION_CARDS.keys()))
        
    bot_card = ACTION_CARDS[bot_card_id]
    
    # Базовые расчеты
    p_base = p_hockeyist["attack"] if p_card["type"] == "attack" else p_hockeyist["defense"]
    bot_base = bot_hockeyist["attack"] if bot_card["type"] == "attack" else bot_hockeyist["defense"]
    
    player_total = p_base + p_card["value"]
    bot_total = bot_base + bot_card["value"]
    
    # МЕХАНИКА КРИПТОНИТА
    kryptonite_msg = ""
    if p_card.get("counters") == bot_card_id:
        bot_total -= 15
        kryptonite_msg = f" 🎯 Твой '{p_card['name']}' законтрил тактику бота (-15 ИИ)!"
    elif bot_card.get("counters") == p_action_id:
        player_total -= 15
        kryptonite_msg = f" ❌ Бот прочитал тебя! Его '{bot_card['name']}' обнулил твою тактику (-15 тебе)!"
        
    # ХОККЕЙНЫЙ БОГ (Дисперсия)
    p_luck = random.randint(-8, 8)
    b_luck = random.randint(-8, 8)
    player_total += p_luck
    bot_total += b_luck
    
    # Определение результатов матча
    is_win = False
    if round_idx == 1:
        is_win = player_total > bot_total
        details = f"ГООЛ! Пробили защиту бота!" if is_win else "Сейв! Бот отразил атаку."
    elif round_idx == 2:
        is_win = player_total >= bot_total
        details = f"Ты отбился, атака бота захлебнулась!" if is_win else "Гол в твои ворота... Не удержали оборону."
    else:
        is_win = player_total > bot_total
        details = f"Победный бросок на вбрасывании!" if is_win else "Бот вырвал победу в раунде."
        
    details += kryptonite_msg
    
    return jsonify({
        "is_win": is_win,
        "details": details,
        "player_score": f"{player_total} (удача {p_luck:+d})",
        "bot_score": f"{bot_total} (удача {b_luck:+d})",
        "bot_setup": f"{bot_hockeyist['name']} [{bot_hockeyist['tier']}] + {bot_card['name']}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

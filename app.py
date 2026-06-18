import os
import random
from flask import Flask, jsonify, request, render_template

app = Flask(__name__, template_folder='templates')

# Расширенная база данных без дубликатов на старте
PLAYERS = {
    # Золото
    "mcdavid": {"name": "К. Макдэвид", "attack": 55, "defense": 20, "image": "⚡", "tier": "Золото", "type": "skater"},
    "kucherov": {"name": "Н. Кучеров", "attack": 52, "defense": 18, "image": "🪄", "tier": "Золото", "type": "skater"},
    "matthews": {"name": "О. Мэттьюс", "attack": 54, "defense": 22, "image": "🎯", "tier": "Золото", "type": "skater"},
    "mackinnon": {"name": "Н. Маккиннон", "attack": 53, "defense": 25, "image": "🚀", "tier": "Золото", "type": "skater"},
    "makar": {"name": "К. Макар", "attack": 30, "defense": 54, "image": "🏆", "tier": "Золото", "type": "skater"},
    "fox": {"name": "А. Фокс", "attack": 28, "defense": 50, "image": "🦊", "tier": "Золото", "type": "skater"},
    
    # Серебро
    "bedard": {"name": "К. Бедард", "attack": 44, "defense": 15, "image": "🦅", "tier": "Серебро", "type": "skater"},
    "pastrnak": {"name": "Д. Пастрняк", "attack": 46, "defense": 16, "image": "🍝", "tier": "Серебро", "type": "skater"},
    "panarin": {"name": "А. Панарин", "attack": 45, "defense": 14, "image": "🍞", "tier": "Серебро", "type": "skater"},
    "mintyukov": {"name": "П. Минтюков", "attack": 22, "defense": 42, "image": "🏒", "tier": "Серебро", "type": "skater"},
    "josi": {"name": "Р. Йоси", "attack": 24, "defense": 44, "image": "🇨🇭", "tier": "Серебро", "type": "skater"},
    
    # Бронза
    "michkov": {"name": "М. Мичков", "attack": 38, "defense": 12, "image": "🔥", "tier": "Бронза", "type": "skater"},
    "celebrini": {"name": "М. Челебрини", "attack": 36, "defense": 11, "image": "👶", "tier": "Бронза", "type": "skater"},
    "fantilli": {"name": "А. Фантилли", "attack": 35, "defense": 13, "image": "🍁", "tier": "Бронза", "type": "skater"},
    "levshunov": {"name": "А. Левшунов", "attack": 16, "defense": 35, "image": "🧱", "tier": "Бронза", "type": "skater"},
    "nikishin": {"name": "А. Никишин", "attack": 18, "defense": 36, "image": "🐻", "tier": "Бронза", "type": "skater"},

    # ВРАТАРИ
    "vasilevskiy": {"name": "А. Василевский", "save": 48, "image": "🧱", "tier": "Золото", "type": "goalie"},
    "shesterkin": {"name": "И. Шестеркин", "save": 46, "image": "🛡️", "tier": "Золото", "type": "goalie"},
    "bobrovsky": {"name": "С. Бобровский", "save": 40, "image": "🙅‍♂️", "tier": "Серебро", "type": "goalie"}
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
    if roll < 0.20: target_tier = "Золото"
    elif roll < 0.60: target_tier = "Серебро"
    else: target_tier = "Бронза"
        
    eligible_items = [k for k, v in PLAYERS.items() if v["tier"] == target_tier]
    dropped_id = random.choice(eligible_items if eligible_items else list(PLAYERS.keys()))
    dropped_card_id = random.choice(list(ACTION_CARDS.keys()))
    
    return jsonify({
        "player": {"id": dropped_id, "data": PLAYERS[dropped_id]},
        "card": {"id": dropped_card_id, "data": ACTION_CARDS[dropped_card_id]}
    })

@app.route('/play', methods=['POST'])
def play_round():
    data = request.json
    player_id = data.get('player_id')
    goalie_id = data.get('goalie_id', 'bobrovsky')
    p_action_id = data.get('action_id')
    round_idx = int(data.get('round_idx'))
    
    p_hockeyist = PLAYERS[player_id]
    p_goalie = PLAYERS[goalie_id]
    p_card = ACTION_CARDS[p_action_id]
    
    # ИИ выбирает случайного полевого и случайного вратаря
    bot_skaters = [k for k, v in PLAYERS.items() if v["type"] == "skater"]
    bot_goalies = [k for k, v in PLAYERS.items() if v["type"] == "goalie"]
    bot_hockeyist = PLAYERS[random.choice(bot_skaters)]
    bot_goalie = PLAYERS[random.choice(bot_goalies)]
    
    # Умный подбор карт для ИИ под раунд
    if round_idx == 1: 
        bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "defense"])
    elif round_idx == 2: 
        bot_card_id = random.choice([k for k, v in ACTION_CARDS.items() if v["type"] == "attack"])
    else: 
        bot_card_id = random.choice(list(ACTION_CARDS.keys()))
        
    bot_card = ACTION_CARDS[bot_card_id]
    
    # Расчет базовых очков
    p_base = p_hockeyist["attack"] if p_card["type"] == "attack" else p_hockeyist["defense"]
    bot_base = bot_hockeyist["attack"] if bot_card["type"] == "attack" else bot_hockeyist["defense"]
    
    player_total = p_base + p_card["value"]
    bot_total = bot_base + bot_card["value"]
    
    # Тактические контр-пики (-30 очков)
    kryptonite_msg = ""
    if p_card.get("beats") == bot_card_id:
        bot_total -= 30
        kryptonite_msg = " 🎯 Тактический разгром (-30 очков ИИ)!"
    elif bot_card.get("beats") == p_action_id:
        player_total -= 30
        kryptonite_msg = " ❌ Твоя тактика полностью прочитана (-30 очков тебе)!"
        
    # Рандомный фактор
    player_total += random.randint(-4, 4)
    bot_total += random.randint(-4, 4)
    
    is_goal = False
    goal_cancelled_by_goalie = False
    log_details = ""

    # ЛОГИКА ХОККЕЙНЫХ РАУНДОВ
    if round_idx == 1:  # Твоя Атака против Защиты ИИ
        if player_total > bot_total:
            # Защита ИИ пробита! Но у вратаря ИИ есть шанс на спасение (сейв)
            goalie_roll = bot_goalie["save"] + random.randint(-5, 5)
            if goalie_roll >= player_total:
                is_goal = False
                goal_cancelled_by_goalie = True
                log_details = f"Сейв спасения! Твой визави пробил защиту, но вратарь ИИ ({bot_goalie['name']}) вытащил шайбу щитком!"
            else:
                is_goal = True
                log_details = f"ГОООЛ! Оборона ИИ разорвана в клочья, вратарь бессилен!"
        else:
            is_goal = False
            log_details = "Атака увязла в оборонительных порядках ИИ."

    elif round_idx == 2:  # Атака ИИ против твоей Защиты
        if bot_total > player_total:
            # Твоя защита пробита. Твой вратарь пробует спасти положение
            my_goalie_roll = p_goalie["save"] + random.randint(-5, 5)
            if my_goalie_roll >= bot_total:
                is_goal = False
                log_details = f"Фантастический сейв! Твой вратарь ({p_goalie['name']}) выручает команду после провала защиты!"
            else:
                is_goal = True
                log_details = f"Гол в твои ворота! Нападающие ИИ развели защиту и вратаря."
        else:
            is_goal = False
            log_details = "Твои защитники намертво зацементировали подступы к воротам."

    else:  # Вбрасывание (Не дает голов напрямую!)
        if player_total > bot_total:
            log_details = "Выиграно вбрасывание! Твоя команда захватила контроль над игрой."
        elif player_total < bot_total:
            log_details = "ИИ выиграл вбрасывание и контролирует темп."
        else:
            log_details = "Судья просит переиграть вбрасывание — жесткая ничья на точке."

    if kryptonite_msg:
        log_details += f" ({kryptonite_msg})"

    return jsonify({
        "round_type": round_idx,
        "is_goal": is_goal,
        "details": log_details,
        "player_total": player_total,
        "bot_total": bot_total,
        "bot_setup": f"{bot_hockeyist['name']} + {bot_card['name']} (Вр: {bot_goalie['name']})"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

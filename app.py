import os
from flask import Flask, jsonify, request
import random

app = Flask(__name__)

# Наша мини-база данных (пока прямо в коде для простоты)
CARDS = {
    "defense": [
        {"id": "hedman_block", "name": "Блок Хедмана", "power": 35},
        {"id": "hook", "name": "Зацеп крюком", "power": 25},
        {"id": "wall", "name": "Глухая оборона", "power": 40}
    ]
}

# Тестовая страница, чтобы убедиться, что сервер жив
@app.route('/')
def home():
    return "Ледовая арена готова! Сервер НХЛ запущен."

# API-точка для розыгрыша дуэли
@app.route('/play', methods=['POST'])
def play_duel():
    # Получаем данные от игрока (какую карту он разыграл)
    data = request.json
    player_card_name = data.get('card_name', 'Обычный бросок')
    player_card_power = data.get('power', 0)
    
    # Бот (ИИ) достает случайную карту защиты
    bot_card = random.choice(CARDS["defense"])
    
    # Математика дуэли
    if player_card_power > bot_card["power"]:
        match_result = "ГОЛ! Твоя атака прошила оборону."
    elif player_card_power < bot_card["power"]:
        match_result = "СЕЙВ / БЛОК! Защита оказалась сильнее."
    else:
        match_result = "НИЧЬЯ! Жесткая борьба у бортика, шайба ничья."
        
    # Возвращаем ответ в формате JSON
    return jsonify({
        "your_attack": player_card_name,
        "your_power": player_card_power,
        "bot_defense": bot_card["name"],
        "bot_power": bot_card["power"],
        "result": match_result
    })

if __name__ == '__main__':
    # Настройки для запуска на сервере
    app.run(host='0.0.0.0', port=10000)

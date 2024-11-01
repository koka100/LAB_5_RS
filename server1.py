from flask import Flask, request, jsonify
import requests
import subprocess
import threading
import time

app = Flask(__name__)

# Список URL серверов для пересылки запросов
server_urls = []
max_servers = 5  # Максимальное количество серверов для запуска
min_servers = 1  # Минимальное количество серверов для запуска
load_threshold = 10  # Порог нагрузки для масштабирования вверх/вниз
server_processes = []  # Список процессов серверов

@app.route('/api/data', methods=['POST'])
def handle_request():
    data = request.get_json()  # Получаем JSON данные из входящего запроса

    for url in server_urls:
        try:
            # Пересылаем запрос на сервер
            response = requests.post(f"{url}/api/data", json=data, verify=False)  # Установите verify=False для тестирования

            if response.status_code == 200:
                return response.json()  # Возвращаем ответ от сервера, если успешно
        except requests.exceptions.RequestException as e:
            print(f"Ошибка подключения к {url}: {e}")  # Логируем ошибку для отладки

    return {'error': 'Все серверы недоступны'}, 503  # Возвращаем ошибку, если все серверы не работают

@app.route('/register', methods=['POST'])
def register_server():
    server_url = request.json.get('url')
    if server_url not in server_urls:
        server_urls.append(server_url)
    return jsonify({'message': 'Сервер успешно зарегистрирован'}), 200

@app.route('/deregister', methods=['POST'])
def deregister_server():
    server_url = request.json.get('url')
    if server_url in server_urls:
        server_urls.remove(server_url)
    return jsonify({'message': 'Сервер успешно отключен'}), 200

def scale_servers():
    while True:
        current_load = get_current_load()  # Реализуйте эту функцию для получения текущей нагрузки
        if current_load > load_threshold and len(server_urls) < max_servers:
            start_new_server()
        elif current_load < load_threshold and len(server_urls) > min_servers:
            stop_last_server()
        time.sleep(5)  # Проверяем каждые 5 секунд

def start_new_server():
    # Запускаем новый процесс сервера
    process = subprocess.Popen(['python3', 'server.py'])
    server_processes.append(process)
    print("Запущен новый экземпляр сервера.")

def stop_last_server():
    if server_processes:
        process = server_processes.pop()
        process.terminate()  # Завершаем процесс сервера
        print("Серверный экземпляр остановлен.")

def get_current_load():
    # Заглушка для логики расчета нагрузки
    # Вы можете реализовать свою логику для определения текущей нагрузки
    return len(server_urls) * 5  # Пример: нагрузка на основе количества активных серверов

if __name__ == '__main__':
    threading.Thread(target=scale_servers, daemon=True).start()  # Запускаем поток масштабирования
    app.run(host='0.0.0.0', port=8000)  # Запускаем Flask приложение на всех интерфейсах

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('localhost', 8080))
sock.listen(5)
sock.setblocking(False)

players = dict()


def handle_data():
    while True:
        time.sleep(0.01)  # додаємо невелике затримання для зменшення навантаження

        to_remove = []
        player_data = {}

        # Обробка даних від усіх гравців
        for conn in list(players.keys()):
            try:
                data = conn.recv(32).decode().strip()
                if data and ',' in data:
                    players[conn] = data
                    x, y, r = map(int, data.split(','))
                    player_data[conn] = {'x': x, 'y': y, 'r': r}

            except:
                continue

        eliminated = []
        for conn1 in player_data:
            if conn1 in eliminated:
                continue

            p1 = player_data[conn1]
            for conn2 in player_data:
                if conn1 == conn2 or conn2 in eliminated:
                    continue

                p2 = player_data[conn2]
                dx = p1['x'] - p2['x']
                dy = p1['y'] - p2['y']
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < p1['r'] + p2['r'] and p1['r'] > p2['r'] * 1.1:
                    eliminated.append(conn2)
                    p1['r'] += int(p2['r'] * 0.5)
                    players[conn1] = f"{p1['x']},{p1['y']},{p1['r']}"
                    break

        # Надсилання повідомлення про програш для усунених гравців
        for conn in list(players.keys()):
            if conn in eliminated:
                try:
                    conn.send("LOSE".encode())
                except:
                    pass
                to_remove.append(conn)
                continue

            # Надсилання оновлених даних іншим гравцям
            try:
                packet = '|'.join([players[c] for c in players if c != conn and c not in eliminated]) + '|'
                conn.send(packet.encode())
            except:
                to_remove.append(conn)

        # Видалення з'єднаних гравців, які більше не активні
        for conn in to_remove:
            players.pop(conn, None)


# Запуск окремого потоку для обробки даних
Thread(target=handle_data, daemon=True).start()

print("SERVER is running...")

# Основний цикл прийому з'єднань
while True:
    try:
        conn, addr = sock.accept()
        players[conn] = "0,0,20"
        conn.send('0,0,20'.encode())
    except:
        pass

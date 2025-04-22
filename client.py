from math import hypot
from socket import socket, AF_INET, SOCK_STREAM
from pygame import *
from threading import Thread
from random import randint

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('5.tcp.eu.ngrok.io', 10321))
my_player = list(map(int, sock.recv(32).decode().strip('|').split(',')))
sock.setblocking(False)

init()
window = display.set_mode((1000, 1000))
clock = time.Clock()
all_players = []

f = font.Font(None, 50)


def receive_data():
    global all_players, running, lose
    last_good_data = []
    while running:
        try:
            data = sock.recv(4096).decode().strip()
            if data == "LOSE":
                lose = True
            elif data:
                parts = data.strip('|').split('|')
                parsed = [list(map(int, p.split(','))) for p in parts if len(p.split(',')) == 3]
                if parsed:
                    last_good_data = parsed
            all_players = last_good_data
        except:
            pass


class Eat:
    def __init__(self, x, y, r, c):
        self.x = x
        self.y = y
        self.radius = r
        self.color = c

    def check_collision(self, player_x, player_y, player_r):
        dx = self.x - player_x
        dy = self.y - player_y
        distance = hypot(dx, dy)
        return distance <= self.radius + player_r


eats = [Eat(randint(-2000, 2000), randint(-2000, 2000), 10,
            (randint(0, 255), randint(0, 255), randint(0, 255)))
        for _ in range(500)]

running = True
Thread(target=receive_data, daemon=True).start()
lose = False
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    window.fill((255, 255, 255))
    scale = 50 / my_player[2]
    scale = max(0.3, min(scale, 1.5))

    for p in all_players:
        screen_x = int((p[0] - my_player[0]) * scale + 500)
        screen_y = int((p[1] - my_player[1]) * scale + 500)
        draw.circle(window, (255, 0, 0), (screen_x, screen_y), int(p[2] * scale))

    draw.circle(window, (0, 255, 0), (500, 500), int(my_player[2] * scale))

    to_remove = []
    for eat in eats:
        if eat.check_collision(my_player[0], my_player[1], my_player[2]):
            to_remove.append(eat)
            my_player[2] += int(eat.radius * 0.2)
        else:
            screen_x = int((eat.x - my_player[0]) * scale + 500)
            screen_y = int((eat.y - my_player[1]) * scale + 500)
            draw.circle(window, eat.color, (screen_x, screen_y), int(eat.radius * scale))

    for eat in to_remove:
        eats.remove(eat)
    if lose:
        t = f.render('U lose!', 1, (244, 0, 0))
        window.blit(t, (500, 500))

    display.update()
    clock.tick(60)

    if not lose:
        keys = key.get_pressed()
        if keys[K_w]: my_player[1] -= 15
        if keys[K_s]: my_player[1] += 15
        if keys[K_a]: my_player[0] -= 15
        if keys[K_d]: my_player[0] += 15

        try:
            msg = f"{my_player[0]},{my_player[1]},{my_player[2]}"
            sock.send(msg.encode())
        except:
            pass

quit()

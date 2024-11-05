from sweeperlib import *
from random import randint
import datetime

l = open("records.txt", "a")
l.close()

def create_table():
    """
    Creates 2D list that will be used as a board
    """
    y = HEIGHT - 80
    while y >= 0:
        rows = []
        x = WIDTH - 40 - (WIDTH % 40) / 2
        while x >= 0:
            rows.append(" ")
            x -= 40
        TABLE.append(rows)
        y -= 40

def locate_square(x_find, y_find):
    """
    Finds a square based on x and y coordinates
    """
    ry = 0
    y5 = HEIGHT - 80
    while y5 / 40 >= 0:
        rx = 0
        x5 = WIDTH - 40 - ((WIDTH % 40) / 2)
        while x5 / 40 >= 0:
            if (x_find >= x5 and x_find < x5 + 40 and y_find >= y5 and y_find < y5 + 40) or (x_find == rx and y_find == ry):
                return x5, y5, rx, ry
            rx += 1
            x5 -= 40
        y5 -= 40
        ry += 1
    return None, None, None, None

def rand(number_of_mines):
    """
    Returns a list of randomly selected numbers from zero to 
    possible amount of squares on the frame
    """
    r = []
    while len(r) < number_of_mines:
        x = randint(0, int((WIDTH - 40 - (WIDTH % 40) / 2) / 40))
        y = randint(0, int((HEIGHT - 80) / 40))
        if (x, y) not in r:
            r.append((x, y))
    return r

def count_ninjas(x, y):
    """
    Counts the ninjas surrounding one tile in the given room and
    returns the result. The function assumes the selected tile does
    not have a ninja in it - if it does, it counts that one as well.
    """
    l1 = [y-1,y,y+1]
    l2 = [x-1,x,x+1]
    c = 0
    for i, j in enumerate(TABLE):
        for k, g in enumerate(j):
            if (k, i) in MINE_LOC:
                if i in l1 and k in l2:
                    c+=1
    return c

def open_surrounding(idx, idy):
    """
    This function recursively opens empty squares surrounding until
    it reaches squares that have mines adjacent to them.
    """
    if idx < 0 or idy < 0 or idy >= len(TABLE) or idx >= len(TABLE[0]):
        return

    if TABLE[idy][idx] != " ":
        return

    c = count_ninjas(idx, idy)

    if c > 0:
        TABLE[idy][idx] = c
    else:
        TABLE[idy][idx] = 0 

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    open_surrounding(idx + dx, idy + dy)

def apply(x, y, b):
    """
    Called when user clicks on a square
    """
    _, _, idx, idy = locate_square(x, y)
    if idx is not None and idy is not None:
        if b == MOUSE_RIGHT:
            TABLE[idy][idx] = "f"
        else:
            if (idx, idy) in MINE_LOC:
                TABLE[idy][idx] = "x"
                global game
                game = True
                set_mouse_handler(close_w)
            else:
                open_surrounding(idx, idy)

def won():
    c = 0
    for i, j in enumerate(TABLE):
        for k, g in enumerate(j):
            if g == " " and (k, i) not in MINE_LOC:
                c += 1
    return c

def game_over():
    global LEFT
    draw_text("GAME OVER", (WIDTH - 270) / 2, HEIGHT / 2, (255, 0, 0, 255), "Arial")
    l = 0
    for i, j in enumerate(TABLE):
        for k, g in enumerate(j):
            if (k, i) in MINE_LOC and g != "f":
                TABLE[i][k] = "x"
            if g == "x":
                l += 1
    LEFT = l

def timet(t):
    if not game and started:
        global TIME
        TIME += int(t)

def close_w(x, y, button, mods):
            close()

def prompt_input(m, f):
    """
        Prompts the user for an integer using the prompt parameter.
        If an invalid input is given, an error message is shown using
        the error message parameter. A valid input is returned as an
        integer.
    """
    if m == "NUMBER OF MINES: ":
        while True:
            r = input(m)
            try:
                t = float(r)
            except ValueError:
                print(f)
            else:
                if t % 1 != 0.0 or t <= 0:
                    print(f)
                else:
                    return int(r)
    while True:
        r = input(m)
        try:
            t = float(r)
        except ValueError:
            print(f)
        else:
            if t % 1 != 0.0 or t <= 100:
                print(f)
            else:
                return int(r)

WIDTH = 0
HEIGHT = 0
N_MINES = 0
TABLE = []
OPENED_S = [[], []]
ZEROS = []
game = False
started = False
TIME = 0
NAME = ""
MOVES = 0
LEFT = 0

def record():
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    with open("records.txt", "a") as t:
        t.write(f"{dt_string} {NAME} played {N_MINES} mines game {f'losing with {LEFT} mines left' if started else 'winning'} in {TIME / 60:.2f} minutes in {MOVES} moves\n")
    return

def hello():
    global WIDTH, HEIGHT, N_MINES, NAME, started
    print("MINESWEEPER")
    print("Hey, welcome to MINESWEEPER.")
    print("Choose what you want:")
    print("(P)lay the game")
    print("(V)iew statistics")
    print("(Q)uit")
    r = ""
    while True:
        r = input("Your choice: ")
        if r.lower() in ("p","v","q"):
            break
        else:
            print("You do not have that choice.")
    if r.lower() == "p":
        NAME = input("What is your name: ")
        WIDTH = prompt_input("WIDTH: ", "Give an integer greater than 100")
        HEIGHT = prompt_input("HEIGHT: ", "Give an integer greater than 100")
        N_MINES = prompt_input("NUMBER OF MINES: ", "Give an integer greater than 0")
        started = True
        load_sprites("sprites")
        create_window(WIDTH, HEIGHT)
        global MINE_LOC
        MINE_LOC = rand(N_MINES)
        create_table()
        def draw():
            clear_window()
            draw_background()
            begin_sprite_draw()
            for i, j in enumerate(TABLE):
                for k, g in enumerate(j):
                    new_x, new_y, _, _ = locate_square(k, i)
                    prepare_sprite(g, new_x, new_y)
            draw_sprites()
            draw_text(f"{TIME} seconds", WIDTH / 4, HEIGHT - 45, (0, 0, 255, 255), "Arial", 25)
            if won() == 0:
                draw_text("YOU WON", (WIDTH - 210) / 2, HEIGHT / 2, (255, 155, 0, 255), "Arial")
                global game, started
                started = False
                game = True
                set_mouse_handler(close_w)
            elif game:
                game_over()
                set_mouse_handler(close_w)
        def play(x, y, button, mods):
            _, _, x1, y1 = locate_square(x, y)
            if x1 is not None and y1 is not None:
                global MOVES
                MOVES += 1
                apply(x1, y1, button)

        set_interval_handler(timet, 1)
        set_draw_handler(draw)
        set_mouse_handler(play)

        start()
        record()
    elif r.lower() == "v":
        with open("records.txt", "r") as p:
            for k, i in enumerate(p.readlines()):
                print(f"{k+1} {i}")
    else:
        return
    
hello()
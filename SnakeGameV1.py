import tkinter as tk
from tkinter import messagebox
import random
import webbrowser
import os
import time

GAME_WIDTH = 600
GAME_HEIGHT = 400
SPACE_SIZE = 20
SCORES_FILE = "scores.txt"
SELECTED_SNAKE_COLOR = "#00FF00"
BG_COLOR = "#1e1e1e"
FOOD_COLOR = "#FF0000"

SETTINGS = {
    "snake_color": SELECTED_SNAKE_COLOR,
    "theme": "Dark",
    "mode": "Classic",
    "difficulty": "Normal",
    "player_name": "Player"
}

DIFFICULTY_SPEED = {
    "Easy": 150,
    "Normal": 100,
    "Hard": 70
}


def save_score(player, score):
    with open(SCORES_FILE, "a") as file:
        file.write(f"{player}:{score}\n")


def get_best_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    
    with open(SCORES_FILE, "r") as file:
        scores = []
        for line in file.readlines():
            parts = line.strip().split(":")
            if len(parts) == 2:
                name, score = parts
                if score.isdigit():
                    scores.append((name, int(score)))
    
    return sorted(scores, key=lambda x: x[1], reverse=True)[:10]


def clear_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "w"):
            pass


class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Snake Game")
        self.root.resizable(False, False)
        self.direction = 'down'
        self.running = False
        self.timer_mode = False
        self.start_time = None
        self.speed = DIFFICULTY_SPEED[SETTINGS['difficulty']]
        self.canvas = tk.Canvas(root, bg=BG_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
        self.canvas.pack(pady=10)
        self.score_label = tk.Label(root, text=f"Score: 0", font=("Consolas", 18), fg="lime", bg="#111")
        self.score_label.pack(pady=5)
        self.root.bind("<KeyPress>", self.change_direction)
        self.reset_game()

    def reset_game(self):
        self.direction = 'down'
        self.score = 0
        self.canvas.delete("all")
        self.snake = []
        self.snake_coords = []
        self.score_label.config(text=f"Score: 0")
        for i in range(3):
            self.snake_coords.append([0, 0])
            rect = self.canvas.create_rectangle(0, 0, SPACE_SIZE, SPACE_SIZE, fill=SETTINGS['snake_color'])
            self.snake.append(rect)
        self.create_food()
        self.running = True
        if SETTINGS['mode'] == "Timed":
            self.timer_mode = True
            self.start_time = time.time()
        self.next_turn()

    def create_food(self):
        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        self.food = self.canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR)

    def next_turn(self):
        if not self.running:
            return
        x, y = self.snake_coords[0]
        if self.direction == "up":
            y -= SPACE_SIZE
        elif self.direction == "down":
            y += SPACE_SIZE
        elif self.direction == "left":
            x -= SPACE_SIZE
        elif self.direction == "right":
            x += SPACE_SIZE

        if SETTINGS['mode'] == "No Walls":
            x %= GAME_WIDTH
            y %= GAME_HEIGHT

        self.snake_coords.insert(0, [x, y])
        rect = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SETTINGS['snake_color'])
        self.snake.insert(0, rect)

        if self.check_food_collision(x, y):
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.canvas.delete(self.food)
            self.create_food()
        else:
            del self.snake_coords[-1]
            self.canvas.delete(self.snake[-1])
            del self.snake[-1]

        if self.check_collisions(x, y):
            self.game_over()
        else:
            if self.timer_mode and time.time() - self.start_time >= 30:
                self.game_over()
            else:
                self.root.after(self.speed, self.next_turn)

    def check_food_collision(self, x, y):
        coords = self.canvas.coords(self.food)
        return coords[0] == x and coords[1] == y

    def check_collisions(self, x, y):
        if SETTINGS['mode'] != "No Walls":
            if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
                return True
        for part in self.snake_coords[1:]:
            if part == [x, y]:
                return True
        return False

    def change_direction(self, event):
        keys = {'Up': 'up', 'Down': 'down', 'Left': 'left', 'Right': 'right'}
        opposite = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
        if event.keysym in keys and keys[event.keysym] != opposite.get(self.direction):
            self.direction = keys[event.keysym]

    def game_over(self):
        self.running = False
        save_score(SETTINGS['player_name'], self.score)
        messagebox.showinfo("Game Over", f"Your score: {self.score}")
        show_main_menu(self.root)


def show_main_menu(root):
    for widget in root.winfo_children():
        widget.destroy()

    def start_game():
        for widget in root.winfo_children():
            widget.destroy()
        SnakeGame(root)

    def show_scores():
        win = tk.Toplevel(root)
        win.title("Best Scores")
        win.configure(bg="#202020")
        tk.Label(win, text="Top 10 Scores", font=("Arial", 16), fg="white", bg="#202020").pack(pady=10)
        scores = get_best_scores()
        for name, s in scores:
            tk.Label(win, text=f"{name}: {s}", font=("Consolas", 14), fg="lime", bg="#202020").pack()
        tk.Button(win, text="Clear Scores", bg="darkred", fg="white", command=lambda: [clear_scores(), win.destroy()]).pack(pady=10)

    def show_info():
        messagebox.showinfo("Info", "Snake Game with multiple features\nEat food, avoid crashing, and customize everything!")

    def open_github():
        webbrowser.open("https://github.com/CodePexV1")

    def show_settings():
        win = tk.Toplevel(root)
        win.title("Settings")
        win.geometry("400x400")
        tk.Label(win, text="Snake Color").pack()
        colors = ["Green", "Red", "Blue", "Yellow", "White", "Pink"]
        color_map = {
            "Green": "#00FF00",
            "Red": "#FF3333",
            "Blue": "#3399FF",
            "Yellow": "#FFFF33",
            "White": "#FFFFFF",
            "Pink": "#FF69B4"
        }
        color_var = tk.StringVar(value="Green")
        tk.OptionMenu(win, color_var, *colors).pack()

        tk.Label(win, text="Theme").pack()
        theme_var = tk.StringVar(value=SETTINGS['theme'])
        tk.OptionMenu(win, theme_var, "Dark", "Light", "Retro").pack()

        tk.Label(win, text="Game Mode").pack()
        mode_var = tk.StringVar(value=SETTINGS['mode'])
        tk.OptionMenu(win, mode_var, "Classic", "No Walls", "Timed").pack()

        tk.Label(win, text="Difficulty").pack()
        diff_var = tk.StringVar(value=SETTINGS['difficulty'])
        tk.OptionMenu(win, diff_var, "Easy", "Normal", "Hard").pack()

        tk.Label(win, text="Player Name").pack()
        name_entry = tk.Entry(win)
        name_entry.insert(0, SETTINGS['player_name'])
        name_entry.pack()

        def apply():
            SETTINGS['snake_color'] = color_map[color_var.get()]
            SETTINGS['theme'] = theme_var.get()
            SETTINGS['mode'] = mode_var.get()
            SETTINGS['difficulty'] = diff_var.get()
            SETTINGS['player_name'] = name_entry.get()
            messagebox.showinfo("Saved", "Settings updated!")
            win.destroy()

        tk.Button(win, text="Apply", command=apply, bg="lime", fg="black").pack(pady=10)

    frame = tk.Frame(root, bg="#181818")
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text="🐍 Snake Game", font=("Verdana", 26, "bold"), fg="lime", bg="#181818").pack(pady=30)

    btn_cfg = {"font": ("Arial", 16), "bg": "#2e2e2e", "fg": "white", "width": 20, "relief": "groove", "bd": 3}
    tk.Button(frame, text="▶ Play", command=start_game, **btn_cfg).pack(pady=8)
    tk.Button(frame, text="📊 Best Scores", command=show_scores, **btn_cfg).pack(pady=8)
    tk.Button(frame, text="ℹ Info", command=show_info, **btn_cfg).pack(pady=8)
    tk.Button(frame, text="⚙ Settings", command=show_settings, **btn_cfg).pack(pady=8)
    tk.Button(frame, text="🌐 GitHub", command=open_github, **btn_cfg).pack(pady=8)
    tk.Label(frame, text="Made By CodePex", bg="#181818", fg="gray").pack(side="bottom", pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + 100}")
    root.title("Snake Game")
    try:
        root.iconbitmap("snake.ico")
    except:
        pass
    show_main_menu(root)
    root.mainloop()

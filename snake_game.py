
import pygame
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import random
from pathlib import Path
import time
from pygame import mixer

# Initialize Pygame and mixer
pygame.init()
mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE                                                                                                                                                         
INITIAL_LENGTH = 5

# RGB Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)          
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             

# Custom theme colors
BACKGROUND_COLOR = (20, 20, 35)
SNAKE_HEAD_COLOR = (0, 255, 100)
SNAKE_BODY_COLOR = (0, 200, 80)                                                                                                                                             
FOOD_COLOR = (255, 50, 50)

def format_time(seconds):
    minutes = int(seconds // 60)         
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02d}"

def load_leaderboard():                      
    leaderboard_file = Path("leaderboard.json")     # storing file path in variable
    if not leaderboard_file.exists():               # checking if file already exists
        default_data = {                            # some default data
            "Ahmed": {"score": 150, "time": "2:45"},
            "Bilal": {"score": 120, "time": "2:10"},
            "Hamza": {"score": 100, "time": "1:55"}
        }
        with open(leaderboard_file, 'w') as f:      # write file
            json.dump(default_data, f)
    
    with open(leaderboard_file, 'r') as f:  # read file
        return json.load(f)

class Snake:
    def  __init__(self):
        self.length = INITIAL_LENGTH
        self.positions = [(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)]
        self.direction = random.choice([pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN])
        self.score = 0
        
        for i in range(self.length-1):
            if self.direction == pygame.K_RIGHT:
                self.positions.append((self.positions[-1][0]-GRID_SIZE, self.positions[-1][1]))
            elif self.direction == pygame.K_LEFT:
                self.positions.append((self.positions[-1][0]+GRID_SIZE, self.positions[-1][1]))
            elif self.direction == pygame.K_UP:
                self.positions.append((self.positions[-1][0], self.positions[-1][1]+GRID_SIZE))
            elif self.direction == pygame.K_DOWN:
                self.positions.append((self.positions[-1][0], self.positions[-1][1]-GRID_SIZE))

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = cur

        if self.direction == pygame.K_LEFT:
            x -= GRID_SIZE
        elif self.direction == pygame.K_RIGHT:
            x += GRID_SIZE
        elif self.direction == pygame.K_UP:
            y -= GRID_SIZE
        elif self.direction == pygame.K_DOWN:
            y += GRID_SIZE

        self.positions.insert(0, (x, y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def render(self, surface):
        for i, p in enumerate(self.positions):
            if i == 0:  # Head
                pygame.draw.rect(surface, SNAKE_HEAD_COLOR, 
                               pygame.Rect(p[0], p[1], GRID_SIZE-2, GRID_SIZE-2))
                # Draw eyes
                eye_color = BLACK
                if self.direction == pygame.K_RIGHT:
                    pygame.draw.circle(surface, eye_color, (p[0]+15, p[1]+5), 2)
                    pygame.draw.circle(surface, eye_color, (p[0]+15, p[1]+15), 2)
                elif self.direction == pygame.K_LEFT:
                    pygame.draw.circle(surface, eye_color, (p[0]+5, p[1]+5), 2)
                    pygame.draw.circle(surface, eye_color, (p[0]+5, p[1]+15), 2)
                elif self.direction == pygame.K_UP:
                    pygame.draw.circle(surface, eye_color, (p[0]+5, p[1]+5), 2)
                    pygame.draw.circle(surface, eye_color, (p[0]+15, p[1]+5), 2)
                elif self.direction == pygame.K_DOWN:
                    pygame.draw.circle(surface, eye_color, (p[0]+5, p[1]+15), 2)
                    pygame.draw.circle(surface, eye_color, (p[0]+15, p[1]+15), 2)
            else:  # Body
                color_intensity = 255 - (i * 5) if 255 - (i * 5) > 50 else 50
                body_color = (0, color_intensity, int(color_intensity * 0.8))
                pygame.draw.rect(surface, body_color,
                               pygame.Rect(p[0], p[1], GRID_SIZE-2, GRID_SIZE-2))

class Food:
    def  __init__(self):
        self.position = (0, 0)
        self.color = FOOD_COLOR
        self.glow_value = 0  # Initialize glow value
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1) * GRID_SIZE,
                         random.randint(0, GRID_HEIGHT-1) * GRID_SIZE)

    def update_glow(self):
        # Example logic to update glow value
        self.glow_value = (self.glow_value + 1) % 100  # Cycle the glow value

    def render_with_glow(self, surface):
        # Update glow effect
        self.update_glow()
        
        # Draw glow effect
        glow_radius = GRID_SIZE + self.glow_value // 10
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*FOOD_COLOR[:3], 100), 
                         (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, 
                    (self.position[0] + GRID_SIZE//2 - glow_radius,
                     self.position[1] + GRID_SIZE//2 - glow_radius))

        # Draw main food
        food_rect = pygame.Rect(self.position[0], self.position[1], 
                              GRID_SIZE-2, GRID_SIZE-2)
        pygame.draw.rect(surface, self.color, food_rect)
        
        # Draw shine effect
        shine_pos = (self.position[0] + GRID_SIZE//4, 
                    self.position[1] + GRID_SIZE//4)
        pygame.draw.circle(surface, (255, 255, 255), shine_pos, 2)

class MenuWindow:
    def  __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake Game")
        self.root.geometry("400x500")
        self.root.configure(bg='#2C3E50')
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, 
                         text="🐍 Snake Game 🐍", 
                         font=("Helvetica", 24, "bold"),
                         bg='#2C3E50',
                         fg='white')
        title.pack(pady=30)

        style = ttk.Style()
        style.configure('Custom.TButton', 
                        font=('Helvetica', 12),
                        padding=10,
                        width=20)

        play_btn = ttk.Button(self.root, 
                              text="Play Game",
                              style='Custom.TButton',
                              command=self.play_game)
        play_btn.pack(pady=10)

        leaderboard_btn = ttk.Button(self.root,
                                      text="Leaderboard",
                                      style='Custom.TButton',
                                      command=self.show_leaderboard)
        leaderboard_btn.pack(pady=10)

        instructions_btn = ttk.Button(self.root,
                                       text="How to Play",
                                       style='Custom.TButton',
                                       command=self.show_instructions)
        instructions_btn.pack(pady=10)

        quit_btn = ttk.Button(self.root,
                              text="Quit",
                              style='Custom.TButton',
                              command=self.root.quit)
        quit_btn.pack(pady=10)

    def show_instructions(self):
        instructions = """
        How to Play:
        
        🎮 Controls:
        • Use Arrow Keys to change direction
        • ESC to pause/quit
        
        🎯 Objectives:
        • Eat food to grow longer
        • Avoid hitting walls
        • Avoid hitting yourself
        • Try to get the highest score!
        
        🏆 Scoring:
        • Each food item: +10 points
        • Time bonus: Faster completion = Better score!
        
        Good Luck! 🍀
        """
        messagebox.showinfo("How to Play", instructions)

    def show_leaderboard(self):
        self.root.withdraw()
        display_leaderboard()
        self.root.deiconify()

    def play_game(self):
        self.root.withdraw()  # Hide the main menu window
        score, time_taken = self.run_game()  # Run the game and get the score and time
        self.root.deiconify()  # Show the main menu window again
        
        # Create a temporary root window for the dialog
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the temporary root window
        
        # Get player name
        player_name = simpledialog.askstring("Game Over", 
                                           f"Your score: {score}\nTime: {time_taken}\nEnter your name:",
                                           parent=temp_root)
        
        temp_root.destroy()  # Destroy the temporary root window
        
        # Show leaderboard with the new score
        display_leaderboard(score, time_taken, player_name)

    def run_game(self):
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Snake Game')
        clock = pygame.time.Clock()
        
        snake = Snake()
        food = Food()
        
        running = True
        paused = False
        start_time = time.time()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                    elif not paused:
                        if event.key == pygame.K_LEFT and snake.direction != pygame.K_RIGHT:
                            snake.direction = pygame.K_LEFT
                        elif event.key == pygame.K_RIGHT and snake.direction != pygame.K_LEFT:
                            snake.direction = pygame.K_RIGHT
                        elif event.key == pygame.K_UP and snake.direction != pygame.K_DOWN:
                            snake.direction = pygame.K_UP
                        elif event.key == pygame.K_DOWN and snake.direction != pygame.K_UP:
                            snake.direction = pygame.K_DOWN

            if not paused:
                snake.update()

                if snake.get_head_position() == food.position:
                    snake.length += 1
                    snake.score += 10
                    food.randomize_position()

                head_pos = snake.get_head_position()
                if (head_pos[0] < 0 or head_pos[0] >= WINDOW_WIDTH or
                    head_pos[1] < 0 or head_pos[1] >= WINDOW_HEIGHT or
                    head_pos in snake.positions[1:]):
                    running = False
                    # Move the player name input and leaderboard display here
                    self.root.deiconify()  # Show the main menu window again
                    temp_root = tk.Tk()
                    temp_root.withdraw()  # Hide the temporary root window
                    
                    # Get player name
                    player_name = simpledialog.askstring("Game Over", 
                                                       f"Your score: {snake.score}\nTime: {format_time(time.time() - start_time)}\nEnter your name:",
                                                       parent=temp_root)
                    
                    temp_root.destroy()  # Destroy the temporary root window
                    
                    # Show leaderboard with the new score
                    display_leaderboard(snake.score, format_time(time.time() - start_time), player_name)
                    return  # Exit the run_game method

            screen.fill(BACKGROUND_COLOR)
            
            for x in range(0, WINDOW_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, WINDOW_HEIGHT))
            for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, (40, 40, 40), (0, y), (WINDOW_WIDTH, y))
            
            snake.render(screen)
            food.render_with_glow(screen)

            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Score: {snake.score}', True, WHITE)
            time_text = font.render(f'Time: {format_time(time.time() - start_time)}', True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(time_text, (10, 40))

            if paused:
                pause_text = font.render('PAUSED', True, WHITE)
                screen.blit(pause_text, (WINDOW_WIDTH//2 - pause_text.get_width()//2,
                                       WINDOW_HEIGHT//2))

            pygame.display.flip()
            clock.tick(10)

        end_time = time.time() - start_time
        pygame.quit()
        return snake.score, format_time(end_time)

def display_leaderboard(final_score=None, time_taken=None, player_name=None):
    leaderboard = load_leaderboard()
    
    # If there's a new score and player name, add it to the leaderboard
    if final_score is not None and player_name is not None:
        leaderboard[player_name] = {"score": final_score, "time": time_taken}
        with open("leaderboard.json", 'w') as f:
            json.dump(leaderboard, f)

    leaderboard_window = tk.Tk()
    leaderboard_window.title("Leaderboard")
    leaderboard_window.geometry("400x500")
    leaderboard_window.configure(bg='#2C3E50')

    sorted_scores = sorted(leaderboard.items(), 
                           key=lambda x: x[1]["score"], 
                           reverse=True)

    tk.Label(leaderboard_window, 
             text="🏆 Leaderboard 🏆",
             font=("Helvetica", 20, "bold"),
             bg='#2C3E50',
             fg='white').pack(pady=20)

    table_frame = tk.Frame(leaderboard_window, bg='#2C3E50')
    table_frame.pack(padx=20, pady=10)

    headers = ["Rank", "Name", "Score", "Time"]
    for col, header in enumerate(headers):
        tk.Label(table_frame,
                 text=header,
                 font=("Helvetica", 12, "bold"),
                 bg='#2C3E50',
                 fg='white',
                 width=10).grid(row=0, column=col, padx=5, pady=5)

    for idx, (name, data) in enumerate(sorted_scores[:10], 1):
        rank_color = 'gold' if idx == 1 else 'silver' if idx == 2 else 'orange' if idx == 3 else 'white'
        tk.Label(table_frame,
                 text=f"#{idx}",
                 font=("Helvetica", 11),
                 bg='#2C3E50',
                 fg=rank_color).grid(row=idx, column=0, padx=5, pady=3)
        
        tk.Label(table_frame,
                 text=name,
                 font=("Helvetica", 11),
                 bg='#2C3E50',
                 fg='white').grid(row=idx, column=1, padx=5, pady=3)
        
        tk.Label(table_frame,
                 text=str(data["score"]),
                 font=("Helvetica", 11),
                 bg='#2C3E50',
                 fg='white').grid(row=idx, column=2, padx=5, pady=3)
        
        tk.Label(table_frame,
                 text=data["time"],
                 font=("Helvetica", 11),
                 bg='#2C3E50',
                 fg='white').grid(row=idx, column=3, padx=5, pady=3)

    button_frame = tk.Frame(leaderboard_window, bg='#2C3E50')
    button_frame.pack(pady=20)

    def play_again():
        leaderboard_window.destroy()
        MenuWindow().play_game()

    tk.Button(button_frame,
              text="Play Again",
              font=("Helvetica", 12),
              command=play_again).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame,
              text="Quit",
              font=("Helvetica", 12),
              command=lambda: [leaderboard_window.destroy(), quit()]).pack(side=tk.LEFT, padx=10)

    leaderboard_window.mainloop()

if __name__ == "__main__":
    game = MenuWindow()
    game.root.mainloop()

    leaderboard_window.mainloop() # type: ignore

if __name__ == "__main__":
    game = MenuWindow()
    game.root.mainloop()
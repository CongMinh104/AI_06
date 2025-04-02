
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import math
import random
from collections import defaultdict
import time

class GameTreeNode:
    #Represents a node in the game tree
    def __init__(self, parent, current_number, move, player_type):
        self.parent = parent
        self.current_number = current_number
        self.move = move
        self.player_type = player_type
        self.children = []
    #Function that adds child into the already generated node
    def add_child(self, child):
        self.children.append(child)

class GameTree:
    def __init__(self):
        self.root = None
    def insert_node(self, parent, current_number, move, player_type):
        new_node = GameTreeNode(parent, current_number, move, player_type)
        if parent is None:
            self.root = new_node
        else:
            parent.add_child(new_node)
        return new_node

class Game:
    def __init__(self, master):
        self.master = master
        self.master.title("Multiplication Game")
        self.master.geometry("900x750")
        self.master.configure(bg="#561C24")

        #function that initialize the game tree
        self.game_tree = GameTree()
        self.current_node = None

        # Game statistics
        self.game_stats = {
            'games_played': 0,
            'human_wins': 0,
            'computer_wins': 0,
            'move_frequency': defaultdict(int)
        }
        """
        This part is mostly UI
        """
        #Function to load images into the game, extra things. 
        try:
            self.win_image = ImageTk.PhotoImage(Image.open('C://Users//anugr//Downloads//Win.jpg'))
        except Exception as e:
            print(f"Error loading win image: {e}")
            self.win_image = None

        try:
            self.lose_image = ImageTk.PhotoImage(Image.open('C://Users//anugr//Downloads//Lose.jpg'))
        except Exception as e:
            print(f"Error loading lose image: {e}")
            self.lose_image = None

        try:
           self.draw_image = ImageTk.PhotoImage(Image.open('C://Users//anugr//Downloads//Draw.jpg'))
        except Exception as e:
            print(f"Error loading draw image: {e}")
            self.draw_image = None

        self.starting_number = None
        self.current_number = None
        self.player_score = 0
        self.computer_score = 0
        self.first_player = None
        self.move_history = []
        self.computation_time = 0

        
        custom_font = font.Font(family="Helvetica", size=12, weight="bold")


        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        for i in range(12):
            self.master.grid_rowconfigure(i, weight=1)

        # Label for starting number input
        self.label = tk.Label(master, text="Choose a starting number (8-18):", bg="#E8D8C4", fg="#561C24", font=custom_font)
        self.label.grid(row=0, column=0, columnspan=3, pady=(20, 10))

        # Entry for starting number
        self.entry = tk.Entry(master, font=custom_font, bg="#ffffff", fg="#1e1e2f", borderwidth=2, relief="flat")
        self.entry.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        # Label for choosing who plays first
        self.first_player_label = tk.Label(master, text="Who should play first?", bg="#E8D8C4", fg="#561C24", font=custom_font)
        self.first_player_label.grid(row=2, column=0, columnspan=3, pady=(10, 5))


        self.player_first_button = tk.Button(master, text="Player First", bg="#A0522D", fg="white", font=custom_font, 
                                           command=lambda: self.set_first_player("player"), relief="flat", bd=0, 
                                           activebackground="#6aa8ff", activeforeground="white")
        self.player_first_button.grid(row=3, column=0, padx=10, pady=(0, 10))

        self.computer_first_button = tk.Button(master, text="Computer First", bg="#A0522D", fg="white", font=custom_font, 
                                            command=lambda: self.set_first_player("computer"), relief="flat", bd=0, 
                                            activebackground="#6aa8ff", activeforeground="white")
        self.computer_first_button.grid(row=3, column=2, padx=10, pady=(0, 10))

        # This to enables which algorithm can players choose visually.
        self.algorithm_var = tk.StringVar(value="Alpha-Beta")
        self.algorithm_menu = tk.OptionMenu(master, self.algorithm_var, "Alpha-Beta", "Minimax")
        self.algorithm_menu.config(bg="#A0522D", fg="white", font=custom_font, relief="flat", 
                                 activebackground="#6E3B2D", activeforeground="white")
        self.algorithm_menu["menu"].config(bg="#E8D8C4", fg="#561C24", font=custom_font, 
                                         activebackground="#C7B8A5", activeforeground="#561C24")
        self.algorithm_menu.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        self.algorithm_var.trace("w", self.update_algorithm_display)

        # Make button to start the game
        self.start_button = tk.Button(master, text="Start Game", bg="#50c878", fg="white", font=custom_font, 
                                     command=self.start_game, relief="flat", bd=0, 
                                     activebackground="#70e89e", activeforeground="white")
        self.start_button.grid(row=6, column=0, columnspan=3, pady=(10, 20))

  
        self.multiplier_label = tk.Label(master, text="", bg="white", fg="#561C24", font=custom_font)
        self.multiplier_label.grid(row=7, column=0, columnspan=3, pady=(0, 10))


        self.multiplier_buttons = []
        multipliers = [2, 3, 4]
        for i, multiplier in enumerate(multipliers):
            button = tk.Button(master, text=f"×{multiplier}", bg="#A0522D", fg="white", font=custom_font, 
                              command=lambda x=multiplier: self.player_turn(x), relief="flat", bd=0, 
                              activebackground="#ff8f81", activeforeground="white")
            button.grid(row=8, column=i, padx=10, pady=(0, 20))
            self.multiplier_buttons.append(button)

        # Label for results and current number
        self.result_label = tk.Label(master, text="", bg="white", fg="#561C24", font=custom_font, wraplength=350)
        self.result_label.grid(row=9, column=0, columnspan=3, pady=(0, 10))

        # Label for scores
        self.score_label = tk.Label(master, text="", bg="white", fg="#561C24", font=custom_font)
        self.score_label.grid(row=10, column=0, columnspan=3, pady=(0, 10))

        # Label for computation time
        self.time_label = tk.Label(master, text="AI Computation Time: 0.000s (Alpha-Beta)", bg="#E8D8C4", fg="#561C24", font=custom_font)
        self.time_label.grid(row=9, column=3, rowspan=2, padx=10, pady=(0, 10), sticky="n")

        # Label for move history
        self.history_label = tk.Label(master, text="Move History:", bg="white", fg="#561C24", font=custom_font)
        self.history_label.grid(row=11, column=0, columnspan=3, pady=(0, 10))

        # Text widget to display move history
        self.history_text = tk.Text(master, height=5, width=50, bg="white", fg="#561C24", font=custom_font, wrap=tk.WORD)
        self.history_text.grid(row=12, column=0, columnspan=3, pady=(0, 10))

        # Button to reset the game
        self.reset_button = tk.Button(master, text="Reset", bg="#ff4757", fg="white", font=custom_font, 
                                     command=self.reset_game, relief="flat", bd=0, 
                                     activebackground="#ff6b81", activeforeground="white")
        self.reset_button.grid(row=13, column=0, columnspan=3, pady=(0, 20))
        self.reset_button.config(state=tk.DISABLED)
    """
    End of UI configuration part here.
    """
    #this function is to update for the game which algorithm was chosen
    def update_algorithm_display(self, *args):

        selected = self.algorithm_var.get()
        self.time_label.config(text=f"AI Computation Time: {self.computation_time:.3f}s ({selected})")
        
    #to choose who plays first
    def set_first_player(self, player):
 
        self.first_player = player
        self.player_first_button.config(state=tk.DISABLED)
        self.computer_first_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        
    #initialize the starting of our game
    def start_game(self):
        try:
            self.starting_number = int(self.entry.get())
            if 8 <= self.starting_number <= 18:
                self.current_number = self.starting_number
                self.player_score = 0
                self.computer_score = 0
                self.move_history = []
                self.computation_time = 0
                self.update_score()
                self.result_label.config(text=f"Current number: {self.current_number}")
                self.multiplier_label.config(text="Choose a multiplier:")
                self.reset_button.config(state=tk.NORMAL)
                for button in self.multiplier_buttons:
                    button.config(state=tk.NORMAL)

                self.current_node = self.game_tree.insert_node(None, self.current_number, None, None)

                if self.first_player == "computer":
                    self.master.after(1000, self.computer_turn)
            else:
                self.result_label.config(text="Please choose a number between 8 and 18.")
        except ValueError:
            self.result_label.config(text="Invalid input. Please enter a valid integer.")

    def player_turn(self, multiplier):
        if self.current_number is not None:
            self.current_number *= multiplier
            self.result_label.config(text=f"You multiplied by {multiplier}. Current number: {self.current_number}")
            self.update_scores("player")
            self.check_number()

            self.move_history.append(f"Player ×{multiplier} → {self.current_number}")
            self.update_history()

            self.current_node = self.game_tree.insert_node(self.current_node, self.current_number, multiplier, "player")

            if self.current_number < 1200:
                self.master.after(1000, self.computer_turn)

    def computer_turn(self):
        if self.current_number < 1200:
            start_time = time.time()
            best_move = self.find_best_move()
            end_time = time.time()
            self.computation_time = end_time - start_time
            algorithm = self.algorithm_var.get()
            self.time_label.config(text=f"AI Computation Time: {self.computation_time:.3f}s ({algorithm})")
            
            self.current_number *= best_move
            self.result_label.config(text=f"Computer multiplied by {best_move}. Current number: {self.current_number}")
            self.update_scores("computer")
            self.check_number()

            self.move_history.append(f"Computer ×{best_move} → {self.current_number}")
            self.update_history()

            self.current_node = self.game_tree.insert_node(self.current_node, self.current_number, best_move, "computer")

    def find_best_move(self):
        if self.algorithm_var.get() == "Minimax":
            return self.find_best_move_minimax()
        else:
            return self.find_best_move_alpha_beta()

    def find_best_move_alpha_beta(self):
        possible_moves = [2, 3, 4]
        best_score = -math.inf
        best_move = None
        
        for move in possible_moves:
            new_number = self.current_number * move
            score = self.alpha_beta(new_number, depth=4, alpha=-math.inf, beta=math.inf, is_maximizing=False)
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move if best_move is not None else random.choice(possible_moves)

    def find_best_move_minimax(self):
        """Minimax implementation."""
        possible_moves = [2, 3, 4]
        best_score = -math.inf
        best_move = None
        
        for move in possible_moves:
            new_number = self.current_number * move
            score = self.minimax(new_number, depth=4, is_maximizing=False)
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move if best_move is not None else random.choice(possible_moves)

    def alpha_beta(self, number, depth, alpha, beta, is_maximizing):
        if number >= 1200:
            return 1 if not is_maximizing else -1
            
        if depth == 0:
            return self.evaluate(number)
            
        possible_moves = [2, 3, 4]
        
        if is_maximizing:
            max_eval = -math.inf
            for move in possible_moves:
                new_number = number * move
                eval = self.alpha_beta(new_number, depth-1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            for move in possible_moves:
                new_number = number * move
                eval = self.alpha_beta(new_number, depth-1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def minimax(self, number, depth, is_maximizing):
        """Minimax algorithm implementation."""
        if number >= 1200:
            return 1 if not is_maximizing else -1
            
        if depth == 0:
            return self.evaluate(number)
            
        possible_moves = [2, 3, 4]
        
        if is_maximizing:
            #maximizing player (Computer), highest heuristic value is considered and selected 
            max_eval = -math.inf
            for move in possible_moves:
                new_number = number * move
                eval = self.minimax(new_number, depth-1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            #minimizing player(player), this function will search for nodes with lowest heuristic value
            min_eval = math.inf
            for move in possible_moves:
                new_number = number * move
                eval = self.minimax(new_number, depth-1, True)
                min_eval = min(min_eval, eval)
            return min_eval

    def evaluate(self, number):
        if number >= 1200:
            return 1 if number % 2 == 1 else -1
        
        # 1. Odd number advantage (primary factor)
        odd_bonus = 0.4 if number % 2 == 1 else -0.3
        
        # 2. Strategic positions near powers of 2
        next_power = 2 ** (math.floor(math.log2(number)) + 1)
        strategic_bonus = 0.3 if (next_power - number) <= 4 else 0
        
        # 3. Progress toward 1200
        progress_score = min(number / 1200, 1) * 0.2
        
        # 4. Opponent threat detection
        threat_penalty = -0.4 if any(number*m >= 1200 for m in [2,3,4]) else 0
        
        return odd_bonus + strategic_bonus + progress_score + threat_penalty

    def update_scores(self, player_type):
        """Update scores based on the resulting number."""
        if self.current_number % 2 == 0:
            if player_type == "player":
                self.computer_score -= 1
                points_info = f"Computer loses 1 point. (Number: {self.current_number} is even)"
            else:
                self.player_score -= 1
                points_info = f"You lose 1 point. (Number: {self.current_number} is even)"
        else:
            if player_type == "player":
                self.player_score += 1
                points_info = f"You gain 1 point. (Number: {self.current_number} is odd)"
            else:
                self.computer_score += 1
                points_info = f"Computer gains 1 point. (Number: {self.current_number} is odd)"

        self.result_label.config(text=f"{self.result_label.cget('text')}\n{points_info}")
        self.update_score()

    def check_number(self):
        """Check if the game has ended."""
        if self.current_number >= 1200:
            self.end_game()

    def update_score(self):
        """Update the score display."""
        self.score_label.config(text=f"Your Score: {self.player_score} | Computer Score: {self.computer_score}")

    def update_history(self):
        """Update the move history display."""
        self.history_text.delete(1.0, tk.END)
        for move in self.move_history:
            self.history_text.insert(tk.END, move + "\n")

    def end_game(self):
        """End the game and display the result."""
        for button in self.multiplier_buttons:
            button.config(state=tk.DISABLED)

        # Update game statistics
        self.game_stats['games_played'] += 1
        if self.player_score > self.computer_score:
            result_text = "Game Over! You win!"
            self.game_stats['human_wins'] += 1
            if self.win_image:
                self.result_label.config(image=self.win_image, compound="top")
        elif self.computer_score > self.player_score:
            result_text = "Game Over! Computer wins!"
            self.game_stats['computer_wins'] += 1
            if self.lose_image:
                self.result_label.config(image=self.lose_image, compound="top")
        else:
            result_text = "Game Over! It's a draw!"
            if self.draw_image:
                self.result_label.config(image=self.draw_image, compound="top")
            else:
                self.result_label.config(image="")

        self.result_label.config(text=f"{result_text}\nFinal Number: {self.current_number}\nFinal Scores - You: {self.player_score}, Computer: {self.computer_score}")

    def reset_game(self):
        self.starting_number = None
        self.current_number = None
        self.player_score = 0
        self.computer_score = 0
        self.first_player = None
        self.move_history = []
        self.computation_time = 0
        self.time_label.config(text="AI Computation Time: 0.000s (Alpha-Beta)")
        self.result_label.config(text="", image="")
        self.score_label.config(text="")
        self.multiplier_label.config(text="")
        self.history_text.delete(1.0, tk.END)
        self.entry.delete(0, tk.END)
        self.reset_button.config(state=tk.DISABLED)
        self.player_first_button.config(state=tk.NORMAL)
        self.computer_first_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        for button in self.multiplier_buttons:
            button.config(state=tk.NORMAL)

 
        self.game_tree = GameTree()
        self.current_node = None

root = tk.Tk()
game = Game(root)
root.mainloop()







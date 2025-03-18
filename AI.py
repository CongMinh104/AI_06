import tkinter as tk
from tkinter import messagebox
import time
import random


class GameNode:
    def __init__(self, number, human_score, computer_score, is_human_turn):
        self.number = number
        self.human_score = human_score
        self.computer_score = computer_score
        self.is_human_turn = is_human_turn
        self.children = []


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiplication Game")

        self.start_number = tk.IntVar()
        self.current_number = 0
        self.human_score = 0
        self.computer_score = 0
        self.algorithm = tk.StringVar(value="Minimax")
        self.turn = tk.StringVar(value="human")
        self.nodes_visited = 0  # For experiment tracking
        self.move_times = []  # For experiment tracking

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Choose a starting number (8-18):").pack()
        tk.Entry(self.root, textvariable=self.start_number).pack()
        tk.Button(self.root, text="Start Game", command=self.start_game).pack()

        tk.Label(self.root, text="Choose Algorithm:").pack()
        tk.Radiobutton(self.root, text="Minimax", variable=self.algorithm, value="Minimax").pack()
        tk.Radiobutton(self.root, text="Alpha-Beta", variable=self.algorithm, value="Alpha-Beta").pack()

        tk.Label(self.root, text="Who starts the game?").pack()
        tk.Radiobutton(self.root, text="Human", variable=self.turn, value="human").pack()
        tk.Radiobutton(self.root, text="Computer", variable=self.turn, value="computer").pack()

        self.info_label = tk.Label(self.root, text="")
        self.info_label.pack()

        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack()

        for factor in [2, 3, 4]:
            tk.Button(self.buttons_frame, text=f"Multiply by {factor}",
                      command=lambda f=factor: self.play_turn(f)).pack(side=tk.LEFT)

    def generate_game_tree(self, node, depth):
        if depth == 0 or node.number >= 1200:
            return
        for factor in [2, 3, 4]:
            new_number = node.number * factor
            new_human_score = node.human_score
            new_computer_score = node.computer_score
            if new_number % 2 == 0:
                if node.is_human_turn:
                    new_computer_score -= 1
                else:
                    new_human_score -= 1
            else:
                if node.is_human_turn:
                    new_human_score += 1
                else:
                    new_computer_score += 1
            child = GameNode(new_number, new_human_score, new_computer_score, not node.is_human_turn)
            node.children.append(child)
            self.generate_game_tree(child, depth - 1)

    def evaluate_score(self, node):
        # Heuristic: score difference, favoring the current player
        return node.computer_score - node.human_score if not node.is_human_turn else node.human_score - node.computer_score

    def minimax(self, node, depth, max_depth, is_maximizing):
        self.nodes_visited += 1
        if depth == max_depth or node.number >= 1200:
            return self.evaluate_score(node)

        if is_maximizing:
            best_score = float('-inf')
            for child in node.children:
                score = self.minimax(child, depth + 1, max_depth, False)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for child in node.children:
                score = self.minimax(child, depth + 1, max_depth, True)
                best_score = min(best_score, score)
            return best_score

    def alpha_beta(self, node, depth, max_depth, alpha, beta, is_maximizing):
        self.nodes_visited += 1
        if depth == max_depth or node.number >= 1200:
            return self.evaluate_score(node)

        if is_maximizing:
            best_score = float('-inf')
            for child in node.children:
                score = self.alpha_beta(child, depth + 1, max_depth, alpha, beta, False)
                best_score = max(best_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = float('inf')
            for child in node.children:
                score = self.alpha_beta(child, depth + 1, max_depth, alpha, beta, True)
                best_score = min(best_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return best_score

    def start_game(self):
        self.current_number = self.start_number.get()
        if not (8 <= self.current_number <= 18):
            messagebox.showerror("Error", "Choose a number between 8 and 18")
            return
        self.human_score = 0
        self.computer_score = 0
        self.nodes_visited = 0
        self.move_times = []
        self.info_label.config(
            text=f"Current Number: {self.current_number}\nHuman Score: {self.human_score}, Computer Score: {self.computer_score}")

        if self.turn.get() == "computer":
            self.root.after(1000, self.computer_move)

    def play_turn(self, factor):
        if self.turn.get() != "human":
            return

        self.current_number *= factor
        self.update_scores(self.current_number, True)

        if self.current_number >= 1200:
            self.end_game()
            return

        self.turn.set("computer")
        self.root.after(1000, self.computer_move)

    def computer_move(self):
        start_time = time.time()
        self.nodes_visited = 0

        # Create root node and generate tree
        root = GameNode(self.current_number, self.human_score, self.computer_score, False)
        self.generate_game_tree(root, 3)  # 3-ply lookahead

        best_move = None
        best_score = float('-inf')

        for i, child in enumerate(root.children):
            if self.algorithm.get() == "Minimax":
                score = self.minimax(child, 0, 3, False)
            else:
                score = self.alpha_beta(child, 0, 3, float('-inf'), float('inf'), False)

            if score > best_score:
                best_score = score
                best_move = [2, 3, 4][i]

        self.current_number *= best_move
        self.update_scores(self.current_number, False)
        self.move_times.append(time.time() - start_time)

        if self.current_number >= 1200:
            self.end_game()
            return

        self.turn.set("human")

    def update_scores(self, number, is_human):
        if number % 2 == 0:
            if is_human:
                self.computer_score -= 1
            else:
                self.human_score -= 1
        else:
            if is_human:
                self.human_score += 1
            else:
                self.computer_score += 1

        self.info_label.config(
            text=f"Current Number: {self.current_number}\nHuman Score: {self.human_score}, Computer Score: {self.computer_score}")

    def end_game(self):
        if self.human_score > self.computer_score:
            winner = "Human wins!"
        elif self.human_score < self.computer_score:
            winner = "Computer wins!"
        else:
            winner = "It's a draw!"
        messagebox.showinfo("Game Over", winner)


def run_experiments():
    results = {"Minimax": {"human_wins": 0, "comp_wins": 0, "nodes": [], "times": []},
               "Alpha-Beta": {"human_wins": 0, "comp_wins": 0, "nodes": [], "times": []}}

    for algo in ["Minimax", "Alpha-Beta"]:
        for _ in range(10):
            # Create a non-GUI instance for experiments
            game = Game(tk.Tk())
            game.algorithm.set(algo)
            game.current_number = random.randint(8, 18)
            game.human_score = 0
            game.computer_score = 0
            game.turn.set(random.choice(["human", "computer"]))
            game.nodes_visited = 0
            game.move_times = []

            while game.current_number < 1200:
                if game.turn.get() == "human":
                    factor = random.choice([2, 3, 4])
                    game.current_number *= factor
                    game.update_scores(game.current_number, True)
                    game.turn.set("computer")
                else:
                    game.computer_move()
                    game.turn.set("human")

            results[algo]["nodes"].append(game.nodes_visited)
            results[algo]["times"].extend(game.move_times)
            if game.human_score > game.computer_score:
                results[algo]["human_wins"] += 1
            elif game.computer_score > game.human_score:
                results[algo]["comp_wins"] += 1

    # Print results
    for algo in results:
        print(f"\n{algo} Results:")
        print(f"Human Wins: {results[algo]['human_wins']}")
        print(f"Computer Wins: {results[algo]['comp_wins']}")
        print(f"Avg Nodes Visited: {sum(results[algo]['nodes']) / 10:.2f}")
        print(f"Avg Move Time: {sum(results[algo]['times']) / len(results[algo]['times']):.4f}s")


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
    # Uncomment to run experiments after closing GUI
    # run_experiments()

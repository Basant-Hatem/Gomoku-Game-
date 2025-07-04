import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

class WelcomeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gomoku Game Launcher")
        self.setup_ui()

    def setup_ui(self):
        # Welcome label
        welcome_label = tk.Label(self.root, text="Welcome to Gomoku!", font=('Arial', 24))
        welcome_label.pack(pady=20)

        # Mode selection label
        mode_label = tk.Label(self.root, text="Select Game Mode:", font=('Arial', 16))
        mode_label.pack(pady=10)

        # AI vs AI button
        ai_vs_ai_btn = tk.Button(self.root, text="AI vs AI",
                                command=self.launch_ai_vs_ai,
                                font=('Arial', 14), width=20)
        ai_vs_ai_btn.pack(pady=5)

        # Human vs AI button
        human_vs_ai_btn = tk.Button(self.root, text="Human vs AI",
                                   command=self.show_ai_selection,
                                   font=('Arial', 14), width=20)
        human_vs_ai_btn.pack(pady=5)

        # Exit button
        exit_btn = tk.Button(self.root, text="Exit",
                           command=self.root.quit,
                           font=('Arial', 12))
        exit_btn.pack(pady=20)

    def show_ai_selection(self):
        # Clear current widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # AI selection label
        ai_label = tk.Label(self.root, text="Select AI Opponent:", font=('Arial', 16))
        ai_label.pack(pady=20)

        # Alpha-Beta button
        alphabeta_btn = tk.Button(self.root, text="Play vs Alpha-Beta AI",
                                 command=lambda: self.launch_human_vs_ai("alphabeta"),
                                 font=('Arial', 14), width=20)
        alphabeta_btn.pack(pady=5)

        # Minimax button
        minimax_btn = tk.Button(self.root, text="Play vs Minimax AI",
                              command=lambda: self.launch_human_vs_ai("minimax"),
                              font=('Arial', 14), width=20)
        minimax_btn.pack(pady=5)

        # Back button
        back_btn = tk.Button(self.root, text="Back",
                            command=self.setup_ui,
                            font=('Arial', 12))
        back_btn.pack(pady=20)

    def launch_ai_vs_ai(self):
        self.root.destroy()
        try:
            subprocess.run([sys.executable, "AiVsAi\AiVsAi.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch AI vs AI game: {str(e)}")

    def launch_human_vs_ai(self, ai_type):
        self.root.destroy()
        try:
            if ai_type == "alphabeta":
                subprocess.run([sys.executable, "HumanVsAi\GUI_human_vs_ai_alphabeta_final.py"])
            else:
                subprocess.run([sys.executable, "HumanVsAi\GUI_human_vs_ai_minimax_final.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch Human vs AI game: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = WelcomeGUI(root)
    root.mainloop()
import tkinter as tk
from createscratch import CreateFromScratchApp

class MainMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu GUI")
        self.root.geometry("800x600")

        # Setting up main menu
        self.main_menu()

    def main_menu(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create menu buttons
        self.start_button = tk.Button(self.root, text="Create from Scratch", command=self.create_from_scratch)
        self.start_button.pack(pady=10)

        self.load_button = tk.Button(self.root, text="Load Points from File")
        self.load_button.pack(pady=10)

    def create_from_scratch(self):
        # Destroy the current window and open CreateFromScratchApp in a new window
        self.root.destroy()
        new_root = tk.Tk()
        CreateFromScratchApp(new_root, self.reopen_main_menu)

    def reopen_main_menu(self):
        # Reopen the main menu
        new_root = tk.Tk()
        MainMenuApp(new_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenuApp(root)
    root.mainloop()

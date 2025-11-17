import tkinter as tk
from tkinter import font
import random

class JokeAssistant:
    def __init__(self, master):
        self.master = master
        master.title("Joke-Telling Assistant")
        master.geometry("600x400")
        master.configure(bg="#f0f0f0")

        # Jokes list (setup, punchline)
        self.joke_list = self.get_jokes()
        self.active_joke = None
        self.is_punchline_visible = False

        # Build all GUI Elements
        self.build_ui()

    def get_jokes(self):
        return [
            ("Why did the chicken cross the road?", "To get to the other side."),
            ("What happens if you boil a clown?", "You get a laughing stock."),
            ("Why did the car get a flat tire?", "Because there was a fork in the road!"),
            ("How did the hipster burn his mouth?", "He ate his pizza before it was cool."),
            ("What did the janitor say when he jumped out of the closet?", "SUPPLIES!!!!"),
            ("Have you heard about the band 1023MB?", "It's because they haven't got a gig yet…"),
            ("Why does the golfer wear two pants?", "In case he gets a hole-in-one."),
            ("Why should you wear glasses to maths class?", "Because it helps with division."),
            ("Why does it take pirates so long to learn the alphabet?", "They spend years at C."),
            ("Why did the woman date the mushroom?", "Because he was a fun-ghi."),
            ("Why do bananas never get lonely?", "Because they hang out in bunches."),
            ("What did the buffalo say when his son left?", "Bison."),
            ("Why shouldn't secrets be told in a cornfield?", "Too many ears."),
            ("What do you call someone who hates carbs?", "Lack-Toast Intolerant."),
            ("Why did the can crusher quit?", "It was soda pressing."),
            ("Why did the birthday boy wrap himself?", "He wanted to live in the present."),
            ("What does a house wear?", "A dress."),
            ("Why couldn't the toilet paper cross?", "It got stuck in a crack."),
            ("Why didn't the bike go anywhere?", "It was two-tired!"),
            ("Want to hear a pizza joke?", "Never mind. It's too cheesy."),
            ("Why are chemists great problem solvers?", "They have all the solutions."),
            ("Why can't you starve in a desert?", "Because of the sand which is there!"),
            ("What did the cheese say to the mirror?", "Halloumi!"),
            ("Why did the developer go broke?", "He used up all his cache."),
            ("Why don't ants get sick?", "They have little antibodies."),
            ("Why did the donut see a dentist?", "To get a filling."),
            ("What do you call a bear with no teeth?", "A gummy bear!"),
            ("What do vegan zombies eat?", "Graaains."),
            ("What do you call a one-eyed dinosaur?", "Do-you-think-he-saw-us!"),
            ("Why not fall in love with a tennis player?", "Because to them love means NOTHING!"),
            ("What did the full glass say to the empty one?", "You look drunk."),
            ("What’s a potato’s favorite transport?", "The gravy train."),
            ("What did one ocean say to the other?", "Nothing. They waved."),
            ("What did the right eye say to the left?", "Between you and me, something smells."),
            ("What do you call a dog run over by a steamroller?", "Spot!"),
            ("What's the difference between a hippo and a zippo?", "One's heavy; the other's a little lighter."),
            ("Why don't scientists trust atoms?", "They make up everything.")
        ]

    def build_ui(self):
        # Title
        title_style = font.Font(family="Helvetica", size=18, weight="bold")
        tk.Label(self.master, text="Joke-Telling Assistant",
                 font=title_style, bg="#f0f0f0", fg="#333").pack(pady=20)

        # Joke display frame
        self.display_frame = tk.Frame(self.master, bg="white", borderwidth=2, relief=tk.RIDGE)
        self.display_frame.pack(pady=20, padx=30, fill=tk.BOTH, expand=True)

        # Joke setup text
        setup_style = font.Font(family="Arial", size=14, weight="bold")
        self.setup_text = tk.Label(self.display_frame, text="Click the button to hear a joke!",
                                   font=setup_style, bg="white", fg="#2c3e50",
                                   wraplength=500, justify=tk.CENTER)
        self.setup_text.pack(pady=20)

        # Punchline text
        punch_style = font.Font(family="Arial", size=12)
        self.punch_text = tk.Label(self.display_frame, text="", font=punch_style,
                                   bg="white", fg="#27ae60", wraplength=500,
                                   justify=tk.CENTER)
        self.punch_text.pack(pady=10)

        # Button frame
        button_area = tk.Frame(self.master, bg="#f0f0f0")
        button_area.pack(pady=10)

        # Buttons
        self.alexa_button = tk.Button(button_area, text="Alexa tell me a Joke",
                                      command=self.new_joke, bg="#3498db", fg="white",
                                      font=("Arial", 12, "bold"), padx=20, pady=10,
                                      relief=tk.RAISED, cursor="hand2")
        self.alexa_button.grid(row=0, column=0, padx=5)

        self.show_button = tk.Button(button_area, text="Show Punchline",
                                     state=tk.DISABLED, command=self.reveal_punchline,
                                     bg="#e74c3c", fg="white",
                                     font=("Arial", 14, "bold"), padx=20, pady=10)
        self.show_button.grid(row=0, column=1, padx=5)

        self.next_button = tk.Button(button_area, text="Next Joke",
                                     state=tk.DISABLED, command=self.new_joke,
                                     bg="#f39c12", fg="white",
                                     font=("Arial", 14, "bold"), padx=20, pady=10)
        self.next_button.grid(row=0, column=2, padx=5)

        tk.Button(button_area, text="Quit", command=self.master.quit,
                  bg="#95a5a6", fg="white", font=("Arial", 12, "bold"),
                  padx=20, pady=10).grid(row=0, column=3, padx=5)

    def new_joke(self):
        self.active_joke = random.choice(self.joke_list)
        self.is_punchline_visible = False

        self.setup_text.config(text=self.active_joke[0])
        self.punch_text.config(text="")

        self.alexa_button.config(state=tk.DISABLED)
        self.show_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.NORMAL)

    def reveal_punchline(self):
        if self.active_joke and not self.is_punchline_visible:
            self.punch_text.config(text=self.active_joke[1])
            self.is_punchline_visible = True

            self.show_button.config(state=tk.DISABLED)
            self.alexa_button.config(state=tk.NORMAL)


# Start app
root = tk.Tk()
JokeAssistant(root)
root.mainloop()

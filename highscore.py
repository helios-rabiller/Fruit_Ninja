import pygame
import pymunk
import random
import sys
import os
import json

# Initialize Pygame and Pymunk
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
SPACE = pymunk.Space()
SPACE.gravity = (0, 500)  # Gravity to pull fruits downward

# Load fruit images
FRUIT_IMAGES = {
    'melon': pygame.image.load("images/melon.png"),
    'orange': pygame.image.load("images/orange.png"),
    'pomegranate': pygame.image.load("images/pomegranate.png"),
    'guava': pygame.image.load("images/guava.png"),
    'bomb': pygame.image.load("images/bomb.png"),
    'ice': pygame.image.load("images/ice.png")
}
for fruit, img in FRUIT_IMAGES.items():
    FRUIT_IMAGES[fruit] = pygame.transform.scale(img, (80, 80))  # Resize fruits

# Load half-fruit images
HALF_FRUIT_IMAGES = {
    'melon': pygame.image.load("images/half_melon.png"),
    'orange': pygame.image.load("images/half_orange.png"),
    'pomegranate': pygame.image.load("images/half_pomegranate.png"),
    'guava': pygame.image.load("images/half_guava.png"),
    'bomb': pygame.image.load("images/half_bomb.png"),
    'ice': pygame.image.load("images/half_ice.png")
}
for fruit, img in HALF_FRUIT_IMAGES.items():
    HALF_FRUIT_IMAGES[fruit] = pygame.transform.scale(img, (40, 80))  # Resize half-fruits

# Save highscore to JSON
def save_highscore(name, score):
    try:
        # Read existing highscores
        with open("highscores.json", "r") as f:
            highscores = json.load(f)
    except FileNotFoundError:
        highscores = []

    # Add new highscore
    highscores.append({"name": name, "score": score})

    # Sort highscores by score (descending)
    highscores.sort(key=lambda x: x["score"], reverse=True)

    # Save updated highscores
    with open("highscores.json", "w") as f:
        json.dump(highscores, f)

# Clear highscores
def clear_highscores():
    with open("highscores.json", "w") as f:
        f.write("[]")  # Write an empty list to JSON

# Read highscores from JSON
def read_highscores():
    try:
        with open("highscores.json", "r") as f:
            highscores = json.load(f)
            return highscores[:5]  # Return top 5 highscores
    except FileNotFoundError:
        return []

# Show highscores screen
def show_highscores():
    WINDOW.blit(background, (0, 0))
    draw_text(WINDOW, "High Scores", 90, WIDTH / 2, 50)

    # Read and display highscores
    scores = read_highscores()
    y_offset = 150
    for entry in scores:
        draw_text(WINDOW, f"{entry['name']}: {entry['score']}", 40, WIDTH / 2, y_offset)
        y_offset += 40

    # Buttons "Effacer" and "Menu"
    effacer_button = create_small_button("Effacer", WIDTH // 2 - 150, HEIGHT - 100)
    menu_button = create_small_button("Menu", WIDTH // 2 + 50, HEIGHT - 100)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                # If "Effacer" button is clicked
                if effacer_button.collidepoint(mouse_pos):
                    clear_highscores()  # Clear highscores
                    scores = read_highscores()  # Refresh highscores list
                    show_highscores()  # Redraw the screen

                # If "Menu" button is clicked
                elif menu_button.collidepoint(mouse_pos):
                    waiting = False
                    show_menu_screen()

# Input player name
def input_name():
    global player_name
    player_name = ""

    while True:
        WINDOW.blit(background, (0, 0))
        draw_text(WINDOW, "Enter your name:", 50, WIDTH / 2, HEIGHT / 2 - 50)
        draw_text(WINDOW, player_name, 50, WIDTH / 2, HEIGHT / 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    save_highscore(player_name, score)
                    return
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    player_name += event.unicode

# Add boundaries (left and right walls)
def add_boundaries():
    # Left wall
    left_wall = pymunk.Segment(SPACE.static_body, (0, 0), (0, HEIGHT), 5)
    left_wall.elasticity = 0.8  # Bounciness
    # Right wall
    right_wall = pymunk.Segment(SPACE.static_body, (WIDTH, 0), (WIDTH, HEIGHT), 5)
    right_wall.elasticity = 0.8  # Bounciness
    SPACE.add(left_wall, right_wall)

# Fruit class
class Fruit:
    def __init__(self, x, y, image, fruit_type):
        self.body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 25))
        self.body.position = (x, y)
        self.body.velocity = (random.randint(-200, 200), -700)  # Initial upward velocity
        self.shape = pymunk.Circle(self.body, 25)
        self.shape.elasticity = 0.8  # Bounciness of fruits
        self.shape.friction = 0.5  # Friction to slow down fruits
        self.image = image
        self.fruit_type = fruit_type
        self.letter = fruit_keys[fruit_type]  # Use the assigned letter from fruit_keys
        self.is_cut = False  # Track if the fruit is cut
        SPACE.add(self.body, self.shape)

    def draw(self, window):
        pos = int(self.body.position.x), int(self.body.position.y)
        if self.is_cut:
            # Draw two half-fruits
            window.blit(HALF_FRUIT_IMAGES[self.fruit_type], (pos[0] - 20, pos[1]))
            window.blit(HALF_FRUIT_IMAGES[self.fruit_type], (pos[0] + 20, pos[1]))
        else:
            window.blit(self.image, self.image.get_rect(center=pos))
            # Draw the letter on the fruit
            font = pygame.font.SysFont("Arial", 24)
            text = font.render(self.letter, True, (0, 0, 0))
            text_rect = text.get_rect(center=pos)
            window.blit(text, text_rect)

# HalfFruit class (for displaying cut fruits)
class HalfFruit:
    def __init__(self, x, y, image, velocity):
        self.body = pymunk.Body(1, pymunk.moment_for_box(1, (40, 80)))
        self.body.position = (x, y)
        self.body.velocity = velocity
        self.shape = pymunk.Poly.create_box(self.body, (40, 80))
        self.shape.elasticity = 0.8
        self.shape.friction = 0.5
        self.image = image
        SPACE.add(self.body, self.shape)

    def draw(self, window):
        pos = int(self.body.position.x), int(self.body.position.y)
        window.blit(self.image, self.image.get_rect(center=pos))

# Add boundaries to the space
add_boundaries()

# Variables for game state
player_lives = 3  # Track player lives
score = 0  # Track score
strikes = 0  # Track strikes
combo_count = 0  # Track combo streak
time_paused = False  # Flag for pause when ice is sliced
pause_duration = 0  # Counter for frames during the pause
fruits = ['melon', 'orange', 'pomegranate', 'guava', 'bomb', 'ice']  # Added ice
bomb_letter_change_interval = 300  # Change bomb letter every 5 seconds (60 FPS * 5)
bomb_letter_change_timer = 0
active_fruit_letters = set()

# Map fruits to letters (dynamic assignment)
fruit_keys = {}

def assign_random_keys():
    global fruit_keys, active_fruit_letters
    letters = list('AZERTYUI')  # Use uppercase letters
    random.shuffle(letters)

    # Assign letters to fruits first
    for fruit in fruits:
        if fruit != 'bomb':  # Skip the bomb for now
            fruit_keys[fruit] = letters.pop()

    # Assign a unique letter to the bomb, excluding active fruit letters
    available_letters = [letter for letter in letters if letter not in active_fruit_letters]
    if available_letters:
        bomb_letter = random.choice(available_letters)
    else:
        bomb_letter = random.choice(letters)  # Fallback if no letters are available
    fruit_keys['bomb'] = bomb_letter

assign_random_keys()

difficulty = "easy"  # Default difficulty level
FPS = 60  # Initial FPS value

# Initialize pygame and create window
pygame.display.set_caption('Fruit-Ninja Game')
background = pygame.image.load('back.jpg')
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
lives_icon = pygame.image.load('images/white_lives.png')

def game_over_screen():
    """Function to display Game Over screen"""

    global score, game_over, game_running

    WINDOW.blit(background, (0, 0))
    draw_text(WINDOW, "GAME OVER", 90, WIDTH / 2, HEIGHT / 4)
    draw_text(WINDOW, f"Final Score: {score}", 50, WIDTH / 2, HEIGHT / 2 - 50)

    # Buttons for restart and menu
    restart_button = create_small_button("Restart", WIDTH // 2 - 120, HEIGHT - 200)
    menu_button = create_small_button("Menu", WIDTH // 2 + 20, HEIGHT - 200)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                # If "Restart" button is clicked
                if restart_button.collidepoint(mouse_pos):
                    input_name()  # Ask for player name
                    game_over = True
                    waiting = False

                # If "Menu" button is clicked
                elif menu_button.collidepoint(mouse_pos):
                    input_name()  # Ask for player name
                    show_menu_screen()
                    waiting = False

# Function to generate random fruits
def generate_random_fruit():
    x = random.randint(100, WIDTH - 100)
    y = HEIGHT
    fruit_type = random.choice(fruits)
    fruit_image = FRUIT_IMAGES[fruit_type]
    return Fruit(x, y, fruit_image, fruit_type)

# Dictionary for fruit data
active_fruits = []
half_fruits = []  # List to store cut fruits

def hide_cross_lives(x, y):
    WINDOW.blit(pygame.image.load("images/red_lives.png"), (x, y))

# Generic method to draw fonts
def draw_text(display, text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.Font(pygame.font.match_font('comic.ttf'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    display.blit(text_surface, text_rect)

# Draw player lives
def draw_lives(display, x, y, lives, image):
    for i in range(lives):
        img = pygame.image.load(image)
        img_rect = img.get_rect()
        img_rect.x = int(x + 35 * i)
        img_rect.y = y
        display.blit(img, img_rect)

# Function to create a transparent button
def create_transparent_button(text, width, height, y_position, color=(255, 255, 255, 100)):
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    button_surface.fill(color)
    button_x = WIDTH / 2 - width / 2
    WINDOW.blit(button_surface, (button_x, y_position))
    draw_text(WINDOW, text, 40, WIDTH / 2, y_position + height / 2 - 10, (0, 0, 0))
    return pygame.Rect(button_x, y_position, width, height)

# Small button restart and back
def create_small_button(text, x, y, width=100, height=40):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(WINDOW, (255, 255, 255), button_rect, border_radius=10)
    draw_text(WINDOW, text, 20, x + width // 2, y + height // 2 - 5, (0, 0, 0))
    return button_rect

def show_menu_screen():
    global difficulty, FPS
    WINDOW.blit(background, (0, 0))
    draw_text(WINDOW, "FRUIT NINJA!", 90, WIDTH / 2, HEIGHT / 6)

    # Buttons
    easy_button = create_transparent_button("Easy", 300, 50, HEIGHT / 2 - 80)
    hard_button = create_transparent_button("Hard", 300, 50, HEIGHT / 2)
    highscores_button = create_transparent_button("High Scores", 300, 50, HEIGHT / 2 + 80)
    exit_button = create_transparent_button("Exit", 300, 50, HEIGHT / 2 + 160)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                if easy_button.collidepoint(mouse_pos):
                    difficulty = "easy"
                    FPS = 60
                    assign_random_keys()
                    waiting = False
                elif hard_button.collidepoint(mouse_pos):
                    difficulty = "hard"
                    FPS = 60
                    assign_random_keys()
                    waiting = False
                elif highscores_button.collidepoint(mouse_pos):
                    show_highscores()
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

# Show score screen
def show_score_screen():
    global score
    WINDOW.blit(background, (0, 0))
    draw_text(WINDOW, "Score: " + str(score), 90, WIDTH / 2, HEIGHT / 3)
    draw_text(WINDOW, "Press ENTER to go back", 50, WIDTH / 2, HEIGHT / 2 + 80)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    waiting = False
                    show_menu_screen()

# Game loop
first_round = True
game_over = True
game_running = True
while game_running:
    if game_over:
        if first_round:
            show_menu_screen()
            first_round = False
        game_over = False
        player_lives = 3
        score = 0
        strikes = 0
        combo_count = 0
        time_paused = False
        pause_duration = 0
        active_fruits = []
        half_fruits = []
        draw_lives(WINDOW, 690, 5, player_lives, 'images/red_lives.png')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        if event.type == pygame.KEYDOWN:
            key_pressed = pygame.key.name(event.key).upper()  # Convert to uppercase
            print(f"Key pressed: {key_pressed}")

            for fruit in active_fruits[:]:
                print(f"Fruit letter: {fruit.letter}")
                if key_pressed == fruit.letter:
                    if fruit.fruit_type == 'bomb':
                        player_lives -= 1
                        strikes = 0  # Reset strikes on bomb hit
                        if player_lives == 0:
                            hide_cross_lives(690, 15)
                        elif player_lives == 1:
                            hide_cross_lives(725, 15)
                        elif player_lives == 2:
                            hide_cross_lives(760, 15)

                        if player_lives < 0:
                            game_over_screen()  # Show Game Over screen
                            game_over = True

                    else:
                        combo_count += 1
                        score += combo_count if difficulty == "hard" else 1

                    # Mark the fruit as cut
                    fruit.is_cut = True
                    # Create two half-fruits
                    half_fruit_path = "images/half_" + fruit.fruit_type + ".png"
                    half_fruit_image = pygame.image.load(half_fruit_path)
                    half_fruit_image = pygame.transform.scale(half_fruit_image, (40, 80))

                    half_fruits.append(HalfFruit(fruit.body.position.x, fruit.body.position.y, half_fruit_image, (random.randint(-200, 200), -300)))
                    half_fruits.append(HalfFruit(fruit.body.position.x, fruit.body.position.y, half_fruit_image, (random.randint(-200, 200), -300)))

                    # Remove the fruit from active_fruits
                    active_fruits.remove(fruit)
                    SPACE.remove(fruit.body, fruit.shape)

                    if fruit.fruit_type == 'ice':  # Start pause when ice is sliced
                        time_paused = True
                        pause_duration = 180

        # Handle Restart and Back buttons
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pos = pygame.mouse.get_pos()
            if restart_button.collidepoint(mouse_pos):
                game_over = True
            elif back_button.collidepoint(mouse_pos):
                show_menu_screen()

    # If the game is paused due to ice, skip the fruit updates
    if time_paused:
        pause_duration -= 1
        if pause_duration <= 0:
            time_paused = False  # Resume the game after the pause

    if not time_paused:
        WINDOW.blit(background, (0, 0))
        draw_text(WINDOW, 'Score : ' + str(score), 42, 100, 0)
        draw_lives(WINDOW, 690, 5, player_lives, 'images/red_lives.png')

        # Spawn new fruits randomly
        spawn_chance = 2 if difficulty == "hard" else 1  # Higher chance on hard difficulty
        if random.randint(0, 100) < spawn_chance:  # Adjust spawn rate
            active_fruits.append(generate_random_fruit())

        # Draw and update fruits
        for fruit in active_fruits[:]:
            fruit.draw(WINDOW)
            if fruit.body.position.y > HEIGHT + 50:  # Fruit is off-screen
                active_fruits.remove(fruit)
                SPACE.remove(fruit.body, fruit.shape)
                if fruit.fruit_type != 'bomb':
                    strikes += 1
                    if strikes >= 3:
                        player_lives -= 1
                        strikes = 0
                        if player_lives <= 0:
                            game_over_screen()  # Show Game Over screen
                            game_over = True

        # Draw and update half-fruits
        for half_fruit in half_fruits[:]:
            half_fruit.draw(WINDOW)
            if half_fruit.body.position.y > HEIGHT + 50:  # Half-fruit is off-screen
                half_fruits.remove(half_fruit)
                SPACE.remove(half_fruit.body, half_fruit.shape)

    # Update the screen with buttons
    restart_button = create_small_button("Restart", WIDTH // 2 - 120, HEIGHT - 60)
    back_button = create_small_button("Back", WIDTH // 2 + 20, HEIGHT - 60)

    SPACE.step(1 / 100)  # Smooth physics
    pygame.display.update()
    CLOCK.tick(FPS)  # 60 FPS

pygame.quit()
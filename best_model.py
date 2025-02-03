import pygame
import pymunk
import random
import sys
import os

# Initialize Pygame and Pymunk
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
SPACE = pymunk.Space()
SPACE.gravity = (0, 500)  # Gravity to pull fruits downward
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))


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
        SPACE.add(self.body, self.shape)

    def draw(self, window):
        pos = int(self.body.position.x), int(self.body.position.y)
        window.blit(self.image, self.image.get_rect(center=pos))
        # Draw the letter on the fruit
        font = pygame.font.SysFont("Arial", 36,bold=True)
        text = font.render(self.letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=pos)
        window.blit(text, text_rect)

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
    letters = list('AZERTYUIOPQSDFGHJKLM')  # Use uppercase letters
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

def create_small_button(text, x, y, width=100, height=40):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(gameDisplay, (255, 255, 255), button_rect, border_radius=10)
    draw_text(gameDisplay, text, 20, x + width // 2, y + height // 2 - 5)
    return button_rect

difficulty = "easy"  # Default difficulty level

# Initialize pygame and create window
pygame.display.set_caption('Fruit-Ninja Game')
background = pygame.image.load('back.jpg')
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, (255, 255, 255))
lives_icon = pygame.image.load('images/white_lives.png')

# Function to generate random fruits
def generate_random_fruit():
    x = random.randint(100, WIDTH - 100)
    y = HEIGHT
    fruit_type = random.choice(fruits)
    fruit_image = FRUIT_IMAGES[fruit_type]
    return Fruit(x, y, fruit_image, fruit_type)

# Dictionary for fruit data
active_fruits = []

def hide_cross_lives(x, y):
    WINDOW.blit(pygame.image.load("images/red_lives.png"), (x, y))

# Generic method to draw fonts
def draw_text(display, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('comic.ttf'), size)
    text_surface = font.render(text, True, (0, 0, 0))
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

# Show game menu with transparent buttons
def show_menu_screen():
    global difficulty
    WINDOW.blit(background, (0, 0))
    draw_text(WINDOW, "FRUIT NINJA!", 90, WIDTH / 2, HEIGHT / 6)

    # Define button areas (rectangles) and transparency
    button_height = 50
    button_spacing = 20

    # Vertical positions for buttons
    easy_button_y = HEIGHT / 2 - 80
    hard_button_y = easy_button_y + button_height + button_spacing
    score_button_y = hard_button_y + button_height + button_spacing
    exit_button_y = score_button_y + button_height + button_spacing

    # Create transparent buttons
    draw_text(WINDOW, "Easy", 50, WIDTH / 2, easy_button_y)
    draw_text(WINDOW, "Hard", 50, WIDTH / 2, hard_button_y)
    draw_text(WINDOW, "Score", 50, WIDTH / 2, score_button_y)
    draw_text(WINDOW, "Exit", 50, WIDTH / 2, exit_button_y)

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                # Check for button clicks based on the positions
                if easy_button_y <= mouse_pos[1] <= easy_button_y + button_height:
                    difficulty = "easy"
                    assign_random_keys()  # Reassign keys on difficulty change
                    waiting = False
                elif hard_button_y <= mouse_pos[1] <= hard_button_y + button_height:
                    difficulty = "hard"
                    assign_random_keys()  # Reassign keys on difficulty change
                    waiting = False
                elif score_button_y <= mouse_pos[1] <= score_button_y + button_height:
                    show_score_screen()
                elif exit_button_y <= mouse_pos[1] <= exit_button_y + button_height:
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
        # Update bomb letter change timer
    bomb_letter_change_timer += 1
    if bomb_letter_change_timer >= bomb_letter_change_interval:
        bomb_letter_change_timer = 0 
        assign_random_keys()  # Reassign bomb letter
        
        for fruit in active_fruits:
            if fruit.fruit_type == 'bomb':
                fruit.letter = fruit_keys['bomb']
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
                            show_menu_screen()
                            game_over = True

                    else:
                        combo_count += 1
                        score += combo_count if difficulty == "hard" else 1

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
        SPACE.step(1 / 5000)
        if pause_duration <= 0:
            time_paused = False  # Resume the game after the pause

    if not time_paused:  
        WINDOW.blit(background, (0, 0))
        draw_text(WINDOW, 'Score : ' + str(score), 42, 100, 0)
        draw_lives(WINDOW, 690, 5, player_lives, 'images/red_lives.png')

        # Spawn new fruits randomly
        if random.randint(0, 100) < 1:  # 1% chance to spawn a fruit each frame
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
                            game_over = True

    SPACE.step(1 / 50)  # smooth physics
  # Update the screen with buttons
    restart_button = create_small_button("Restart", WIDTH // 2 - 120, HEIGHT - 60)
    back_button = create_small_button("Back", WIDTH // 2 + 20, HEIGHT - 60)
    pygame.display.update()
    CLOCK.tick(60)  # 60 FPS

pygame.quit()
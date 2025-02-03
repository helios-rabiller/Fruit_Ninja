#ca marche
import pygame, sys
import os
import random 

# Variables for game state
player_lives = 3  # Track player lives
score = 0  # Track score
strikes = 0  # Track strikes
combo_count = 0  # Track combo streak
time_paused = False  # Flag for pause when ice is sliced
pause_duration = 0  # Counter for frames during the pause
fruits = ['melon', 'orange', 'pomegranate', 'guava', 'bomb', 'ice']  # Added ice

# Map fruits to letters (dynamic assignment)
fruit_keys = {}

def assign_random_keys():
    letters = list('abcdefghijklmnopqrstuvwxyz')
    random.shuffle(letters)
    for fruit in fruits:
        fruit_keys[fruit] = letters.pop()

assign_random_keys()

difficulty = "easy"  # Default difficulty level
FPS = 5  # Initial FPS value

# Initialize pygame and create window
WIDTH = 800
HEIGHT = 500
pygame.init()
pygame.display.set_caption('Fruit-Ninja Game')
gameDisplay = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

background = pygame.image.load('back.jpg')
font = pygame.font.Font(os.path.join(os.getcwd(), 'comic.ttf'), 42)
score_text = font.render('Score : ' + str(score), True, WHITE)
lives_icon = pygame.image.load('images/white_lives.png')

# Function to generate random fruits
def generate_random_fruits(fruit):
    fruit_path = "images/" + fruit + ".png"
    data[fruit] = {
        'img': pygame.image.load(fruit_path),
        'x': random.randint(100, 500),
        'y': 800,
        'speed_x': random.randint(-10, 10),
        'speed_y': random.randint(-80, -60),
        'throw': False,
        't': 0,
        'hit': False,
    }

    if random.random() >= 0.75:
        data[fruit]['throw'] = True
    else:
        data[fruit]['throw'] = False

# Dictionary for fruit data
data = {}
for fruit in fruits:
    generate_random_fruits(fruit)

def hide_cross_lives(x, y):
    gameDisplay.blit(pygame.image.load("images/red_lives.png"), (x, y))

# Generic method to draw fonts
def draw_text(display, text, size, x, y):
    font = pygame.font.Font(pygame.font.match_font('comic.ttf'), size)
    text_surface = font.render(text, True, WHITE)
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
    button_surface.fill(color)  # Fill with transparent color
    gameDisplay.blit(button_surface, (WIDTH / 2 - width / 2, y_position))
    draw_text(gameDisplay, text, 50, WIDTH / 2, y_position + height / 2)

# Show game menu with transparent buttons
def show_menu_screen():
    global difficulty, FPS
    gameDisplay.blit(background, (0, 0))
    draw_text(gameDisplay, "FRUIT NINJA!", 90, WIDTH / 2, HEIGHT / 6)

    # Define button areas (rectangles) and transparency
    button_height = 50
    button_spacing = 20

    # Vertical positions for buttons
    easy_button_y = HEIGHT / 2 - 80 #80
    hard_button_y = easy_button_y + button_height + button_spacing
    score_button_y = hard_button_y + button_height + button_spacing
    exit_button_y = score_button_y + button_height + button_spacing

    # Create transparent buttons
    create_transparent_button("Easy", 300, button_height, easy_button_y)
    create_transparent_button("Hard", 300, button_height, hard_button_y)
    create_transparent_button("Score", 300, button_height, score_button_y)
    create_transparent_button("Exit", 300, button_height, exit_button_y)

    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                # Check for button clicks based on the positions
                if easy_button_y <= mouse_pos[1] <= easy_button_y + button_height:
                    difficulty = "easy"
                    FPS = 3
                    assign_random_keys()  # Reassign keys on difficulty change
                    waiting = False
                elif hard_button_y <= mouse_pos[1] <= hard_button_y + button_height:
                    difficulty = "hard"
                    FPS = 5
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
    gameDisplay.blit(background, (0, 0))
    draw_text(gameDisplay, "Score: " + str(score), 90, WIDTH / 2, HEIGHT / 3)
    draw_text(gameDisplay, "Press ENTER to go back", 50, WIDTH / 2, HEIGHT / 2 + 80)
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(FPS)
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
        time_paused = False  # Reset pause flag
        pause_duration = 0  # Reset pause frame counter
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        if event.type == pygame.KEYDOWN:
            key_pressed = pygame.key.name(event.key)

            for fruit, assigned_key in fruit_keys.items():
                if key_pressed == assigned_key:
                    if data[fruit]['throw'] and not data[fruit]['hit']:
                        if fruit == 'bomb':
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

                            half_fruit_path = "images/explosion.png"
                        else:
                            half_fruit_path = "images/half_" + fruit + ".png"

                        data[fruit]['img'] = pygame.image.load(half_fruit_path)
                        data[fruit]['hit'] = True

                        # Increment score
                        if fruit != 'bomb':
                            combo_count += 1
                            score += combo_count if difficulty == "hard" else 1

                        score_text = font.render('Score : ' + str(score), True, WHITE)

                        if fruit == 'ice':  # Start pause when ice is sliced
                            time_paused = True
                            pause_duration = FPS * 3  # 3 seconds * FPS (e.g., 5 FPS = 15 frames)

    # If the game is paused due to ice, skip the fruit updates
    if time_paused:
        pause_duration -= 1
        if pause_duration <= 0:
            time_paused = False  # Resume the game after the pause

    if not time_paused:  # If not paused, move the fruits
        gameDisplay.blit(background, (0, 0))
        gameDisplay.blit(score_text, (0, 0))
        draw_lives(gameDisplay, 690, 5, player_lives, 'images/red_lives.png')

        for key, value in data.items():
            if value['throw']:
                value['x'] += value['speed_x']
                value['y'] += value['speed_y']
                value['speed_y'] += (1 * value['t'])
                value['t'] += 1

                if value['y'] <= 800:
                    gameDisplay.blit(value['img'], (value['x'], value['y']))

                    # Draw the corresponding letter above the fruit
                    letter_x = value['x'] + value['img'].get_width() // 2
                    letter_y = value['y'] - 20
                    draw_text(gameDisplay, fruit_keys[key], 30, letter_x, letter_y)

                else:
                    generate_random_fruits(key)

            else:
                generate_random_fruits(key)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()

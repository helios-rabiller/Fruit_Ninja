import pygame
import pymunk
import random

# Initialize Pygame and Pymunk
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
CLOCK = pygame.time.Clock()
SPACE = pymunk.Space()
SPACE.gravity = (0, 500)  # Gravity to pull fruits downward

# Load fruit images
FRUIT_IMAGES = [
    pygame.image.load("apple.png"),
    pygame.image.load("bomb.png"),
    pygame.image.load("heart.png")
]
for i, img in enumerate(FRUIT_IMAGES):
    FRUIT_IMAGES[i] = pygame.transform.scale(img, (100, 0))  # Resize fruits

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
    def __init__(self, x, y, image):
        self.body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 25))
        self.body.position = (x, y)
        self.body.velocity = (random.randint(-200, 200), -700)  # Initial upward velocity
        self.shape = pymunk.Circle(self.body, 25)
        self.shape.elasticity = 0.8  # Bounciness of fruits
        self.shape.friction = 0.5  # Friction to slow down fruits
        self.image = image
        self.letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # Assign a random letter
        SPACE.add(self.body, self.shape)

    def draw(self, window):
        pos = int(self.body.position.x), int(self.body.position.y)
        window.blit(self.image, self.image.get_rect(center=pos))
        # Draw the letter on the fruit
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(self.letter, True, (0, 0, 0))
        text_rect = text.get_rect(center=pos)
        window.blit(text, text_rect)

# Add boundaries to the space
add_boundaries()

# Main game variables
fruits = []
score = 0
lives = 3

# Main Loop
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():  # Check if a letter key was pressed
                key_pressed = event.unicode.upper()
                for fruit in fruits[:]:
                    if fruit.letter == key_pressed:
                        fruits.remove(fruit)
                        score += 1
                        print(f"Score: {score}")

    # Spawn fruits randomly
    if random.randint(0, 100) < 5:  # 5% chance to spawn a fruit each frame
        x = random.randint(100, WIDTH - 100)
        y = HEIGHT
        fruit_image = random.choice(FRUIT_IMAGES)
        fruits.append(Fruit(x, y, fruit_image))

    # Physics Step
    SPACE.step(1/100)

    # Draw Everything
    WINDOW.fill((0, 0, 0))
    for fruit in fruits:
        fruit.draw(WINDOW)

    # Display score and lives
    font = pygame.font.SysFont("Arial", 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    WINDOW.blit(score_text, (10, 10))
    WINDOW.blit(lives_text, (WIDTH - 150, 10))

    # Check for missed fruits
    for fruit in fruits[:]:
        if fruit.body.position.y > HEIGHT + 50:  # Fruit is off-screen
            fruits.remove(fruit)
            lives -= 1
            if lives <= 0:
                print("Game Over!")
                run = False

    pygame.display.update()
    CLOCK.tick(60)

pygame.quit()
import pygame
from sys import exit
import random

import os
import sys

def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, path)

#game variables
GAME_WIDTH = 360
GAME_HEIGHT = 640

BEST_SCORE_FILE = "best_score.txt"

# Speed milestones: at each score threshold, velocity_x becomes this value
SPEED_MILESTONES = {
    10: -3,
    20: -4,
    30: -5,
    40: -6,
    50: -7,
    60: -8,
}

def load_best_score():
    try:
        with open(BEST_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def save_best_score(score):
    try:
        with open(BEST_SCORE_FILE, "w") as f:
            f.write(str(int(score)))
    except Exception:
        pass

#bird class
bird_x = GAME_WIDTH/8
bird_y = GAME_HEIGHT/2
bird_width = 34 #17/12
bird_height = 24

class Bird(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
        self.img = img

#pipe class
pipe_x = GAME_WIDTH
pipe_y = 0
pipe_width = 64
pipe_height = 512

class Pipe(pygame.Rect):
    def __init__(self, img):
        pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
        self.img = img
        self.passed = False
    
#game image
background_image = pygame.image.load("flappybirdbg.png")
bird_image = pygame.image.load("flappybird.png")
bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
top_pipe_image = pygame.image.load("toppipe.png")
top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height))
bottom_pipe_image = pygame.image.load("bottompipe.png")
bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height))

#game logic
bird = Bird(bird_image)
pipes = []
velocity_x = -2
velocity_y = 0
gravity = 0.4
score = 0
best_score = load_best_score()
game_over = False

# Speed-up flash effect
speed_up_flash_timer = 0   # frames remaining to show flash
FLASH_DURATION = 90        # ~1.5 seconds at 60fps

def get_current_speed(score):
    """Return the velocity_x for the current score."""
    speed = -2
    for threshold, vel in sorted(SPEED_MILESTONES.items()):
        if score >= threshold:
            speed = vel
    return speed

def draw_text_with_shadow(surface, text, font, color, shadow_color, x, y):
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + 2, y + 2))
    main = font.render(text, True, color)
    surface.blit(main, (x, y))

def draw():
    global best_score, speed_up_flash_timer

    window.blit(background_image, (0, 0))
    window.blit(bird.img, bird)

    for pipe in pipes:
        window.blit(pipe.img, pipe)

    text_font = pygame.font.SysFont("Comic Sans MS", 45)
    small_font = pygame.font.SysFont("Comic Sans MS", 22)

    if game_over:
        if score > best_score:
            best_score = int(score)
            save_best_score(best_score)

        draw_text_with_shadow(window, "Game Over", text_font, "white", (50, 50, 50), 30, 220)

        score_text = f"Score:  {int(score)}"
        draw_text_with_shadow(window, score_text, small_font, "white", (50, 50, 50), 30, 285)

        best_color = (255, 215, 0) if int(score) >= best_score else "white"
        best_text = f"Best:    {best_score}"
        draw_text_with_shadow(window, best_text, small_font, best_color, (50, 50, 50), 30, 313)

        hint_font = pygame.font.SysFont("Comic Sans MS", 16)
        draw_text_with_shadow(window, "Press SPACE to restart", hint_font, (220, 220, 220), (30, 30, 30), 30, 350)

    else:
        # Live score (top-left)
        draw_text_with_shadow(window, str(int(score)), text_font, "white", (50, 50, 50), 5, 0)

        # Best score (top-right)
        best_text = f"Best: {best_score}"
        best_render_w = small_font.size(best_text)[0]
        draw_text_with_shadow(window, best_text, small_font, (255, 215, 0), (50, 50, 50),
                              GAME_WIDTH - best_render_w - 8, 8)

        # Speed-up flash banner
        if speed_up_flash_timer > 0:
            speed_up_flash_timer -= 1
            alpha = int(255 * (speed_up_flash_timer / FLASH_DURATION))
            flash_font = pygame.font.SysFont("Comic Sans MS", 28)
            current_level = abs(get_current_speed(score)) - 1  # level 1..7
            flash_text = f"SPEED UP!  x{current_level}"

            glow_surf = flash_font.render(flash_text, True, (255, 140, 0))
            glow_surf.set_alpha(alpha)
            text_surf = flash_font.render(flash_text, True, (255, 255, 255))
            text_surf.set_alpha(alpha)

            fx = GAME_WIDTH // 2 - text_surf.get_width() // 2
            fy = GAME_HEIGHT // 2 - 60
            window.blit(glow_surf, (fx + 2, fy + 2))
            window.blit(text_surf, (fx, fy))

def move():
    global velocity_y, velocity_x, score, game_over, speed_up_flash_timer
    velocity_y += gravity
    bird.y += velocity_y
    bird.y = max(bird.y, 0)

    if bird.y > GAME_HEIGHT:
        game_over = True
        return

    for pipe in pipes:
        pipe.x += velocity_x

        if not pipe.passed and bird.x > pipe.x + pipe.width:
            score += 0.5
            pipe.passed = True

        if bird.colliderect(pipe):
            game_over = True
            return

    # Check speed milestone
    new_speed = get_current_speed(score)
    if new_speed != velocity_x:
        velocity_x = new_speed
        speed_up_flash_timer = FLASH_DURATION

    while len(pipes) > 0 and pipes[0].x < -pipe_width:
        pipes.pop(0)

def create_pipes():
    random_pipe_y = pipe_y - pipe_height/4 - random.random()*(pipe_height/2)
    opening_space = GAME_HEIGHT/4

    top_pipe = Pipe(top_pipe_image)
    top_pipe.y = random_pipe_y
    pipes.append(top_pipe)

    bottom_pipe = Pipe(bottom_pipe_image)
    bottom_pipe.y = top_pipe.y + top_pipe.height + opening_space
    pipes.append(bottom_pipe)

pygame.init()
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

create_pipes_timer = pygame.USEREVENT + 0
pygame.time.set_timer(create_pipes_timer, 1500)

while True: #game loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == create_pipes_timer and not game_over:
            create_pipes()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                velocity_y = -6

                if game_over:
                    bird.y = bird_y
                    pipes.clear()
                    score = 0
                    velocity_x = -2          # reset speed on restart
                    speed_up_flash_timer = 0
                    game_over = False

    if not game_over:
        move()

    draw()
    pygame.display.update()
    clock.tick(60)

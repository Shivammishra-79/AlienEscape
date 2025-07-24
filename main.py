import pygame
import random
import os

pygame.init()

# Game window setup
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Alien Escape")

# Clock for FPS
clock = pygame.time.Clock()

# Load Sounds
jump_sound = pygame.mixer.Sound('assets/jump.wav')
coin_sound = pygame.mixer.Sound('assets/coin.wav')
gameover_sound = pygame.mixer.Sound('assets/gameover.wav')
speed_boost_sound = pygame.mixer.Sound('assets/coin.wav')
pygame.mixer.music.load('assets/music.mp3')
pygame.mixer.music.play(-1)  # Loop continuously

# Background Image
background_img = pygame.image.load('assets/bg.png').convert()

# Fonts
font = pygame.font.SysFont(None, 35)
coin_font = pygame.font.SysFont(None, 25)

# High Score File Handling
high_score_file = 'highscore.txt'
if os.path.exists(high_score_file):
    with open(high_score_file, 'r') as file:
        try:
            high_score = int(file.read())
        except:
            high_score = 0
else:
    high_score = 0

# Save high score to file
def save_high_score():
    with open(high_score_file, 'w') as file:
        file.write(str(high_score))

# Reset game variables
def reset_game():
    global player_x, player_y, is_jump, jump_count, double_jump_available, enemies, coins
    global score, game_over, paused, offset_x, health, speed_boost, boost_timer
    player_x = 100
    player_y = 500
    is_jump = False
    jump_count = 10
    double_jump_available = True
    enemies = []
    for i in range(6):
        size = random.randint(20, 35)
        enemies.append([800 + i * 300, 500, size])
    coins = []
    for i in range(5):
        coins.append([random.randint(50, 750), 500])
    score = 0
    game_over = False
    paused = False
    offset_x = 0
    health = 3
    speed_boost = False
    boost_timer = 0

reset_game()

# Game variables
ball_radius = 25
coin_radius = 20
eye_radius = 5
player_vel = 5
base_enemy_vel = 2
enemy_vel_increment = 0.1
boost_duration = 300

# Show "Created by Shivam Mishra" flag
# Show name flag and control
show_creator = True
game_started = False

running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    keys = pygame.key.get_pressed()

    screen.blit(background_img, (0, 0))  # Background Image

    if not game_started:
        # Big Creator Name
        creator_font = pygame.font.SysFont(None, 60)
        creator_text = creator_font.render("Created by Shivam Mishra", True, (15, 15, 15))
        screen.blit(creator_text, (screen_width // 2 - 250, screen_height // 2 - 50))

        # Play Now Button
        play_btn = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 30, 200, 50)
        pygame.draw.rect(screen, (0, 200, 0), play_btn)
        play_text = font.render("PLAY NOW", True, (255, 255, 255))
        screen.blit(play_text, (play_btn.x + 40, play_btn.y + 10))

        if play_btn.collidepoint(mouse_pos) and mouse_click[0]:
            game_started = True
            show_creator = False
            reset_game()

        pygame.display.update()
        continue  # Skip rest of game logic till start

    # Baaki pura game logic niche rahega...

    # Game logic if not paused or game over
    if not game_over and not paused:

        # Movement
        if keys[pygame.K_LEFT] and player_x > offset_x:
            player_x -= player_vel * (2 if speed_boost else 1)
        if keys[pygame.K_RIGHT] and player_x < offset_x + screen_width - ball_radius * 2:
            player_x += player_vel * (2 if speed_boost else 1)

        if player_x > screen_width // 2:
            offset_x = player_x - screen_width // 2

        # Jump handling with double jump
        if not is_jump:
            if keys[pygame.K_SPACE]:
                is_jump = True
                jump_sound.play()
                double_jump_available = True
        else:
            if jump_count >= -10:
                neg = 1
                if jump_count < 0:
                    neg = -1
                player_y -= (jump_count ** 2) * 0.5* neg
                jump_count -= 1
            else:
                if double_jump_available and keys[pygame.K_SPACE]:
                    double_jump_available = False
                    jump_count = 10
                    jump_sound.play()
                else:
                    is_jump = False
                    double_jump_available = True
                    jump_count = 10
        # Enemy movement and reposition
        for i in range(len(enemies)):
            speed = max(1, base_enemy_vel + score * enemy_vel_increment)
            enemies[i][0] -= speed
            if enemies[i][0] < offset_x - enemies[i][2] * 2:
                enemies[i][0] = offset_x + screen_width + random.randint(50, 300)
                enemies[i][1] = 500
                enemies[i][2] = random.randint(15, 25)

        # Collision detection
        player_rect = pygame.Rect(player_x - ball_radius, player_y - ball_radius, ball_radius * 2, ball_radius * 2)

        for ex, ey, esize in enemies:
            enemy_rect = pygame.Rect(ex - esize // 2, ey - esize // 4, esize + 20, esize // 2 + 10)
            if player_rect.colliderect(enemy_rect):
                health -= 1
                enemies.remove([ex, ey, esize])

        for i in range(len(coins)):
            coin_rect = pygame.Rect(coins[i][0] - coin_radius, coins[i][1] - coin_radius, coin_radius * 2, coin_radius * 2)
            if player_rect.colliderect(coin_rect):
                score += 1
                coins[i][0] = offset_x + screen_width + random.randint(100, 500)
                coins[i][1] = 500
                coin_sound.play()
                if random.random() < 0.3:
                    speed_boost = True
                    boost_timer = boost_duration
                    speed_boost_sound.play()

        # Speed boost timer
        if speed_boost:
            boost_timer -= 1
            if boost_timer <= 0:
                speed_boost = False

        # Health check
        if health <= 0:
            game_over = True
            gameover_sound.play()
            if score > high_score:
                high_score = score
                save_high_score()

    # Draw coins with ₹ symbol
    for cx, cy in coins:
        pygame.draw.circle(screen, (255, 255, 0), (cx - offset_x, cy), coin_radius)
        symbol = coin_font.render("S", True, (0, 0, 0))
        screen.blit(symbol, (cx - offset_x - 7, cy - 10))

    # Draw frog player
    pygame.draw.circle(screen, (0, 200, 0), (player_x - offset_x, player_y), ball_radius)
    pygame.draw.circle(screen, (255, 255, 255), (player_x - offset_x - 7, player_y - 15), eye_radius)
    pygame.draw.circle(screen, (255, 255, 255), (player_x - offset_x + 7, player_y - 15), eye_radius)
    pygame.draw.arc(screen, (0, 0, 0), (player_x - offset_x - 10, player_y - 7, 20, 15), 3.14, 2 * 3.14, 2)

    # Draw enemies (Red snake rectangles)
    for ex, ey, esize in enemies:
          pygame.draw.rect(screen, (255, 0, 0), (ex - offset_x - esize//2, ey - esize//4, esize, esize//2), border_radius=3)

    # Score and health display
    score_text = font.render(f"Score: {score}  High Score: {high_score}  Health: {health}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Menu button
    menu_button = pygame.Rect(screen_width - 100, 10, 90, 40)
    pygame.draw.rect(screen, (100, 100, 255), menu_button)
    menu_text = font.render("Menu", True, (255, 255, 255))
    screen.blit(menu_text, (menu_button.x + 10, menu_button.y + 5))

    if menu_button.collidepoint(mouse_pos) and mouse_click[0]:
        paused = True

    # Pause menu logic
    if paused:
        menu_bg = pygame.Rect(screen_width // 2 - 200, 200, 400, 200)
        pygame.draw.rect(screen, (50, 50, 50), menu_bg)

        play_button = pygame.Rect(screen_width // 2 - 150, 220, 300, 40)
        pygame.draw.rect(screen, (0, 200, 0), play_button)
        play_text = font.render("Play Again", True, (255, 255, 255))
        screen.blit(play_text, (play_button.x + 100, play_button.y + 5))

        resume_button = pygame.Rect(screen_width // 2 - 150, 270, 300, 40)
        pygame.draw.rect(screen, (0, 200, 200), resume_button)
        resume_text = font.render("Resume", True, (255, 255, 255))
        screen.blit(resume_text, (resume_button.x + 110, resume_button.y + 5))

        exit_button = pygame.Rect(screen_width // 2 - 150, 320, 300, 40)
        pygame.draw.rect(screen, (200, 0, 0), exit_button)
        exit_text = font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (exit_button.x + 130, exit_button.y + 5))

        if play_button.collidepoint(mouse_pos) and mouse_click[0]:
            reset_game()
        if resume_button.collidepoint(mouse_pos) and mouse_click[0]:
            paused = False
        if exit_button.collidepoint(mouse_pos) and mouse_click[0]:
            running = False

    # Game over screen
    if game_over:
        over_font = pygame.font.SysFont(None, 75)
        over_text = over_font.render("GAME OVER", True, (255, 255, 255))
        screen.blit(over_text, (screen_width // 2 - 150, 250))

        play_button = pygame.Rect(screen_width // 2 - 150, 350, 300, 40)
        pygame.draw.rect(screen, (0, 200, 0), play_button)
        play_text = font.render("Play Again", True, (255, 255, 255))
        screen.blit(play_text, (play_button.x + 100, play_button.y + 5))

        exit_button = pygame.Rect(screen_width // 2 - 150, 400, 300, 40)
        pygame.draw.rect(screen, (200, 0, 0), exit_button)
        exit_text = font.render("Exit", True, (255, 255, 255))
        screen.blit(exit_text, (exit_button.x + 130, exit_button.y + 5))

        if play_button.collidepoint(mouse_pos) and mouse_click[0]:
            reset_game()
        if exit_button.collidepoint(mouse_pos) and mouse_click[0]:
            running = False

    pygame.display.update()

pygame.quit()

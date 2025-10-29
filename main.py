"""Cyber Space Defender - Prototype (fixed)
Perbaikan: gunakan math.sin, aman untuk pygame.mixer, beberapa safety checks.
"""

import pygame
import sys
import random
import time
import math     

# -----------------------------
# CONFIG / TUNABLE PARAMETERS
# -----------------------------
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
FPS = 60

PLAYER_SPEED = 5
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50  # Ukuran player diperbesar lebih besar
PLAYER_START_POS = (SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 100)  # Posisi awal dinaikkan agar tidak terlalu ke bawah
PLAYER_SHOT_COOLDOWN = 300  # ms

BULLET_SPEED = -10
ENEMY_BULLET_SPEED = 6  # Meningkatkan kecepatan peluru musuh agar lebih mungkin mengenai sprite pemain

LEVEL_TIME_BASE = 45  # seconds for level 1; later levels slightly shorter
MAX_LEVEL = 3

# Visual colors (placeholder assets)
COLOR_BG = (10, 12, 30)
COLOR_PLAYER = (50, 160, 255)
COLOR_ENEMY = (220, 60, 60)
COLOR_BULLET = (255, 230, 100)
COLOR_TEXT = (230, 230, 230)
COLOR_UI = (90, 90, 120)
COLOR_BOSS = (170, 80, 200)
COLOR_COLLECT = (60, 200, 120)

# Story and quizzes (editable)
STORY_DIALOGS = [
    # Intro sequence before level 1
    [
        "— CYBER SPACE DEFENDER —",
        "Kamu adalah Cyber Guardian, pilot kapal kecil yang menjaga ruang siber.",
        "Sebuah AI jahat mulai menyebarkan hoax dan virus. Hentikan mereka!",
        "Tekan Enter untuk memulai misi."
    ]
]

LEVEL_INTROS = {
    1: [
        "Level 1: Spam Invasion",
        "Musuh: Spam bots sederhana. Kumpulkan fakta dan jangan biarkan info palsu menyebar."
    ],
    2: [
        "Level 2: Data Fortress",
        "Musuh lebih kuat. Jaga privasi data dan waspadai jebakan."
    ],
    3: [
        "Level 3: Boss - The Hoax Master",
        "Ini boss yang mengendalikan jaringan hoax. Jawab quiz untuk menembakkan Truth Blaster!"
    ]
}

QUIZ_DATA = {
    1: [
        ("Kamu menerima berita mencurigakan. Apa yang kamu lakukan?",
         ["Langsung bagikan", "Periksa kebenaran dulu", "Simpan untuk nanti"], 1)
    ],
    2: [
        ("Seseorang meminta data pribadimu lewat link yang mencurigakan. Apa langkahmu?",
         ["Isi form untuk cepat", "Tutup dan laporkan", "Berikan data setengahnya"], 1)
    ],
    3: [
        ("Bagaimana cara melawan penyebaran hoax?",
         ["Sebarkan counter-hoax tanpa cek", "Verifikasi fakta dan laporkan", "Abaikan saja"], 1),
        ("Ketika AI memberi saran yang meragukan, apa yang dilakukan?",
         ["Ikuti langsung", "Cek sumber & minta pendapat ahli", "Gunakan untuk trolling"], 1)
    ]
}


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyber Space Defender")
clock = pygame.time.Clock()


try:
    
    player_sprite = pygame.image.load("assets/player.png").convert_alpha()
    player_sprite = pygame.transform.scale(player_sprite, (PLAYER_WIDTH, PLAYER_HEIGHT))
    
    
    enemy_sprite = pygame.image.load("assets/enemy.png").convert_alpha()
    enemy_sprite = pygame.transform.scale(enemy_sprite, (100, 100))  # Enemy lebih besar
    
    
    boss_sprite = pygame.image.load("assets/boss.png").convert_alpha()
    boss_sprite = pygame.transform.scale(boss_sprite, (250, 250))  # Boss jauh lebih besar
except Exception as e:
    print(f"Error loading sprites: {e}")
    player_sprite = enemy_sprite = boss_sprite = None


try:
    background_img = pygame.image.load("assets/background.jpg").convert()
    
    if background_img.get_width() != SCREEN_WIDTH:
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, background_img.get_height()))
    background_y = 0  
    SCROLL_SPEED = 1  
except:
    
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT * 2))
    background_img.fill(COLOR_BG)
    
    for _ in range(100):
        x = random.randint(0, SCREEN_WIDTH-1)
        y = random.randint(0, background_img.get_height()-1)
        pygame.draw.circle(background_img, (255, 255, 255), (x, y), 1)
    background_y = 0
    SCROLL_SPEED = 1


try:
    FONT = pygame.font.SysFont("arial", 18)
    BIG_FONT = pygame.font.SysFont("arial", 28, bold=True)
    TITLE_FONT = pygame.font.SysFont("arial", 36, bold=True)
except Exception:
    
    FONT = pygame.font.Font(None, 18)
    BIG_FONT = pygame.font.Font(None, 28)
    TITLE_FONT = pygame.font.Font(None, 36)

SOUND_SHOT = SOUND_HIT = SOUND_QUIZ_RIGHT = SOUND_QUIZ_WRONG = None
try:
    pygame.mixer.init()
    # If you have real sound files, load them like:
    # SOUND_SHOT = pygame.mixer.Sound("shot.wav")
    # SOUND_HIT = pygame.mixer.Sound("hit.wav")
    # SOUND_QUIZ_RIGHT = pygame.mixer.Sound("right.wav")
    # SOUND_QUIZ_WRONG = pygame.mixer.Sound("wrong.wav")
except Exception:
    # mixer not available or init failed: keep None
    SOUND_SHOT = SOUND_HIT = SOUND_QUIZ_RIGHT = SOUND_QUIZ_WRONG = None


class Player:
    def __init__(self):
        self.rect = pygame.Rect(*PLAYER_START_POS, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.speed = PLAYER_SPEED
        self.last_shot = 0
        self.hp = 3
        self.score = 0
        self.sprite = player_sprite  

    def move(self, dx):
        self.rect.x += dx * self.speed
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def can_shoot(self):
        return pygame.time.get_ticks() - self.last_shot >= PLAYER_SHOT_COOLDOWN

    def shoot(self):
        self.last_shot = pygame.time.get_ticks()
        if SOUND_SHOT:
            try: SOUND_SHOT.play()
            except: pass
        bx = self.rect.centerx
        by = self.rect.top
        return Bullet(bx - 3, by, 6, 12, BULLET_SPEED, color=COLOR_BULLET, owner="player")

class Bullet:
    def __init__(self, x, y, w, h, vy, color=(255,255,255), owner="player", target=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.vy = vy
        self.color = color
        self.owner = owner
        self.target = target  

    def update(self):
        self.rect.y += self.vy
        
        if self.owner == "enemy" and self.target:
           
            bullet_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bullet_surface, self.color, bullet_surface.get_rect())
            bullet_mask = pygame.mask.from_surface(bullet_surface)

            target_mask = pygame.mask.from_surface(self.target.sprite)

            
            offset_x = self.rect.x - self.target.rect.x
            offset_y = self.rect.y - self.target.rect.y

            
            if bullet_mask.overlap(target_mask, (offset_x, offset_y)):
                self.target.hp -= 1  
                return True  
        return False

class Enemy:
    def __init__(self, x, y, w=70, h=70, speed=1.5, hp=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed
        self.hp = hp
        self.dir = random.choice([-1, 1])
        self.sprite = enemy_sprite  

    def update(self):
        self.rect.x += self.speed * self.dir
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.dir *= -1
            self.rect.y += 10

    def shoot_chance(self):
        return random.random() < 0.008

class Boss:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH//2 - 125, 50, 250, 250)  
        self.hp = 6
        self.timer = 0
        self.attack_cooldown = 120
        self.phase = 1
        self.sprite = boss_sprite  

    def update(self):
        
        t = pygame.time.get_ticks() / 800.0
        
        offset = int(100 * (0.5 * (1.0 + math.sin(t))))
        self.rect.x = SCREEN_WIDTH//2 - 120 + offset
        if self.timer > 0:
            self.timer -= 1

    def ready_attack(self):
        return self.timer <= 0

    def set_cooldown(self):
        self.timer = self.attack_cooldown

    def take_damage(self):
        self.hp -= 1


def draw_text(surface, text, x, y, font=FONT, color=COLOR_TEXT):
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))

def center_text(surface, text, y, font=BIG_FONT, color=COLOR_TEXT):
    txt = font.render(text, True, color)
    rect = txt.get_rect(center=(SCREEN_WIDTH//2, y))
    surface.blit(txt, rect)

def draw_hud(player, level, time_left):
    pygame.draw.rect(screen, COLOR_UI, (6, 6, 220, 68), border_radius=6)
    draw_text(screen, f"HP: {player.hp}", 14, 12)
    draw_text(screen, f"Score: {player.score}", 14, 34)
    draw_text(screen, f"Level: {level}", 14, 54)
    timer_text = f"Time: {int(time_left)}s"
    txt = FONT.render(timer_text, True, COLOR_TEXT)
    screen.blit(txt, (SCREEN_WIDTH - txt.get_width() - 12, 14))

def show_dialog(lines):
    idx = 0
    while True:
        if idx >= len(lines):
            break  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    idx += 1
                    break  

      
        if idx >= len(lines):
            break

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((8, 10, 20))
        screen.blit(overlay, (0,0))
        center_text(screen, "STORY", 110, font=TITLE_FONT)
        center_text(screen, lines[idx], 180, font=BIG_FONT)
        draw_text(screen, "Press Enter to continue...", SCREEN_WIDTH - 240, SCREEN_HEIGHT - 40, font=FONT)
        pygame.display.flip()
        clock.tick(FPS)


def show_quiz(quiz_tuple):
    question, options, correct = quiz_tuple
    selected = None
    result = None
    start_time = pygame.time.get_ticks()
    TIMEOUT_MS = 20000
    while result is None:
        elapsed = pygame.time.get_ticks() - start_time
        if elapsed > TIMEOUT_MS:
            result = False
            break
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    selected = 0
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    selected = 1
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    selected = 2
                if selected is not None:
                    result = (selected == correct)
                    if result and SOUND_QUIZ_RIGHT:
                        try: SOUND_QUIZ_RIGHT.play()
                        except: pass
                    if (not result) and SOUND_QUIZ_WRONG:
                        try: SOUND_QUIZ_WRONG.play()
                        except: pass

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(210)
        overlay.fill((6, 8, 18))
        screen.blit(overlay, (0,0))
        center_text(screen, "QUIZ", 100, font=TITLE_FONT)
        qsurf = BIG_FONT.render(question, True, COLOR_TEXT)
        qrect = qsurf.get_rect(center=(SCREEN_WIDTH//2, 180))
        screen.blit(qsurf, qrect)
        y = 260
        for i, opt in enumerate(options):
            prefix = f"{i+1}. "
            line_surf = FONT.render(prefix + opt, True, COLOR_TEXT)
            line_rect = line_surf.get_rect(center=(SCREEN_WIDTH//2, y))
            screen.blit(line_surf, line_rect)
            y += 36
        draw_text(screen, "Press 1 / 2 / 3 to answer. Timeout 20s.", SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT - 40)
        pygame.display.flip()
        clock.tick(FPS)
    return result

def pixel_perfect_collision(sprite1, rect1, sprite2, rect2):
    """Check pixel-perfect collision between two sprites."""
    offset_x = rect2.x - rect1.x
    offset_y = rect2.y - rect1.y
    mask1 = pygame.mask.from_surface(sprite1)
    mask2 = pygame.mask.from_surface(sprite2)
    return mask1.overlap(mask2, (offset_x, offset_y)) is not None


def spawn_enemies_for_level(level):
    enemies = []
    count = 4 + (level - 1) * 3
    for i in range(count):
        x = random.randint(40, SCREEN_WIDTH - 80)
        y = random.randint(10, 150)  # Posisi musuh dinaikkan agar lebih jauh dari pemain
        speed = 1.0 + level * 0.4 + random.random() * 0.5
        hp = 1 + (1 if level > 1 else 0)
        enemies.append(Enemy(x, y, speed=speed, hp=hp))
    return enemies

def run_game():
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    collectables = []
    boss = None

    level = 1
    running = True

    show_dialog(STORY_DIALOGS[0])

    while running and level <= MAX_LEVEL and player.hp > 0:
        enemies = spawn_enemies_for_level(level)
        bullets.clear()
        enemy_bullets.clear()
        collectables.clear()
        boss = Boss() if level == MAX_LEVEL else None
        level_start_time = time.time()
        level_time_limit = max(15, LEVEL_TIME_BASE - (level - 1) * 6)
        if level == 1:
           pygame.mixer.music.load("assets/music_level1.mp3")
        elif level == 2:
           pygame.mixer.music.load("assets/music_level2.mp3")
        elif level == 3:
           pygame.mixer.music.load("assets/boss_theme.mp3")
        pygame.mixer.music.play(-1)

        show_dialog(LEVEL_INTROS[level])
        level_cleared = False

        while True:
            dt = clock.tick(FPS)
            elapsed = time.time() - level_start_time
            time_left = max(0, level_time_limit - elapsed)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.move(-1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.move(1)
            if keys[pygame.K_SPACE]:
                if player.can_shoot():
                    bullets.append(player.shoot())

            # Update bullets
            for b in bullets[:]:
                b.update()
                if b.rect.bottom < 0:
                    try:
                        bullets.remove(b)
                    except ValueError:
                        pass

            for eb in enemy_bullets[:]:
                eb.update()
                if eb.rect.top > SCREEN_HEIGHT:
                    try:
                        enemy_bullets.remove(eb)
                    except ValueError:
                        pass

            
            for en in enemies[:]:
                en.update()
                if en.shoot_chance():
                    ex = en.rect.centerx
                    ey = en.rect.bottom
                    enemy_bullets.append(Bullet(ex, ey, 6, 12, ENEMY_BULLET_SPEED, color=(255,180,90), owner="enemy"))
                for b in bullets[:]:
                    if b.rect.colliderect(en.rect):
                        en.hp -= 1
                        try:
                            bullets.remove(b)
                        except ValueError:
                            pass
                        if SOUND_HIT:
                            try: SOUND_HIT.play()
                            except: pass
                        if en.hp <= 0:
                            try:
                                enemies.remove(en)
                            except ValueError:
                                pass
                            player.score += 10
                            if random.random() < 0.15:
                                cx = en.rect.centerx
                                cy = en.rect.centery
                                collectables.append(pygame.Rect(cx-8, cy-8, 16, 16))
                        break

            
            for eb in enemy_bullets[:]:
                if eb.rect.colliderect(player.rect):
                    player.hp -= 1
                    try:
                        enemy_bullets.remove(eb)
                    except ValueError:
                        pass
                    player.rect.topleft = PLAYER_START_POS
                    if SOUND_HIT:
                        try: SOUND_HIT.play()
                        except: pass

            # Collectables pickup
            for c in collectables[:]:
                if player.rect.colliderect(c):
                    player.score += 5
                    try:
                        collectables.remove(c)
                    except ValueError:
                        pass

            # Boss logic
            if boss:
                boss.update()
                if boss.ready_attack() and random.random() < 0.02:
                    for i in range(5):
                        bx = boss.rect.left + 20 + i*(boss.rect.width // 5)
                        by = boss.rect.bottom
                        enemy_bullets.append(Bullet(bx, by, 8, 12, ENEMY_BULLET_SPEED + 1, color=(240,120,120), owner="enemy"))
                    boss.set_cooldown()
                for b in bullets[:]:
                    if b.rect.colliderect(boss.rect):
                        try:
                            bullets.remove(b)
                        except ValueError:
                            pass
                        player.score += 1

            # Level cleared
            if not enemies and not boss:
                center_text(screen, "LEVEL CLEARED!", SCREEN_HEIGHT//2 - 40, font=TITLE_FONT)
                pygame.display.flip()
                pygame.time.delay(700)
                quiz_list = QUIZ_DATA.get(level, [])
                if quiz_list:
                    quiz_choice = random.choice(quiz_list)
                    correct = show_quiz(quiz_choice)
                else:
                    correct = True
                if correct:
                    level += 1
                    level_cleared = True
                    break
                else:
                    player.hp -= 1
                    player.rect.topleft = PLAYER_START_POS
                    enemies = spawn_enemies_for_level(level)
                    bullets.clear()
                    enemy_bullets.clear()
                    collectables.clear()
                    if player.hp <= 0:
                        break

            # Boss quiz mechanic during fight
            if boss:
                if random.random() < 0.0025:
                    quiz_choice = random.choice(QUIZ_DATA.get(3, []))
                    if quiz_choice:
                        correct = show_quiz(quiz_choice)
                        if correct:
                            boss.take_damage()
                            center_text(screen, "TRUTH HIT!", SCREEN_HEIGHT//2 - 60, font=BIG_FONT)
                            pygame.display.flip()
                            pygame.time.delay(700)
                        else:
                            player.hp -= 1
                            player.rect.topleft = PLAYER_START_POS
                        if boss.hp <= 0:
                            center_text(screen, "BOSS DOWN!", SCREEN_HEIGHT//2 - 40, font=TITLE_FONT)
                            pygame.display.flip()
                            pygame.time.delay(800)
                            level += 1
                            level_cleared = True
                            break

            # Time up
            if time_left <= 0:
                player.hp -= 1
                player.rect.topleft = PLAYER_START_POS
                enemies = spawn_enemies_for_level(level)
                bullets.clear()
                enemy_bullets.clear()
                collectables.clear()
                if player.hp <= 0:
                    break

            # Drawing
            # Draw scrolling background
            global background_y
            # Draw background twice to create seamless scroll
            screen.blit(background_img, (0, background_y))
            screen.blit(background_img, (0, background_y - background_img.get_height()))
            # Update scroll position
            background_y = (background_y + SCROLL_SPEED) % background_img.get_height()

            # Draw player
            if player.sprite:
                screen.blit(player.sprite, player.rect)
            else:
                pygame.draw.rect(screen, COLOR_PLAYER, player.rect)
                pygame.draw.rect(screen, (255,255,255), (player.rect.centerx - 6, player.rect.top - 6, 12, 6))

            # Draw bullets
            for b in bullets:
                pygame.draw.rect(screen, b.color, b.rect)
            for eb in enemy_bullets:
                pygame.draw.rect(screen, eb.color, eb.rect)

            # Draw enemies
            for en in enemies:
                if en.sprite:
                    screen.blit(en.sprite, en.rect)
                else:
                    pygame.draw.rect(screen, COLOR_ENEMY, en.rect)
            
            # Draw boss
            if boss:
                if boss.sprite:
                    screen.blit(boss.sprite, boss.rect)
                else:
                    pygame.draw.rect(screen, COLOR_BOSS, boss.rect)
                bar_w = 200
                bar_x = SCREEN_WIDTH//2 - bar_w//2
                pygame.draw.rect(screen, (60,60,60), (bar_x, 12, bar_w, 18))
                if boss.hp > 0:
                    inner = int((boss.hp / 6.0) * (bar_w - 4))
                    pygame.draw.rect(screen, (200, 80, 200), (bar_x + 2, 14, inner, 14))

            for c in collectables:
                pygame.draw.rect(screen, COLOR_COLLECT, c)

            draw_hud(player, level, time_left)
            draw_text(screen, "Controls: ←/A, →/D, Space=Shoot. Answer quizzes with 1/2/3.", 12, SCREEN_HEIGHT - 28, font=FONT)
            pygame.display.flip()

            if player.hp <= 0:
                break

        if player.hp <= 0:
            break
        if level > MAX_LEVEL:
            break

    # End of game screen
    screen.fill(COLOR_BG)
    if player.hp > 0:
        center_text(screen, "CONGRATULATIONS - You saved the digital world!", SCREEN_HEIGHT//2 - 20, font=BIG_FONT)
        center_text(screen, f"Final Score: {player.score}", SCREEN_HEIGHT//2 + 30, font=BIG_FONT)
    else:
        center_text(screen, "GAME OVER", SCREEN_HEIGHT//2 - 20, font=BIG_FONT)
        center_text(screen, "Hoax prevailed... Try again!", SCREEN_HEIGHT//2 + 30, font=BIG_FONT)
    draw_text(screen, "Press Enter to exit.", SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT - 60)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    waiting = False
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

def show_main_menu():
    print("Starting main menu...")  # Debug log
    try:
        # Load menu assets
        menu_bg = pygame.image.load("assets/tampilan awal.png").convert()
        menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        play_button = pygame.image.load("assets/Play.png").convert_alpha()
        about_button = pygame.image.load("assets/About me.png").convert_alpha()
        
        # Button sizes and scaling
        button_width, button_height = 200, 80
        play_button = pygame.transform.scale(play_button, (button_width, button_height))
        about_button = pygame.transform.scale(about_button, (button_width, button_height))
        
        # Button positions (adjusted to be more visible)
        play_button_rect = play_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        about_button_rect = about_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        
        print("Menu assets loaded successfully")  # Debug log
        
        # Play menu music once
        try:
            pygame.mixer.music.load("assets/music_level1.mp3")
            pygame.mixer.music.play(-1)  # Loop the music
        except Exception as e:
            print(f"Warning: Could not play menu music: {e}")
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        return "play"
                    elif about_button_rect.collidepoint(event.pos):
                        return "about"

            # Draw the menu
            screen.blit(menu_bg, (0, 0))
            screen.blit(play_button, play_button_rect)
            screen.blit(about_button, about_button_rect)
            
            # Draw text to indicate clickable buttons
            font = pygame.font.SysFont(None, 24)
            instruction = font.render("Click a button to continue", True, (255, 255, 255))
            instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            screen.blit(instruction, instruction_rect)
            
            pygame.display.flip()
            clock.tick(FPS)
            
    except Exception as e:
        print(f"Error loading menu assets: {e}")
        return "quit"

def show_about_me():
    print("Opening About Me screen...")  # Debug log
    try:
        # Load and scale about image
        about_image = pygame.image.load("assets/Perkenalan.png").convert()
        about_image = pygame.transform.scale(about_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("About Me image loaded successfully")  # Debug log
        
        # Create back button text
        font = pygame.font.SysFont(None, 36)
        text = font.render("Press ESC to return to menu", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("Returning to main menu...")  # Debug log
                        return "menu"
            
            # Draw about screen
            screen.blit(about_image, (0, 0))
            screen.blit(text, text_rect)
            pygame.display.flip()
            clock.tick(60)
            
    except Exception as e:
        print(f"Error in About Me screen: {e}")
        return "menu"

if __name__ == "__main__":
    # Initialize pygame and display
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cyber Space Defender")
    clock = pygame.time.Clock()

    # Main program loop
    current_screen = "menu"
    running = True
    
    while running:
        if current_screen == "menu":
            choice = show_main_menu()
            print(f"Menu selection: {choice}")  # Debug log
            if choice == "play":
                run_game()
                current_screen = "menu"  # Return to menu after game
            elif choice == "about":
                current_screen = "about"
            elif choice == "quit":
                running = False
        elif current_screen == "about":
            result = show_about_me()
            if result == "menu":
                current_screen = "menu"
            elif result == "quit":
                running = False
    
    pygame.quit()
    sys.exit()  # Kembali ke menu utama setelah keluar dari about me

import pygame
import sys
import random
import time
import math     


SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
FPS = 60

PLAYER_SPEED = 5
PLAYER_WIDTH, PLAYER_HEIGHT = 75, 75
PLAYER_START_POS = (SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 100)
PLAYER_SHOT_COOLDOWN = 300

BULLET_SPEED = -10
ENEMY_BULLET_SPEED = 6

LEVEL_TIME_BASE = 45
MAX_LEVEL = 3

COLOR_BG = (10, 12, 30)
COLOR_PLAYER = (50, 160, 255)
COLOR_ENEMY = (220, 60, 60)
COLOR_BULLET = (255, 230, 100)
COLOR_TEXT = (230, 230, 230)
COLOR_UI = (90, 90, 120)
COLOR_BOSS = (170, 80, 200)
COLOR_COLLECT = (60, 200, 120)

STORY_DIALOGS = [
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
        "ini adalah musuhmu di level 1",
        "Musuh: Spam bots sederhana. Kumpulkan fakta dan jangan biarkan info palsu menyebar. ",
        "serang menggunakan space dan bergerak menggunakan a/d"
    ],
    2: [
        "Level 2: Data Fortress",
        "ini adalah musuhmu di level 2",
        "Musuh lebih kuat. Jaga privasi data dan waspadai jebakan.",
        "serang menggunakan space dan bergerak menggunakan a/d"
    ],
    3: [
        "Level 3: Boss - The Hoax Master",
        "ini adalah boss yang akan kamu hadapi",
        "boss ini yang mengendalikan jaringan hoax. Jawab quiz untuk menembakkan Truth Blaster!"
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


icon = pygame.image.load("assets/logo2.png")
pygame.display.set_icon(icon)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyber Space Defender")
clock = pygame.time.Clock()


try:
    player_sprite = pygame.image.load("assets/player.png").convert_alpha()
    player_sprite = pygame.transform.scale(player_sprite, (PLAYER_WIDTH, PLAYER_HEIGHT))

    # Load level-specific enemy sprites (fall back to generic if not present)
    try:
        enemy_lvl1_sprite = pygame.image.load("assets/enemy_level_1.png").convert_alpha()
        enemy_lvl1_sprite = pygame.transform.scale(enemy_lvl1_sprite, (90, 90))
    except Exception:
        enemy_lvl1_sprite = None

    try:
        enemy_lvl2_sprite = pygame.image.load("assets/enemy_level_2.png").convert_alpha()
        enemy_lvl2_sprite = pygame.transform.scale(enemy_lvl2_sprite, (100, 100))
    except Exception:
        enemy_lvl2_sprite = None

    # Generic enemy sprite for backwards compatibility
    try:
        enemy_sprite = pygame.image.load("assets/enemy.png").convert_alpha()
        enemy_sprite = pygame.transform.scale(enemy_sprite, (100, 100))
    except Exception:
        # if no generic, prefer level1 or level2
        enemy_sprite = enemy_lvl1_sprite or enemy_lvl2_sprite

    boss_sprite = pygame.image.load("assets/boss.png").convert_alpha()
    boss_sprite = pygame.transform.scale(boss_sprite, (350, 350))
except Exception as e:
    print(f"Error loading sprites: {e}")
    player_sprite = enemy_sprite = boss_sprite = None
    # ensure level-specific variables exist
    try:
        enemy_lvl1_sprite
    except NameError:
        enemy_lvl1_sprite = None
    try:
        enemy_lvl2_sprite
    except NameError:
        enemy_lvl2_sprite = None


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

SOUND_SHOT = SOUND_HIT = SOUND_QUIZ_RIGHT = SOUND_QUIZ_WRONG = SOUND_BUTTON = None

try:
    pygame.mixer.init()
    try:
        SOUND_SHOT = pygame.mixer.Sound("assets/shot.mp3")
        SOUND_HIT = pygame.mixer.Sound("assets/hit.mp3")
        SOUND_QUIZ_RIGHT = pygame.mixer.Sound("assets/right.mp3")
        SOUND_QUIZ_WRONG = pygame.mixer.Sound("assets/wrong.mp3")
        SOUND_BUTTON = pygame.mixer.Sound("assets/button.mp3")
        
        for sound in [SOUND_SHOT, SOUND_HIT, SOUND_QUIZ_RIGHT, SOUND_QUIZ_WRONG, SOUND_BUTTON]:
            if sound:
                sound.set_volume(0.5)
    except Exception as e:
        print(f"Warning: Could not load some sound files: {e}")
except Exception as e:
    print(f"Warning: Could not initialize sound mixer: {e}")
    SOUND_SHOT = SOUND_HIT = SOUND_QUIZ_RIGHT = SOUND_QUIZ_WRONG = SOUND_BUTTON = None


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
    story_bg = pygame.image.load("assets/story.png").convert()
    story_bg = pygame.transform.scale(story_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    char_index = 0
    char_speed = 2  # Karakter per frame
    char_timer = 0
    current_text = ""
    text_complete = False

    while True:
        if idx >= len(lines):
            break  

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if text_complete:
                        idx += 1
                        char_index = 0
                        current_text = ""
                        text_complete = False
                    else:
                        # Tampilkan semua teks jika masih berjalan
                        char_index = len(lines[idx])
                        text_complete = True
                    break  
        
        if idx >= len(lines):
            break

        screen.blit(story_bg, (0, 0))
        
        if idx == 0:  # Judul
            center_text(screen, lines[idx], 180, font=TITLE_FONT)
            text_complete = True
        else:  # Cerita
            # Area teks di bagian bawah layar
            text_area_y = SCREEN_HEIGHT - 150  # Posisi y di bagian bawah
            
            # Update teks yang sedang berjalan
            if not text_complete:
                char_timer += 1
                if char_timer >= char_speed:
                    char_timer = 0
                    if char_index < len(lines[idx]):
                        current_text += lines[idx][char_index]
                        char_index += 1
                    else:
                        text_complete = True
            else:
                current_text = lines[idx]
            
            # Membuat background semi-transparan untuk teks
            text_bg = pygame.Surface((SCREEN_WIDTH, 100))
            text_bg.fill((0, 0, 0))
            text_bg.set_alpha(128)  # 50% transparan
            screen.blit(text_bg, (0, text_area_y - 20))
            
            # Render teks cerita
            text_lines = []
            words = current_text.split()
            current_line = []
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                if BIG_FONT.size(test_line)[0] > 800:  # Batas lebar teks
                    text_lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                text_lines.append(' '.join(current_line))
            
            # Menampilkan teks per baris
            y_offset = text_area_y
            for line in text_lines:
                text_surf = BIG_FONT.render(line, True, (255, 255, 255))  # Warna teks putih
                text_pos = text_surf.get_rect(centerx=SCREEN_WIDTH//2, top=y_offset)
                screen.blit(text_surf, text_pos)
                y_offset += 30

        # Instruksi untuk melanjutkan
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
        y = random.randint(10, 150)
        speed = 1.0 + level * 0.4 + random.random() * 0.5
        hp = 1 + (1 if level > 1 else 0)

        enemy = Enemy(x, y, speed=speed, hp=hp)

        # === GANTI SPRITE SESUAI LEVEL ===
        if level == 1 and enemy_lvl1_sprite:
            enemy.sprite = enemy_lvl1_sprite
        elif level == 2 and enemy_lvl2_sprite:
            enemy.sprite = enemy_lvl2_sprite
        elif level == 3 and enemy_lvl2_sprite:
            enemy.sprite = enemy_lvl2_sprite
        
        else:
            enemy.sprite = None  # fallback kalau belum ada sprite

        enemies.append(enemy)
    return enemies



def run_game():
    global SOUND_SHOT, SOUND_HIT, SOUND_QUIZ_RIGHT, SOUND_QUIZ_WRONG, SOUND_BUTTON
    
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
        
        if level == MAX_LEVEL:  
            level_time_limit = 60  
        else:
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

            
            for c in collectables[:]:
                if player.rect.colliderect(c):
                    player.score += 5
                    try:
                        collectables.remove(c)
                    except ValueError:
                        pass

            
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

            
            if time_left <= 0:
                player.hp -= 1
                player.rect.topleft = PLAYER_START_POS
                enemies = spawn_enemies_for_level(level)
                bullets.clear()
                enemy_bullets.clear()
                collectables.clear()
                if player.hp <= 0:
                    break

            
            global background_y
            
            screen.blit(background_img, (0, background_y))
            screen.blit(background_img, (0, background_y - background_img.get_height()))
            
            background_y = (background_y + SCROLL_SPEED) % background_img.get_height()

            
            if player.sprite:
                screen.blit(player.sprite, player.rect)
            else:
                pygame.draw.rect(screen, COLOR_PLAYER, player.rect)
                pygame.draw.rect(screen, (255,255,255), (player.rect.centerx - 6, player.rect.top - 6, 12, 6))

            
            for b in bullets:
                pygame.draw.rect(screen, b.color, b.rect)
            for eb in enemy_bullets:
                pygame.draw.rect(screen, eb.color, eb.rect)

            
            for en in enemies:
                if en.sprite:
                    screen.blit(en.sprite, en.rect)
                else:
                    pygame.draw.rect(screen, COLOR_ENEMY, en.rect)
                
                bar_width = en.rect.width
                bar_height = 5
                bar_x = en.rect.x
                bar_y = en.rect.y - 10
                
                pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
                
                if en.hp > 0:
                    current_health_width = int((en.hp / (2 if level > 1 else 1)) * bar_width)
                    pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, current_health_width, bar_height))
            
            
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

    
    screen.fill(COLOR_BG)
    if player.hp > 0:
        center_text(screen, "CONGRATULATIONS - You saved the digital world!", SCREEN_HEIGHT//2 - 40, font=BIG_FONT)
        center_text(screen, f"Final Score: {player.score}", SCREEN_HEIGHT//2, font=BIG_FONT)
    else:
        center_text(screen, "GAME OVER", SCREEN_HEIGHT//2 - 40, font=BIG_FONT)
        center_text(screen, "Hoax prevailed... Try again!", SCREEN_HEIGHT//2, font=BIG_FONT)
    center_text(screen, "Press ENTER to return to Main Menu", SCREEN_HEIGHT//2 + 60, font=FONT)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if SOUND_BUTTON:
                        try: SOUND_BUTTON.play()
                        except: pass
                    return "menu"
        clock.tick(FPS)

def show_main_menu():
    try:
        
        menu_bg = pygame.image.load("assets/tampilan awal.png").convert()
        menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        play_button = pygame.image.load("assets/Play.png").convert_alpha()
        about_button = pygame.image.load("assets/About me.png").convert_alpha()
        
        
        normal_width, normal_height = 300, 100
        hover_width, hover_height = 330, 110  
        
        
        play_button_normal = pygame.transform.scale(play_button, (normal_width, normal_height))
        about_button_normal = pygame.transform.scale(about_button, (normal_width, normal_height))
        
        
        play_button_hover = pygame.transform.scale(play_button, (hover_width, hover_height))
        about_button_hover = pygame.transform.scale(about_button, (hover_width, hover_height))
        
        
        exit_font = pygame.font.SysFont(None, 48)
        exit_button_normal = pygame.Surface((200, 60), pygame.SRCALPHA)
        exit_button_hover = pygame.Surface((220, 66), pygame.SRCALPHA)
        
        
        pygame.draw.rect(exit_button_normal, (100, 100, 100, 180), exit_button_normal.get_rect(), border_radius=10)
        exit_text = exit_font.render("Exit Game", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=(exit_button_normal.get_width()//2, exit_button_normal.get_height()//2))
        exit_button_normal.blit(exit_text, exit_text_rect)
        
        
        pygame.draw.rect(exit_button_hover, (120, 120, 120, 180), exit_button_hover.get_rect(), border_radius=12)
        exit_text_hover = exit_font.render("Exit Game", True, (255, 255, 255))
        exit_text_hover_rect = exit_text_hover.get_rect(center=(exit_button_hover.get_width()//2, exit_button_hover.get_height()//2))
        exit_button_hover.blit(exit_text_hover, exit_text_hover_rect)
        
        
        play_button_rect = play_button_normal.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        about_button_rect = about_button_normal.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 175))
        exit_button_rect = exit_button_normal.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 220))
        
        print("Menu assets loaded successfully")  
        
        
        try:
            pygame.mixer.music.load("assets/music_level1.mp3")
            pygame.mixer.music.play(-1)  
        except Exception as e:
            print(f"Warning: Could not play menu music: {e}")
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            play_hovered = play_button_rect.collidepoint(mouse_pos)
            about_hovered = about_button_rect.collidepoint(mouse_pos)
            exit_hovered = exit_button_rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if SOUND_BUTTON:
                            try: SOUND_BUTTON.play()
                            except: pass
                        return "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect.collidepoint(event.pos):
                        if SOUND_BUTTON:
                            try: SOUND_BUTTON.play()
                            except: pass
                        return "play"
                    elif about_button_rect.collidepoint(event.pos):
                        if SOUND_BUTTON:
                            try: SOUND_BUTTON.play()
                            except: pass
                        return "about"
                    elif exit_button_rect.collidepoint(event.pos):
                        if SOUND_BUTTON:
                            try: SOUND_BUTTON.play()
                            except: pass
                        return "quit"

            
            screen.blit(menu_bg, (0, 0))
            
            
            if play_hovered:
                hover_rect = play_button_hover.get_rect(center=play_button_rect.center)
                screen.blit(play_button_hover, hover_rect)
            else:
                screen.blit(play_button_normal, play_button_rect)
                
            if about_hovered:
                hover_rect = about_button_hover.get_rect(center=about_button_rect.center)
                screen.blit(about_button_hover, hover_rect)
            else:
                screen.blit(about_button_normal, about_button_rect)
            
            
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
    try:
        about_image = pygame.image.load("assets/Perkenalan.png").convert()
        about_image = pygame.transform.scale(about_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        
        font = pygame.font.SysFont(None, 36)
        text = font.render("Press ESC to return to menu", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50))
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
            
            
            screen.blit(about_image, (0, 0))
            screen.blit(text, text_rect)
            pygame.display.flip()
            clock.tick(60)
            
    except Exception as e:
        print(f"Error in About Me screen: {e}")
        return "menu"

if __name__ == "__main__":
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cyber Space Defender")
    clock = pygame.time.Clock()

    
    current_screen = "menu"
    running = True
    
    while running:
        if current_screen == "menu":
            choice = show_main_menu()
            if choice == "play":
                run_game()
                current_screen = "menu"
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
    sys.exit()

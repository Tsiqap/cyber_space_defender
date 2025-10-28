import pygame, random, sys, os

pygame.init()

# === SETUP DASAR ===
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Space Defender")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# === LOAD GAMBAR ===
# Robust image loading: use absolute paths relative to this file and fallback to a
# visible placeholder surface if loading fails. This avoids errors when the
# current working directory differs from the script directory.
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

def _load_image(filename, fallback_size=(64,64)):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception as e:
        print(f"Warning: gagal memuat '{path}': {e}")
        # create magenta-transparent placeholder so it's obvious in the game
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 180))
        pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
        return surf

# Scale images relative to screen size to avoid oversized sprites causing early collisions.
def _scale_image(img, target_w):
    w, h = img.get_width(), img.get_height()
    if w == 0:
        return img
    scale = target_w / w
    return pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))

player_img = _load_image("player.png", fallback_size=(64,64))
enemy_img = _load_image("enemy.png", fallback_size=(48,48))
boss_img = _load_image("boss.png", fallback_size=(160,120))

player_img = _scale_image(player_img, max(24, WIDTH // 12))
enemy_img = _scale_image(enemy_img, max(20, WIDTH // 14))
boss_img = _scale_image(boss_img, max(80, WIDTH // 4))



# === LOAD MUSIK UNTUK SETIAP LEVEL ===
music_files = [
    "assets/music_level1.mp3",
    "assets/music_level2.mp3",
    "assets/boss_theme.mp3"
]

# === ENTITY SETUP ===
player = player_img.get_rect(center=(WIDTH//2, HEIGHT - 80))
enemies = []
level = 1
player_life = 3
start_time = pygame.time.get_ticks()  # Track game start time
invincible_duration = 2000  # 2 seconds of invincibility at start

# Boss
boss = boss_img.get_rect(center=(WIDTH//2, -150))
boss_health = 15
boss_active = False
boss_speed = 2

# === QUIZ DATA ===
quizzes = [
    {
        "q": "Apa yang harus dilakukan sebelum membagikan berita di internet?",
        "a": ["Periksa kebenarannya dulu", "Langsung bagikan", "Tambahkan hoax"],
        "correct": 0
    },
    {
        "q": "Kalau ada komentar jahat di medsos, apa yang sebaiknya kamu lakukan?",
        "a": ["Balas dengan kasar", "Laporkan dan tetap sopan", "Sebar balik"],
        "correct": 1
    }
]

# === FUNGSI ===
def play_music(index):
    pygame.mixer.music.load(music_files[index])
    pygame.mixer.music.play(-1)

def spawn_enemy():
    enemies.clear()
    print(f"Spawning enemies... Player at y={player.y}")  # Debug print
    for i in range(5 + level * 2):
        # create rect from image and place it fully above the top of the screen
        rect = enemy_img.get_rect()
        rect.centerx = random.randint(40, WIDTH - 40)
        # ensure the enemy starts much higher off-screen
        rect.y = -rect.height - random.randint(300, 800)  # Increased height range
        print(f"Enemy {i} spawned at y={rect.y}")  # Debug print
        enemies.append(rect)

def show_text(text, y=300, color=(255,255,255)):
    label = font.render(text, True, color)
    screen.blit(label, (WIDTH//2 - label.get_width()//2, y))

def show_quiz(qdata):
    running = True
    selected = -1
    while running:
        screen.fill((0,0,0))
        show_text(qdata["q"], 100)
        for i, ans in enumerate(qdata["a"]):
            color = (255,255,255)
            if i == selected:
                color = (0,255,0)
            show_text(f"{i+1}. {ans}", 200 + i*60, color)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    selected = int(event.unicode) - 1
                    if selected == qdata["correct"]:
                        return True
                    else:
                        return False

# === CERITA PEMBUKA ===
screen.fill((0, 0, 0))
show_text("🌐 Dunia digital diserang oleh AI penyebar hoax!", 250)
show_text("Kau adalah CYBER DEFENDER!", 300)
show_text("Gunakan pengetahuanmu untuk melindungi dunia maya.", 350)
pygame.display.flip()
pygame.time.wait(4000)

# === GAME MULAI ===
play_music(0)
spawn_enemy()

running = True
while running:
    screen.fill((0,0,0) )
    screen.blit(player_img, player)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    # Gerak pemain
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= 5
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += 5
    if keys[pygame.K_UP] and player.top > 0:
        player.y -= 5
    if keys[pygame.K_DOWN] and player.bottom < HEIGHT:
        player.y += 5

    # Gerak musuh
    current_time = pygame.time.get_ticks()
    is_invincible = current_time - start_time < invincible_duration

    if not boss_active:
        for enemy in enemies[:]:
            enemy.y += 4
            screen.blit(enemy_img, enemy)
            # remove enemy when it goes off the bottom
            if enemy.top > HEIGHT:
                enemies.remove(enemy)
                continue
            # only detect collisions once the enemy has entered the visible screen
            # and player is not invincible
            if enemy.bottom > 0 and not is_invincible and enemy.colliderect(player):
                print(f"Collision! Enemy at y={enemy.y}, Player at y={player.y}")  # Debug print
                player_life -= 1
                enemies.remove(enemy)
                if player_life <= 0:
                    screen.fill((0,0,0))
                    show_text("GAME OVER", 300, (255, 0, 0))
                    pygame.display.flip()
                    pygame.time.wait(2500)
                    pygame.quit(); sys.exit()

    # Jika semua musuh hilang, naik level
    if not enemies and not boss_active:
        if level < 3: 
            level += 1 
            play_music(level-1)
            if level == 3:
                boss_active = True
            else:
                if show_quiz(quizzes[(level-2) % len(quizzes)]):
                    spawn_enemy()
                else:
                    show_text("Jawaban salah! Coba lagi.", 300, (255,0,0))
                    pygame.display.flip()
                    pygame.time.wait(1500)
                    spawn_enemy()

    # Boss battle (level 3)
    if boss_active:
        boss.y += boss_speed
        if boss.top <= 50 or boss.bottom >= 250:
            boss_speed *= -1
        screen.blit(boss_img, boss)
        pygame.draw.rect(screen, (255,0,0), (boss.x, boss.y-10, 150, 10))
        pygame.draw.rect(screen, (0,255,0), (boss.x, boss.y-10, 150 * (boss_health/15), 10))
        
        # boss damage otomatis seiring waktu
        boss_health -= 0.02
        if boss.colliderect(player):
            player_life -= 1
            if player_life <= 0:
                screen.fill((0,0,0))
                show_text("KALAH! Dunia digital dikuasai AI!", 300, (255,0,0))
                pygame.display.flip()
                pygame.time.wait(2500)
                pygame.quit(); sys.exit()

        if boss_health <= 0:
            screen.fill((0,0,0))
            show_text("🎉 KAMU MENANG!", 280, (0,255,0))
            show_text("Dunia digital aman kembali!", 330, (0,255,0))
            pygame.display.flip()
            pygame.time.wait(4000)
            pygame.quit(); sys.exit()

    # UI tampilan
    show_text(f"Life: {player_life}", 30, (255,255,255))
    show_text(f"Level: {level}", 60, (255,255,255))

    pygame.display.flip()
    clock.tick(60)

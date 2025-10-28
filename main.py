import pygame, random, sys

pygame.init()

# === SETUP DASAR ===
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Space Defender")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# === LOAD GAMBAR ===
player_img = pygame.image.load("assets/player.png").convert_alpha()
enemy_img = pygame.image.load("assets/enemy.png").convert_alpha()
boss_img = pygame.image.load("assets/boss.png").convert_alpha()



# === LOAD MUSIK UNTUK SETIAP LEVEL ===
music_files = [
    "assets/music_level1.mp3",
    "assets/music_level2.mp3",
    "assets/music_boss.mp3"
]

# === ENTITY SETUP ===
player = player_img.get_rect(center=(WIDTH//2, HEIGHT - 80))
enemies = []
level = 1
player_life = 3

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
    for i in range(5 + level * 2):
        rect = enemy_img.get_rect(center=(random.randint(40, WIDTH-40), random.randint(-150, -40)))
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
    if not boss_active:
        for enemy in enemies[:]:
            enemy.y += 4
            screen.blit(enemy_img, enemy)
            if enemy.top > HEIGHT:
                enemies.remove(enemy)
            if enemy.colliderect(player):
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

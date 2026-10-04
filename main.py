import math
import random
import pygame


# ============================================================
# CONFIGURATION
# ============================================================

GAME_WIDTH = 1280
GAME_HEIGHT = 720

SSAA = 2

RENDER_WIDTH = GAME_WIDTH * SSAA
RENDER_HEIGHT = GAME_HEIGHT * SSAA

FPS = 165

MOVEMENT_BPM = 256
CLICK_BPM = 128

NODE_COUNT = 120

PLAYER_RADIUS = 15
PLAYER_SPEED = 420.0

MIN_NODE_DISTANCE = 45.0

# Movement mode has to be reachable at 256 BPM.
MOVEMENT_BEAT = 60.0 / MOVEMENT_BPM
MAX_NODE_DISTANCE = PLAYER_SPEED * MOVEMENT_BEAT * 0.45

# Distance judgement windows.
PERFECT_DISTANCE = 25.0
GOOD_DISTANCE = 50.0
BAD_DISTANCE = 80.0

# Click timing windows.
CLICK_PERFECT = 0.045
CLICK_GOOD = 0.090
CLICK_BAD = 0.140


# ============================================================
# UTILITY
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def draw_text(
    surface,
    text,
    font,
    x,
    y,
    color=(255, 255, 255),
    center=False
):
    image = font.render(str(text), True, color)

    if center:
        rect = image.get_rect(
            center=(int(x), int(y))
        )
    else:
        rect = image.get_rect(
            topleft=(int(x), int(y))
        )

    surface.blit(image, rect)


# ============================================================
# LEVEL GENERATION
# ============================================================

def generate_level():

    nodes = []

    x = GAME_WIDTH / 2
    y = GAME_HEIGHT / 2

    nodes.append((x, y))

    for _ in range(NODE_COUNT - 1):

        previous_x, previous_y = nodes[-1]

        candidates = []

        for _ in range(100):

            angle = random.uniform(
                0.0,
                math.tau
            )

            node_distance = random.uniform(
                MIN_NODE_DISTANCE,
                MAX_NODE_DISTANCE
            )

            nx = (
                previous_x
                + math.cos(angle) * node_distance
            )

            ny = (
                previous_y
                + math.sin(angle) * node_distance
            )

            margin = 70

            nx = clamp(
                nx,
                margin,
                GAME_WIDTH - margin
            )

            ny = clamp(
                ny,
                margin,
                GAME_HEIGHT - margin
            )

            valid = True

            for old_x, old_y in nodes[-8:]:

                if distance(
                    nx,
                    ny,
                    old_x,
                    old_y
                ) < MIN_NODE_DISTANCE:

                    valid = False
                    break

            if valid:
                candidates.append(
                    (nx, ny)
                )

        if candidates:

            nodes.append(
                random.choice(candidates)
            )

        else:

            angle = random.uniform(
                0.0,
                math.tau
            )

            nx = (
                previous_x
                + math.cos(angle)
                * MAX_NODE_DISTANCE
            )

            ny = (
                previous_y
                + math.sin(angle)
                * MAX_NODE_DISTANCE
            )

            nx = clamp(
                nx,
                70,
                GAME_WIDTH - 70
            )

            ny = clamp(
                ny,
                70,
                GAME_HEIGHT - 70
            )

            nodes.append(
                (nx, ny)
            )

    return nodes


# ============================================================
# PARTICLES
# ============================================================

class Particle:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        angle = random.uniform(
            0.0,
            math.tau
        )

        speed = random.uniform(
            50.0,
            220.0
        )

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.uniform(
            0.25,
            0.65
        )

        self.max_life = self.life

        self.radius = random.uniform(
            2.0,
            5.0
        )

        self.color = (
            int(clamp(color[0], 0, 255)),
            int(clamp(color[1], 0, 255)),
            int(clamp(color[2], 0, 255))
        )

    def update(self, dt):

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vx *= 0.96
        self.vy *= 0.96

        self.life -= dt

    def draw(self, surface):

        if self.life <= 0:
            return

        life_ratio = clamp(
            self.life / self.max_life,
            0.0,
            1.0
        )

        alpha = int(
            255 * life_ratio
        )

        radius = max(
            1,
            int(self.radius * life_ratio)
        )

        size = radius * 2 + 4

        particle_surface = pygame.Surface(
            (size, size),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (
                self.color[0],
                self.color[1],
                self.color[2],
                alpha
            ),
            (
                size // 2,
                size // 2
            ),
            radius
        )

        surface.blit(
            particle_surface,
            (
                int(self.x - size / 2),
                int(self.y - size / 2)
            )
        )


def spawn_particles(
    particles,
    x,
    y,
    color,
    amount=20
):

    for _ in range(amount):

        particles.append(
            Particle(
                x,
                y,
                color
            )
        )


# ============================================================
# MOVEMENT JUDGEMENT
# ============================================================

def movement_judgement(
    player_x,
    player_y,
    target
):

    target_x, target_y = target

    d = distance(
        player_x,
        player_y,
        target_x,
        target_y
    )

    if d <= PERFECT_DISTANCE:

        return (
            "PERFECT",
            1000,
            1.0
        )

    if d <= GOOD_DISTANCE:

        return (
            "GOOD",
            600,
            0.60
        )

    if d <= BAD_DISTANCE:

        return (
            "BAD",
            250,
            0.25
        )

    return (
        "MISS",
        0,
        0.0
    )


# ============================================================
# CLICK JUDGEMENT
# ============================================================

def click_judgement(
    click_x,
    click_y,
    target,
    timing_error
):

    target_x, target_y = target

    d = distance(
        click_x,
        click_y,
        target_x,
        target_y
    )

    if d > BAD_DISTANCE:

        return (
            "MISS",
            0,
            0.0
        )

    error = abs(timing_error)

    if error <= CLICK_PERFECT:

        return (
            "PERFECT",
            1000,
            1.0
        )

    if error <= CLICK_GOOD:

        return (
            "GOOD",
            600,
            0.60
        )

    if error <= CLICK_BAD:

        return (
            "BAD",
            250,
            0.25
        )

    return (
        "MISS",
        0,
        0.0
    )


# ============================================================
# RANK
# ============================================================

def calculate_rank(accuracy):

    if accuracy >= 100.0:
        return "SS"

    if accuracy >= 95.0:
        return "S"

    if accuracy >= 85.0:
        return "A"

    if accuracy >= 70.0:
        return "B"

    if accuracy >= 50.0:
        return "C"

    return "D"


# ============================================================
# NODE DRAWING
# ============================================================

def draw_nodes(
    surface,
    nodes,
    target_index,
    completed_count,
    mode,
    elapsed
):

    for i, (x, y) in enumerate(nodes):

        # ----------------------------------------------------
        # Completed nodes
        # ----------------------------------------------------

        if i < completed_count:

            pygame.draw.circle(
                surface,
                (50, 75, 105),
                (int(x), int(y)),
                8
            )

            pygame.draw.circle(
                surface,
                (100, 150, 190),
                (int(x), int(y)),
                4
            )

            continue

        # ----------------------------------------------------
        # Current target
        # ----------------------------------------------------

        if i == target_index:

            pulse = (
                math.sin(elapsed * 8.0)
                * 0.5
                + 0.5
            )

            if mode == "click":

                # Larger click-mode targets.
                radius = int(
                    20 + pulse * 5
                )

                glow_radius = radius + 16
                ring_radius = radius + 8
                center_radius = 7

            else:

                radius = int(
                    11 + pulse * 4
                )

                glow_radius = radius + 13
                ring_radius = radius + 7
                center_radius = 5

            # Glow

            glow_size = (
                glow_radius * 2
                + 4
            )

            glow = pygame.Surface(
                (
                    glow_size,
                    glow_size
                ),
                pygame.SRCALPHA
            )

            glow_alpha = int(
                30 + pulse * 45
            )

            pygame.draw.circle(
                glow,
                (
                    60,
                    210,
                    255,
                    glow_alpha
                ),
                (
                    glow_size // 2,
                    glow_size // 2
                ),
                glow_radius
            )

            surface.blit(
                glow,
                (
                    int(x - glow_size / 2),
                    int(y - glow_size / 2)
                )
            )

            # Target

            pygame.draw.circle(
                surface,
                (60, 210, 255),
                (int(x), int(y)),
                radius
            )

            pygame.draw.circle(
                surface,
                (225, 250, 255),
                (int(x), int(y)),
                center_radius
            )

            pygame.draw.circle(
                surface,
                (140, 240, 255),
                (int(x), int(y)),
                ring_radius,
                2
            )

        # ----------------------------------------------------
        # Future node
        # ----------------------------------------------------

        else:

            pygame.draw.circle(
                surface,
                (45, 65, 90),
                (int(x), int(y)),
                7
            )


# ============================================================
# MAIN
# ============================================================

def main():

    pygame.init()

    pygame.display.set_caption(
        "Pulse Garden"
    )

    # --------------------------------------------------------
    # Window
    # --------------------------------------------------------

    window_width = GAME_WIDTH
    window_height = GAME_HEIGHT

    fullscreen = False

    screen = pygame.display.set_mode(
        (
            window_width,
            window_height
        ),
        pygame.RESIZABLE
    )

    # --------------------------------------------------------
    # Logical render surface
    # --------------------------------------------------------

    logical_surface = pygame.Surface(
        (
            GAME_WIDTH,
            GAME_HEIGHT
        )
    )

    # --------------------------------------------------------
    # SSAA render surface
    # --------------------------------------------------------

    render_surface = pygame.Surface(
        (
            RENDER_WIDTH,
            RENDER_HEIGHT
        )
    )

    # --------------------------------------------------------
    # Fonts
    # --------------------------------------------------------

    font_small = pygame.font.Font(
        None,
        28
    )

    font_medium = pygame.font.Font(
        None,
        38
    )

    font_large = pygame.font.Font(
        None,
        64
    )

    font_huge = pygame.font.Font(
        None,
        96
    )

    clock = pygame.time.Clock()

    # ========================================================
    # GAME STATE
    # ========================================================

    state = "mode_select"

    mode = "movement"

    current_bpm = MOVEMENT_BPM
    current_beat = MOVEMENT_BEAT

    nodes = []

    target_index = 1

    player_x = GAME_WIDTH / 2
    player_y = GAME_HEIGHT / 2

    beat_timer = 0.0

    score = 0

    combo = 0
    max_combo = 0

    perfects = 0
    goods = 0
    bads = 0
    misses = 0

    accuracy_points = 0.0
    judged_count = 0

    particles = []

    judgement_text = ""
    judgement_timer = 0.0

    flash_timer = 0.0

    flash_color = (
        255,
        255,
        255
    )

    elapsed = 0.0

    running = True

    # ========================================================
    # CLICK INPUT
    # ========================================================

    click_received = False

    click_x = 0.0
    click_y = 0.0

    click_timing_error = 999.0

    # ========================================================
    # START LEVEL
    # ========================================================

    def start_level(selected_mode):

        nonlocal state
        nonlocal mode
        nonlocal nodes
        nonlocal target_index
        nonlocal player_x
        nonlocal player_y
        nonlocal beat_timer

        nonlocal current_bpm
        nonlocal current_beat

        nonlocal score
        nonlocal combo
        nonlocal max_combo

        nonlocal perfects
        nonlocal goods
        nonlocal bads
        nonlocal misses

        nonlocal accuracy_points
        nonlocal judged_count

        nonlocal judgement_text
        nonlocal judgement_timer
        nonlocal flash_timer

        nonlocal click_received
        nonlocal click_x
        nonlocal click_y
        nonlocal click_timing_error

        mode = selected_mode

        # --------------------------------------------
        # Mode-specific BPM.
        # --------------------------------------------

        if mode == "movement":

            current_bpm = MOVEMENT_BPM

        else:

            current_bpm = CLICK_BPM

        current_beat = (
            60.0 / current_bpm
        )

        nodes = generate_level()

        player_x, player_y = nodes[0]

        target_index = 1

        beat_timer = 0.0

        score = 0

        combo = 0
        max_combo = 0

        perfects = 0
        goods = 0
        bads = 0
        misses = 0

        accuracy_points = 0.0
        judged_count = 0

        particles.clear()

        judgement_text = ""
        judgement_timer = 0.0
        flash_timer = 0.0

        click_received = False

        click_x = 0.0
        click_y = 0.0

        click_timing_error = 999.0

        state = "playing"

    # ========================================================
    # JUDGE CURRENT TARGET
    # ========================================================

    def judge_target():

        nonlocal target_index

        nonlocal score
        nonlocal combo
        nonlocal max_combo

        nonlocal perfects
        nonlocal goods
        nonlocal bads
        nonlocal misses

        nonlocal accuracy_points
        nonlocal judged_count

        nonlocal judgement_text
        nonlocal judgement_timer

        nonlocal flash_timer
        nonlocal flash_color

        nonlocal click_received

        if target_index >= len(nodes):

            return

        target = nodes[target_index]

        # ----------------------------------------------------
        # Movement Mode
        # ----------------------------------------------------

        if mode == "movement":

            judgement, points, accuracy = (
                movement_judgement(
                    player_x,
                    player_y,
                    target
                )
            )

        # ----------------------------------------------------
        # Click Mode
        # ----------------------------------------------------

        else:

            if click_received:

                judgement, points, accuracy = (
                    click_judgement(
                        click_x,
                        click_y,
                        target,
                        click_timing_error
                    )
                )

            else:

                # No click = automatic MISS.
                judgement = "MISS"
                points = 0
                accuracy = 0.0

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        judged_count += 1

        accuracy_points += accuracy

        score += points

        if judgement == "PERFECT":

            perfects += 1
            combo += 1

            flash_color = (
                100,
                240,
                255
            )

        elif judgement == "GOOD":

            goods += 1
            combo += 1

            flash_color = (
                100,
                255,
                170
            )

        elif judgement == "BAD":

            bads += 1
            combo += 1

            flash_color = (
                255,
                220,
                90
            )

        else:

            misses += 1
            combo = 0

            flash_color = (
                255,
                90,
                100
            )

        max_combo = max(
            max_combo,
            combo
        )

        judgement_text = judgement

        judgement_timer = 0.55

        flash_timer = 0.18

        tx, ty = target

        spawn_particles(
            particles,
            tx,
            ty,
            flash_color,
            24
        )

        # ====================================================
        # IMPORTANT:
        #
        # The target ALWAYS advances after being judged.
        # This happens for PERFECT, GOOD, BAD, AND MISS.
        # ====================================================

        target_index += 1

        # Reset click state for next target.

        click_received = False

        if target_index >= len(nodes):

            state = "results"

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while running:

        dt = clock.tick(FPS) / 1000.0

        dt = min(
            dt,
            0.05
        )

        elapsed += dt

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            # ------------------------------------------------
            # Quit
            # ------------------------------------------------

            if event.type == pygame.QUIT:

                running = False

            # ------------------------------------------------
            # Resize
            # ------------------------------------------------

            elif event.type == pygame.VIDEORESIZE:

                if not fullscreen:

                    window_width = max(
                        640,
                        event.w
                    )

                    window_height = max(
                        360,
                        event.h
                    )

                    screen = pygame.display.set_mode(
                        (
                            window_width,
                            window_height
                        ),
                        pygame.RESIZABLE
                    )

            # ------------------------------------------------
            # Keyboard
            # ------------------------------------------------

            elif event.type == pygame.KEYDOWN:

                # Fullscreen

                if event.key == pygame.K_F11:

                    fullscreen = not fullscreen

                    if fullscreen:

                        screen = pygame.display.set_mode(
                            (
                                0,
                                0
                            ),
                            pygame.FULLSCREEN
                        )

                    else:

                        screen = pygame.display.set_mode(
                            (
                                GAME_WIDTH,
                                GAME_HEIGHT
                            ),
                            pygame.RESIZABLE
                        )

                    window_width, window_height = (
                        screen.get_size()
                    )

                # Escape

                elif event.key == pygame.K_ESCAPE:

                    if fullscreen:

                        fullscreen = False

                        screen = pygame.display.set_mode(
                            (
                                GAME_WIDTH,
                                GAME_HEIGHT
                            ),
                            pygame.RESIZABLE
                        )

                        window_width, window_height = (
                            screen.get_size()
                        )

                    else:

                        running = False

                # Mode selection

                elif state == "mode_select":

                    if event.key == pygame.K_1:

                        start_level(
                            "movement"
                        )

                    elif event.key == pygame.K_2:

                        start_level(
                            "click"
                        )

                # Results screen

                elif state == "results":

                    if event.key == pygame.K_r:

                        start_level(
                            mode
                        )

            # ------------------------------------------------
            # Mouse
            # ------------------------------------------------

            elif (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and state == "playing"
                and mode == "click"
            ):

                if target_index < len(nodes):

                    mouse_x, mouse_y = event.pos

                    # Convert window coordinates into the
                    # game's 1280x720 logical coordinates.

                    logical_x = (
                        mouse_x
                        * GAME_WIDTH
                        / max(
                            1,
                            window_width
                        )
                    )

                    logical_y = (
                        mouse_y
                        * GAME_HEIGHT
                        / max(
                            1,
                            window_height
                        )
                    )

                    # ----------------------------------------
                    # Click timing.
                    #
                    # current beat occurs when beat_timer
                    # reaches current_beat.
                    # ----------------------------------------

                    timing_error = (
                        current_beat
                        - beat_timer
                    )

                    # Keep the best click during the beat.

                    if (
                        not click_received
                        or abs(timing_error)
                        < abs(click_timing_error)
                    ):

                        click_received = True

                        click_x = logical_x
                        click_y = logical_y

                        click_timing_error = (
                            timing_error
                        )

        # ====================================================
        # PLAYING UPDATE
        # ====================================================

        if state == "playing":

            # ------------------------------------------------
            # MOVEMENT MODE
            # ------------------------------------------------

            if mode == "movement":

                keys = pygame.key.get_pressed()

                dx = 0.0
                dy = 0.0

                if (
                    keys[pygame.K_w]
                    or keys[pygame.K_UP]
                ):

                    dy -= 1.0

                if (
                    keys[pygame.K_s]
                    or keys[pygame.K_DOWN]
                ):

                    dy += 1.0

                if (
                    keys[pygame.K_a]
                    or keys[pygame.K_LEFT]
                ):

                    dx -= 1.0

                if (
                    keys[pygame.K_d]
                    or keys[pygame.K_RIGHT]
                ):

                    dx += 1.0

                if dx != 0.0 or dy != 0.0:

                    length = math.hypot(
                        dx,
                        dy
                    )

                    if length > 0:

                        dx /= length
                        dy /= length

                    player_x += (
                        dx
                        * PLAYER_SPEED
                        * dt
                    )

                    player_y += (
                        dy
                        * PLAYER_SPEED
                        * dt
                    )

                player_x = clamp(
                    player_x,
                    PLAYER_RADIUS,
                    GAME_WIDTH - PLAYER_RADIUS
                )

                player_y = clamp(
                    player_y,
                    PLAYER_RADIUS,
                    GAME_HEIGHT - PLAYER_RADIUS
                )

            # ------------------------------------------------
            # BEAT TIMER
            # ------------------------------------------------

            beat_timer += dt

            while beat_timer >= current_beat:

                beat_timer -= current_beat

                # --------------------------------------------
                # Every beat judges exactly one target.
                #
                # If there is no click in click mode,
                # judge_target() creates a MISS.
                # --------------------------------------------

                if target_index < len(nodes):

                    judge_target()

                else:

                    state = "results"

            # ------------------------------------------------
            # PARTICLES
            # ------------------------------------------------

            for particle in particles:

                particle.update(dt)

            particles[:] = [
                particle
                for particle in particles
                if particle.life > 0
            ]

            judgement_timer = max(
                0.0,
                judgement_timer - dt
            )

            flash_timer = max(
                0.0,
                flash_timer - dt
            )

        # ====================================================
        # DRAW
        # ====================================================

        logical_surface.fill(
            (7, 10, 20)
        )

        # ====================================================
        # MODE SELECT
        # ====================================================

        if state == "mode_select":

            draw_text(
                logical_surface,
                "PULSE GARDEN",
                font_huge,
                GAME_WIDTH / 2,
                130,
                (120, 220, 255),
                True
            )

            draw_text(
                logical_surface,
                "Choose a game mode",
                font_large,
                GAME_WIDTH / 2,
                230,
                (230, 240, 255),
                True
            )

            # Movement card

            pygame.draw.rect(
                logical_surface,
                (20, 35, 55),
                (
                    220,
                    330,
                    370,
                    190
                ),
                border_radius=18
            )

            pygame.draw.rect(
                logical_surface,
                (60, 130, 180),
                (
                    220,
                    330,
                    370,
                    190
                ),
                3,
                border_radius=18
            )

            draw_text(
                logical_surface,
                "1",
                font_huge,
                405,
                385,
                (90, 220, 255),
                True
            )

            draw_text(
                logical_surface,
                "MOVEMENT",
                font_medium,
                405,
                455,
                (240, 245, 255),
                True
            )

            draw_text(
                logical_surface,
                f"{MOVEMENT_BPM} BPM",
                font_small,
                405,
                490,
                (160, 180, 205),
                True
            )

            # Click card

            pygame.draw.rect(
                logical_surface,
                (20, 35, 55),
                (
                    690,
                    330,
                    370,
                    190
                ),
                border_radius=18
            )

            pygame.draw.rect(
                logical_surface,
                (70, 170, 190),
                (
                    690,
                    330,
                    370,
                    190
                ),
                3,
                border_radius=18
            )

            draw_text(
                logical_surface,
                "2",
                font_huge,
                875,
                385,
                (90, 240, 220),
                True
            )

            draw_text(
                logical_surface,
                "CLICK",
                font_medium,
                875,
                455,
                (240, 245, 255),
                True
            )

            draw_text(
                logical_surface,
                f"{CLICK_BPM} BPM",
                font_small,
                875,
                490,
                (160, 180, 205),
                True
            )

            draw_text(
                logical_surface,
                f"{NODE_COUNT - 1} targets",
                font_small,
                GAME_WIDTH / 2,
                590,
                (120, 140, 170),
                True
            )

            draw_text(
                logical_surface,
                "F11: Fullscreen",
                font_small,
                GAME_WIDTH / 2,
                635,
                (100, 120, 145),
                True
            )

        # ====================================================
        # PLAYING
        # ====================================================

        elif state == "playing":

            # ------------------------------------------------
            # Background grid
            # ------------------------------------------------

            grid_size = 80

            for x in range(
                0,
                GAME_WIDTH + 1,
                grid_size
            ):

                pygame.draw.line(
                    logical_surface,
                    (12, 18, 32),
                    (x, 0),
                    (x, GAME_HEIGHT)
                )

            for y in range(
                0,
                GAME_HEIGHT + 1,
                grid_size
            ):

                pygame.draw.line(
                    logical_surface,
                    (12, 18, 32),
                    (0, y),
                    (GAME_WIDTH, y)
                )

            # ------------------------------------------------
            # Route
            # ------------------------------------------------

            for i in range(
                max(
                    0,
                    target_index - 1
                ),
                min(
                    len(nodes) - 1,
                    target_index + 8
                )
            ):

                x1, y1 = nodes[i]
                x2, y2 = nodes[i + 1]

                pygame.draw.line(
                    logical_surface,
                    (25, 55, 75),
                    (
                        int(x1),
                        int(y1)
                    ),
                    (
                        int(x2),
                        int(y2)
                    ),
                    2
                )

            # ------------------------------------------------
            # Nodes
            # ------------------------------------------------

            draw_nodes(
                logical_surface,
                nodes,
                target_index,
                target_index,
                mode,
                elapsed
            )

            # ------------------------------------------------
            # Direction indicator
            # ------------------------------------------------

            if (
                mode == "movement"
                and target_index < len(nodes)
            ):

                tx, ty = nodes[target_index]

                dx = tx - player_x
                dy = ty - player_y

                length = math.hypot(
                    dx,
                    dy
                )

                if length > 1:

                    dx /= length
                    dy /= length

                    arrow_distance = 48

                    ax = (
                        player_x
                        + dx
                        * arrow_distance
                    )

                    ay = (
                        player_y
                        + dy
                        * arrow_distance
                    )

                    pygame.draw.line(
                        logical_surface,
                        (130, 230, 255),
                        (
                            int(player_x),
                            int(player_y)
                        ),
                        (
                            int(ax),
                            int(ay)
                        ),
                        3
                    )

            # ------------------------------------------------
            # Movement player
            # ------------------------------------------------

            if mode == "movement":

                pygame.draw.circle(
                    logical_surface,
                    (80, 180, 255),
                    (
                        int(player_x),
                        int(player_y)
                    ),
                    PLAYER_RADIUS
                )

                pygame.draw.circle(
                    logical_surface,
                    (220, 250, 255),
                    (
                        int(player_x),
                        int(player_y)
                    ),
                    5
                )

            # ------------------------------------------------
            # Click cursor
            # ------------------------------------------------

            else:

                mouse_x, mouse_y = pygame.mouse.get_pos()

                logical_x = (
                    mouse_x
                    * GAME_WIDTH
                    / max(
                        1,
                        window_width
                    )
                )

                logical_y = (
                    mouse_y
                    * GAME_HEIGHT
                    / max(
                        1,
                        window_height
                    )
                )

                pygame.draw.circle(
                    logical_surface,
                    (120, 240, 220),
                    (
                        int(logical_x),
                        int(logical_y)
                    ),
                    10,
                    2
                )

                pygame.draw.line(
                    logical_surface,
                    (120, 240, 220),
                    (
                        int(logical_x - 14),
                        int(logical_y)
                    ),
                    (
                        int(logical_x + 14),
                        int(logical_y)
                    ),
                    2
                )

                pygame.draw.line(
                    logical_surface,
                    (120, 240, 220),
                    (
                        int(logical_x),
                        int(logical_y - 14)
                    ),
                    (
                        int(logical_x),
                        int(logical_y + 14)
                    ),
                    2
                )

            # ------------------------------------------------
            # Particles
            # ------------------------------------------------

            for particle in particles:

                particle.draw(
                    logical_surface
                )

            # ------------------------------------------------
            # HUD
            # ------------------------------------------------

            draw_text(
                logical_surface,
                f"{mode.upper()} MODE",
                font_small,
                25,
                20,
                (130, 190, 220)
            )

            draw_text(
                logical_surface,
                f"{current_bpm} BPM",
                font_small,
                25,
                52,
                (180, 200, 220)
            )

            draw_text(
                logical_surface,
                f"Score: {score}",
                font_small,
                25,
                84
            )

            draw_text(
                logical_surface,
                f"Combo: {combo}",
                font_small,
                25,
                116,
                (255, 210, 120)
            )

            draw_text(
                logical_surface,
                f"Target: {min(target_index, NODE_COUNT - 1)} / {NODE_COUNT - 1}",
                font_small,
                GAME_WIDTH - 275,
                20,
                (180, 195, 215)
            )

            # ------------------------------------------------
            # Beat bar
            # ------------------------------------------------

            beat_progress = (
                beat_timer / current_beat
            )

            pygame.draw.rect(
                logical_surface,
                (25, 35, 50),
                (
                    GAME_WIDTH / 2 - 100,
                    25,
                    200,
                    8
                ),
                border_radius=4
            )

            pygame.draw.rect(
                logical_surface,
                (80, 210, 255),
                (
                    GAME_WIDTH / 2 - 100,
                    25,
                    int(
                        200
                        * beat_progress
                    ),
                    8
                ),
                border_radius=4
            )

            # ------------------------------------------------
            # Judgement
            # ------------------------------------------------

            if judgement_timer > 0:

                judgement_color = {
                    "PERFECT": (
                        100,
                        240,
                        255
                    ),
                    "GOOD": (
                        100,
                        255,
                        170
                    ),
                    "BAD": (
                        255,
                        220,
                        90
                    ),
                    "MISS": (
                        255,
                        90,
                        100
                    )
                }.get(
                    judgement_text,
                    (255, 255, 255)
                )

                draw_text(
                    logical_surface,
                    judgement_text,
                    font_large,
                    GAME_WIDTH / 2,
                    GAME_HEIGHT - 105,
                    judgement_color,
                    True
                )

            # ------------------------------------------------
            # Flash
            # ------------------------------------------------

            if flash_timer > 0:

                alpha = int(
                    50
                    * clamp(
                        flash_timer / 0.18,
                        0.0,
                        1.0
                    )
                )

                flash = pygame.Surface(
                    (
                        GAME_WIDTH,
                        GAME_HEIGHT
                    ),
                    pygame.SRCALPHA
                )

                flash.fill(
                    (
                        flash_color[0],
                        flash_color[1],
                        flash_color[2],
                        alpha
                    )
                )

                logical_surface.blit(
                    flash,
                    (0, 0)
                )

        # ====================================================
        # RESULTS
        # ====================================================

        elif state == "results":

            total = max(
                1,
                judged_count
            )

            accuracy = (
                accuracy_points
                / total
            ) * 100.0

            rank = calculate_rank(
                accuracy
            )

            draw_text(
                logical_surface,
                "LEVEL COMPLETE",
                font_huge,
                GAME_WIDTH / 2,
                100,
                (120, 225, 255),
                True
            )

            draw_text(
                logical_surface,
                rank,
                font_huge,
                GAME_WIDTH / 2,
                210,
                (255, 230, 120),
                True
            )

            draw_text(
                logical_surface,
                f"{accuracy:.2f}% ACCURACY",
                font_large,
                GAME_WIDTH / 2,
                290,
                (235, 245, 255),
                True
            )

            draw_text(
                logical_surface,
                f"Score      {score}",
                font_medium,
                300,
                365
            )

            draw_text(
                logical_surface,
                f"Max Combo  {max_combo}",
                font_medium,
                300,
                410
            )

            draw_text(
                logical_surface,
                f"Perfect    {perfects}",
                font_medium,
                300,
                455,
                (100, 240, 255)
            )

            draw_text(
                logical_surface,
                f"Good       {goods}",
                font_medium,
                720,
                365,
                (100, 255, 170)
            )

            draw_text(
                logical_surface,
                f"Bad        {bads}",
                font_medium,
                720,
                410,
                (255, 220, 90)
            )

            draw_text(
                logical_surface,
                f"Miss       {misses}",
                font_medium,
                720,
                455,
                (255, 90, 100)
            )

            draw_text(
                logical_surface,
                f"{current_bpm} BPM",
                font_small,
                GAME_WIDTH / 2,
                510,
                (130, 155, 180),
                True
            )

            draw_text(
                logical_surface,
                "R  —  Play Again",
                font_medium,
                GAME_WIDTH / 2,
                565,
                (180, 205, 230),
                True
            )

            draw_text(
                logical_surface,
                "ESC  —  Quit",
                font_small,
                GAME_WIDTH / 2,
                620,
                (100, 120, 145),
                True
            )

        # ====================================================
        # SSAA
        # ====================================================

        pygame.transform.scale(
            logical_surface,
            (
                RENDER_WIDTH,
                RENDER_HEIGHT
            ),
            render_surface
        )

        # ====================================================
        # WINDOW SCALE
        # ====================================================

        final_surface = pygame.transform.smoothscale(
            render_surface,
            (
                window_width,
                window_height
            )
        )

        screen.blit(
            final_surface,
            (0, 0)
        )

        pygame.display.flip()

    pygame.quit()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
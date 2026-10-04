import math
import random
import pygame


# ============================================================
# CONFIG
# ============================================================
STAR_SEED  = random.random()
GAME_WIDTH = 1280
GAME_HEIGHT = 720

SSAA = 2
FPS = 170

BPM = 256
BEAT = 60.0 / BPM

NODE_COUNT = 120

PLAYER_RADIUS = 15.0
PLAYER_SPEED = 420.0

MIN_NODE_DISTANCE = 45.0
MAX_NODE_DISTANCE = PLAYER_SPEED * BEAT * 0.70

PERFECT_DISTANCE = 25.0
GOOD_DISTANCE = 50.0
BAD_DISTANCE = 80.0


# ============================================================
# COLORS
# ============================================================

BG = (7, 9, 18)
GRID = (12, 17, 31)
STAR = (18, 31, 52)
ROUTE = (24, 55, 80)

NODE_DIM = (28, 70, 92)
NODE_OUTER = (25, 100, 145)
NODE_RING = (50, 170, 230)
NODE_BRIGHT = (100, 225, 255)
NODE_WHITE = (225, 250, 255)

PLAYER_OUTER = (30, 100, 135)
PLAYER = (80, 205, 245)
PLAYER_CORE = (220, 250, 255)

TEXT = (235, 240, 255)
TEXT_DIM = (145, 165, 190)

PROGRESS_BG = (20, 30, 45)
PROGRESS = (70, 190, 230)

PERFECT_COLOR = (120, 255, 220)
GOOD_COLOR = (120, 210, 255)
BAD_COLOR = (255, 210, 100)
MISS_COLOR = (255, 100, 120)


# ============================================================
# HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def normalize(x, y):
    length = math.hypot(x, y)

    if length <= 0.000001:
        return 0.0, 0.0

    return x / length, y / length


def draw_text(surface, font, text, x, y, color=TEXT, center=False):
    image = font.render(str(text), True, color)

    if center:
        rect = image.get_rect(center=(int(x), int(y)))
    else:
        rect = image.get_rect(topleft=(int(x), int(y)))

    surface.blit(image, rect)


# ============================================================
# LEVEL GENERATION
# ============================================================

def generate_garden():
    nodes = []

    x = GAME_WIDTH * 0.5
    y = GAME_HEIGHT * 0.5

    nodes.append((x, y))

    for i in range(NODE_COUNT - 1):
        previous_x, previous_y = nodes[-1]

        candidates = []

        for _ in range(120):
            angle = random.uniform(0.0, math.tau)
            dist = random.uniform(
                MIN_NODE_DISTANCE,
                MAX_NODE_DISTANCE
            )

            candidate_x = previous_x + math.cos(angle) * dist
            candidate_y = previous_y + math.sin(angle) * dist

            margin = 70.0

            if candidate_x < margin:
                continue

            if candidate_x > GAME_WIDTH - margin:
                continue

            if candidate_y < margin:
                continue

            if candidate_y > GAME_HEIGHT - margin:
                continue

            valid = True

            # Keep the recent route from folding over itself.
            for old_x, old_y in nodes[-12:]:
                if distance(
                    candidate_x,
                    candidate_y,
                    old_x,
                    old_y
                ) < MIN_NODE_DISTANCE:
                    valid = False
                    break

            if valid:
                candidates.append((candidate_x, candidate_y))

        if candidates:
            # Prefer candidates that continue in a somewhat
            # different direction, making the route readable.
            candidate = random.choice(candidates)
            nodes.append(candidate)

        else:
            # Guaranteed fallback.
            angle = random.uniform(0.0, math.tau)

            candidate_x = previous_x + math.cos(angle) * MIN_NODE_DISTANCE
            candidate_y = previous_y + math.sin(angle) * MIN_NODE_DISTANCE

            candidate_x = clamp(
                candidate_x,
                70.0,
                GAME_WIDTH - 70.0
            )

            candidate_y = clamp(
                candidate_y,
                70.0,
                GAME_HEIGHT - 70.0
            )

            nodes.append((candidate_x, candidate_y))

    return nodes


# ============================================================
# PARTICLES
# ============================================================

class Particle:
    def __init__(self, x, y, vx, vy, lifetime, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = lifetime
        self.max_life = lifetime
        self.size = size

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vx *= 0.97
        self.vy *= 0.97

        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return

        alpha = clamp(self.life / self.max_life, 0.0, 1.0)

        radius = max(
            1,
            int(self.size * alpha * SSAA)
        )

        color = (
            int(100 * alpha),
            int(225 * alpha),
            int(255 * alpha)
        )

        pygame.draw.circle(
            surface,
            color,
            (
                int(self.x * SSAA),
                int(self.y * SSAA)
            ),
            radius
        )


def spawn_particles(particles, x, y, amount):
    for _ in range(amount):
        angle = random.uniform(0.0, math.tau)
        speed = random.uniform(40.0, 220.0)

        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        particles.append(
            Particle(
                x,
                y,
                vx,
                vy,
                random.uniform(0.35, 0.8),
                random.uniform(2.0, 5.0)
            )
        )


# ============================================================
# LEVEL STATE
# ============================================================

def new_level():
    nodes = generate_garden()

    return {
        "nodes": nodes,
        "player_x": nodes[0][0],
        "player_y": nodes[0][1],

        # Node 0 is the starting position.
        "target_index": 1,

        "score": 0,
        "combo": 0,
        "max_combo": 0,

        "perfect_count": 0,
        "good_count": 0,
        "bad_count": 0,
        "miss_count": 0,

        "beat_timer": 0.0,
        "beat_flash": 0.0,

        "particles": [],

        "arrow_angle": 0.0,

        "last_judgement": "",
        "judgement_timer": 0.0,

        "finished": False,
    }


# ============================================================
# RESULTS
# ============================================================

def calculate_accuracy(state):
    total = (
        state["perfect_count"]
        + state["good_count"]
        + state["bad_count"]
        + state["miss_count"]
    )

    if total <= 0:
        return 0.0

    weighted = (
        state["perfect_count"] * 100.0
        + state["good_count"] * 60.0
        + state["bad_count"] * 25.0
    )

    return weighted / total


def get_rank(accuracy):
    if accuracy >= 100:
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
# MAIN
# ============================================================

def main():
    pygame.init()

    pygame.display.set_caption("Pulse Garden")

    fullscreen = False

    window_width = GAME_WIDTH
    window_height = GAME_HEIGHT

    screen = pygame.display.set_mode(
        (window_width, window_height),
        pygame.RESIZABLE
    )

    render_width = GAME_WIDTH * SSAA
    render_height = GAME_HEIGHT * SSAA

    render_surface = pygame.Surface(
        (render_width, render_height)
    )

    clock = pygame.time.Clock()

    font_small = pygame.font.Font(
        None,
        18 * SSAA
    )

    font_medium = pygame.font.Font(
        None,
        25 * SSAA
    )

    font_large = pygame.font.Font(
        None,
        34 * SSAA
    )

    font_huge = pygame.font.Font(
        None,
        72 * SSAA
    )

    state = new_level()

    running = True

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    window_width = max(640, event.w)
                    window_height = max(480, event.h)

                    screen = pygame.display.set_mode(
                        (window_width, window_height),
                        pygame.RESIZABLE
                    )

            elif event.type == pygame.KEYDOWN:

                # ------------------------------------------------
                # FULLSCREEN
                # ------------------------------------------------

                if event.key == pygame.K_F11:

                    fullscreen = not fullscreen

                    if fullscreen:
                        screen = pygame.display.set_mode(
                            (0, 0),
                            pygame.FULLSCREEN
                        )

                        window_width, window_height = screen.get_size()

                    else:
                        window_width = GAME_WIDTH
                        window_height = GAME_HEIGHT

                        screen = pygame.display.set_mode(
                            (
                                window_width,
                                window_height
                            ),
                            pygame.RESIZABLE
                        )

                # ------------------------------------------------
                # ESC
                # ------------------------------------------------

                elif event.key == pygame.K_ESCAPE:

                    if fullscreen:
                        fullscreen = False

                        window_width = GAME_WIDTH
                        window_height = GAME_HEIGHT

                        screen = pygame.display.set_mode(
                            (
                                window_width,
                                window_height
                            ),
                            pygame.RESIZABLE
                        )

                    else:
                        running = False

                # ------------------------------------------------
                # RESTART AFTER FINISH
                # ------------------------------------------------

                elif (
                    event.key == pygame.K_r
                    and state["finished"]
                ):
                    state = new_level()

        # ====================================================
        # UPDATE
        # ====================================================

        if not state["finished"]:

            keys = pygame.key.get_pressed()

            move_x = 0.0
            move_y = 0.0

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move_x -= 1.0

            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move_x += 1.0

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move_y -= 1.0

            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move_y += 1.0

            move_x, move_y = normalize(
                move_x,
                move_y
            )

            state["player_x"] += (
                move_x * PLAYER_SPEED * dt
            )

            state["player_y"] += (
                move_y * PLAYER_SPEED * dt
            )

            # Keep player inside the level.
            state["player_x"] = clamp(
                state["player_x"],
                PLAYER_RADIUS,
                GAME_WIDTH - PLAYER_RADIUS
            )

            state["player_y"] = clamp(
                state["player_y"],
                PLAYER_RADIUS,
                GAME_HEIGHT - PLAYER_RADIUS
            )

            # ====================================================
            # BEAT TIMER
            # ====================================================

            state["beat_timer"] += dt

            while state["beat_timer"] >= BEAT:

                state["beat_timer"] -= BEAT
                state["beat_flash"] = 1.0

                target_index = state["target_index"]

                if target_index < len(state["nodes"]):

                    target_x, target_y = state["nodes"][target_index]

                    target_distance = distance(
                        state["player_x"],
                        state["player_y"],
                        target_x,
                        target_y
                    )

                    # --------------------------------------------
                    # JUDGEMENT
                    # --------------------------------------------

                    if target_distance <= PERFECT_DISTANCE:

                        state["score"] += 1000
                        state["combo"] += 1
                        state["perfect_count"] += 1

                        state["last_judgement"] = "PERFECT"
                        state["judgement_timer"] = 0.7

                        spawn_particles(
                            state["particles"],
                            target_x,
                            target_y,
                            35
                        )

                    elif target_distance <= GOOD_DISTANCE:

                        state["score"] += 600
                        state["combo"] += 1
                        state["good_count"] += 1

                        state["last_judgement"] = "GOOD"
                        state["judgement_timer"] = 0.7

                        spawn_particles(
                            state["particles"],
                            target_x,
                            target_y,
                            25
                        )

                    elif target_distance <= BAD_DISTANCE:

                        state["score"] += 250
                        state["combo"] += 1
                        state["bad_count"] += 1

                        state["last_judgement"] = "BAD"
                        state["judgement_timer"] = 0.7

                        spawn_particles(
                            state["particles"],
                            target_x,
                            target_y,
                            15
                        )

                    else:

                        state["combo"] = 0
                        state["miss_count"] += 1

                        state["last_judgement"] = "MISS"
                        state["judgement_timer"] = 0.7

                    state["max_combo"] = max(
                        state["max_combo"],
                        state["combo"]
                    )

                    # ------------------------------------------------
                    # IMPORTANT:
                    # The target ALWAYS advances.
                    # ------------------------------------------------

                    state["target_index"] += 1

                    # ------------------------------------------------
                    # LEVEL COMPLETE
                    # ------------------------------------------------

                    if state["target_index"] >= len(state["nodes"]):

                        state["finished"] = True

                        # Make sure the final target gets a burst.
                        spawn_particles(
                            state["particles"],
                            target_x,
                            target_y,
                            60
                        )

        # ====================================================
        # PARTICLES
        # ====================================================

        for particle in state["particles"]:
            particle.update(dt)

        state["particles"] = [
            particle
            for particle in state["particles"]
            if particle.life > 0
        ]

        state["beat_flash"] = max(
            0.0,
            state["beat_flash"] - dt * 4.0
        )

        state["judgement_timer"] = max(
            0.0,
            state["judgement_timer"] - dt
        )

        # ====================================================
        # CURRENT TARGET ARROW
        # ====================================================

        if not state["finished"]:

            target_index = state["target_index"]

            if target_index < len(state["nodes"]):

                target_x, target_y = state["nodes"][target_index]

                desired_angle = math.atan2(
                    target_y - state["player_y"],
                    target_x - state["player_x"]
                )

                # Smooth purely visual arrow rotation.
                difference = (
                    desired_angle
                    - state["arrow_angle"]
                    + math.pi
                ) % math.tau - math.pi

                state["arrow_angle"] += difference * min(
                    1.0,
                    dt * 12.0
                )

        # ====================================================
        # DRAW
        # ====================================================

        render_surface.fill(BG)

        # ====================================================
        # BACKGROUND GRID
        # ====================================================

        grid_offset = (
            pygame.time.get_ticks() * 0.015
        ) % 40.0

        for x in range(-40, GAME_WIDTH + 40, 40):

            px = int(
                (x + grid_offset) * SSAA
            )

            pygame.draw.line(
                render_surface,
                GRID,
                (px, 0),
                (px, render_height),
                max(1, SSAA)
            )

        for y in range(-40, GAME_HEIGHT + 40, 40):

            py = int(
                (y + grid_offset) * SSAA
            )

            pygame.draw.line(
                render_surface,
                GRID,
                (0, py),
                (render_width, py),
                max(1, SSAA)
            )

        # ====================================================
        # BACKGROUND STARS
        # ====================================================

        random.seed(STAR_SEED)

        for _ in range(180):

            sx = random.randrange(GAME_WIDTH)
            sy = random.randrange(GAME_HEIGHT)

            pygame.draw.circle(
                render_surface,
                STAR,
                (
                    sx * SSAA,
                    sy * SSAA
                ),
                random.choice([1, 1, 1, 2]) * SSAA
            )

        # ====================================================
        # ROUTE GUIDE
        # ====================================================

        nodes = state["nodes"]
        target_index = state["target_index"]

        route_end = min(
            target_index + 7,
            len(nodes)
        )

        if not state["finished"]:

            route_points = [
                nodes[i]
                for i in range(
                    max(0, target_index - 1),
                    route_end
                )
            ]

            if len(route_points) >= 2:

                points = [
                    (
                        int(x * SSAA),
                        int(y * SSAA)
                    )
                    for x, y in route_points
                ]

                pygame.draw.lines(
                    render_surface,
                    ROUTE,
                    False,
                    points,
                    2 * SSAA
                )

        # ====================================================
        # NODES
        # ====================================================

        pulse = (
            math.sin(
                pygame.time.get_ticks() * 0.008
            ) + 1.0
        ) * 0.5

        for i, (nx, ny) in enumerate(nodes):

            if i == 0:
                # Starting node.
                color = NODE_RING
                radius = 9

            elif i < target_index:
                # Already completed.
                color = NODE_DIM
                radius = 5

            elif (
                i == target_index
                and not state["finished"]
            ):
                # Current target.
                color = NODE_BRIGHT
                radius = int(11 + pulse * 4)

                # Outer glow ring.
                pygame.draw.circle(
                    render_surface,
                    NODE_OUTER,
                    (
                        int(nx * SSAA),
                        int(ny * SSAA)
                    ),
                    int((radius + 10) * SSAA),
                    2 * SSAA
                )

                pygame.draw.circle(
                    render_surface,
                    NODE_RING,
                    (
                        int(nx * SSAA),
                        int(ny * SSAA)
                    ),
                    int((radius + 5) * SSAA),
                    2 * SSAA
                )

            else:
                color = NODE_OUTER
                radius = 6

            pygame.draw.circle(
                render_surface,
                color,
                (
                    int(nx * SSAA),
                    int(ny * SSAA)
                ),
                radius * SSAA
            )

            if (
                i == target_index
                and not state["finished"]
            ):

                pygame.draw.circle(
                    render_surface,
                    NODE_WHITE,
                    (
                        int(nx * SSAA),
                        int(ny * SSAA)
                    ),
                    3 * SSAA
                )

        # ====================================================
        # PLAYER
        # ====================================================

        px = int(state["player_x"] * SSAA)
        py = int(state["player_y"] * SSAA)

        pygame.draw.circle(
            render_surface,
            PLAYER_OUTER,
            (px, py),
            int(PLAYER_RADIUS * SSAA + 5 * SSAA)
        )

        pygame.draw.circle(
            render_surface,
            PLAYER,
            (px, py),
            int(PLAYER_RADIUS * SSAA)
        )

        pygame.draw.circle(
            render_surface,
            PLAYER_CORE,
            (px, py),
            int(PLAYER_RADIUS * SSAA * 0.42)
        )

        # ====================================================
        # ARROW
        # ====================================================

        if not state["finished"]:

            arrow_length = 45.0
            arrow_x = (
                state["player_x"]
                + math.cos(state["arrow_angle"])
                * arrow_length
            )

            arrow_y = (
                state["player_y"]
                + math.sin(state["arrow_angle"])
                * arrow_length
            )

            pygame.draw.line(
                render_surface,
                NODE_WHITE,
                (px, py),
                (
                    int(arrow_x * SSAA),
                    int(arrow_y * SSAA)
                ),
                3 * SSAA
            )

            # Arrowhead.
            left_angle = state["arrow_angle"] + math.pi * 0.75
            right_angle = state["arrow_angle"] - math.pi * 0.75

            arrow_size = 10.0

            left_x = (
                arrow_x
                + math.cos(left_angle) * arrow_size
            )

            left_y = (
                arrow_y
                + math.sin(left_angle) * arrow_size
            )

            right_x = (
                arrow_x
                + math.cos(right_angle) * arrow_size
            )

            right_y = (
                arrow_y
                + math.sin(right_angle) * arrow_size
            )

            pygame.draw.polygon(
                render_surface,
                NODE_WHITE,
                [
                    (
                        int(arrow_x * SSAA),
                        int(arrow_y * SSAA)
                    ),
                    (
                        int(left_x * SSAA),
                        int(left_y * SSAA)
                    ),
                    (
                        int(right_x * SSAA),
                        int(right_y * SSAA)
                    )
                ]
            )

        # ====================================================
        # PARTICLES
        # ====================================================

        for particle in state["particles"]:
            particle.draw(render_surface)

        # ====================================================
        # HUD
        # ====================================================

        draw_text(
            render_surface,
            font_medium,
            f"Score  {state['score']:,}",
            20 * SSAA,
            16 * SSAA
        )

        draw_text(
            render_surface,
            font_medium,
            f"Combo  {state['combo']}",
            20 * SSAA,
            48 * SSAA
        )

        if not state["finished"]:

            current_node = min(
                state["target_index"],
                len(nodes)
            )

            draw_text(
                render_surface,
                font_small,
                f"Node {current_node}/{len(nodes) - 1}",
                20 * SSAA,
                84 * SSAA,
                TEXT_DIM
            )

            # Progress bar.
            bar_x = 20 * SSAA
            bar_y = 112 * SSAA
            bar_width = 250 * SSAA
            bar_height = 8 * SSAA

            pygame.draw.rect(
                render_surface,
                PROGRESS_BG,
                (
                    bar_x,
                    bar_y,
                    bar_width,
                    bar_height
                )
            )

            progress = clamp(
                state["target_index"]
                / max(1, len(nodes) - 1),
                0.0,
                1.0
            )

            pygame.draw.rect(
                render_surface,
                PROGRESS,
                (
                    bar_x,
                    bar_y,
                    int(bar_width * progress),
                    bar_height
                )
            )

            draw_text(
                render_surface,
                font_small,
                "WASD / Arrow Keys = Move",
                20 * SSAA,
                (GAME_HEIGHT - 54) * SSAA,
                TEXT_DIM
            )

            draw_text(
                render_surface,
                font_small,
                "F11 = Fullscreen    Esc = Exit",
                20 * SSAA,
                (GAME_HEIGHT - 30) * SSAA,
                TEXT_DIM
            )

        # ====================================================
        # JUDGEMENT
        # ====================================================

        if (
            state["judgement_timer"] > 0.0
            and not state["finished"]
        ):

            judgement = state["last_judgement"]

            if judgement == "PERFECT":
                judgement_color = PERFECT_COLOR
            elif judgement == "GOOD":
                judgement_color = GOOD_COLOR
            elif judgement == "BAD":
                judgement_color = BAD_COLOR
            else:
                judgement_color = MISS_COLOR

            alpha = clamp(
                state["judgement_timer"] / 0.7,
                0.0,
                1.0
            )

            # Render text to a transparent surface so it can fade.
            judgement_surface = pygame.Surface(
                (
                    400 * SSAA,
                    70 * SSAA
                ),
                pygame.SRCALPHA
            )

            judgement_image = font_large.render(
                judgement,
                True,
                (
                    judgement_color[0],
                    judgement_color[1],
                    judgement_color[2],
                    int(255 * alpha)
                )
            )

            judgement_rect = judgement_image.get_rect(
                center=(
                    200 * SSAA,
                    35 * SSAA
                )
            )

            judgement_surface.blit(
                judgement_image,
                judgement_rect
            )

            render_surface.blit(
                judgement_surface,
                (
                    int(
                        GAME_WIDTH * SSAA / 2
                        - 200 * SSAA
                    ),
                    int(150 * SSAA)
                )
            )

        # ====================================================
        # BEAT FLASH
        # ====================================================

        if state["beat_flash"] > 0.0:

            flash_alpha = int(
                clamp(
                    state["beat_flash"],
                    0.0,
                    1.0
                ) * 35
            )

            flash_surface = pygame.Surface(
                (render_width, render_height),
                pygame.SRCALPHA
            )

            flash_surface.fill(
                (
                    100,
                    220,
                    255,
                    flash_alpha
                )
            )

            render_surface.blit(
                flash_surface,
                (0, 0)
            )

        # ====================================================
        # RESULTS SCREEN
        # ====================================================

        if state["finished"]:

            overlay = pygame.Surface(
                (render_width, render_height),
                pygame.SRCALPHA
            )

            overlay.fill(
                (3, 5, 12, 220)
            )

            render_surface.blit(
                overlay,
                (0, 0)
            )

            accuracy = calculate_accuracy(state)
            rank = get_rank(accuracy)

            center_x = GAME_WIDTH * SSAA / 2

            draw_text(
                render_surface,
                font_huge,
                "LEVEL COMPLETE",
                center_x,
                125 * SSAA,
                NODE_WHITE,
                center=True
            )

            draw_text(
                render_surface,
                font_large,
                f"RANK  {rank}",
                center_x,
                215 * SSAA,
                NODE_BRIGHT,
                center=True
            )

            draw_text(
                render_surface,
                font_medium,
                f"Score  {state['score']:,}",
                center_x,
                285 * SSAA,
                TEXT,
                center=True
            )

            draw_text(
                render_surface,
                font_medium,
                f"Accuracy  {accuracy:.2f}%",
                center_x,
                325 * SSAA,
                TEXT,
                center=True
            )

            draw_text(
                render_surface,
                font_medium,
                f"Max Combo  {state['max_combo']}",
                center_x,
                365 * SSAA,
                TEXT,
                center=True
            )

            # Judgement statistics.
            draw_text(
                render_surface,
                font_small,
                f"PERFECT   {state['perfect_count']}",
                center_x - 250 * SSAA,
                430 * SSAA,
                PERFECT_COLOR,
                center=True
            )

            draw_text(
                render_surface,
                font_small,
                f"GOOD   {state['good_count']}",
                center_x - 80 * SSAA,
                430 * SSAA,
                GOOD_COLOR,
                center=True
            )

            draw_text(
                render_surface,
                font_small,
                f"BAD   {state['bad_count']}",
                center_x + 80 * SSAA,
                430 * SSAA,
                BAD_COLOR,
                center=True
            )

            draw_text(
                render_surface,
                font_small,
                f"MISS   {state['miss_count']}",
                center_x + 250 * SSAA,
                430 * SSAA,
                MISS_COLOR,
                center=True
            )

            draw_text(
                render_surface,
                font_medium,
                "R = Play Again",
                center_x,
                515 * SSAA,
                TEXT,
                center=True
            )

            draw_text(
                render_surface,
                font_small,
                "Esc = Exit",
                center_x,
                555 * SSAA,
                TEXT_DIM,
                center=True
            )

        # ====================================================
        # SSAA DOWNSCALE
        # ====================================================

        scaled_surface = pygame.transform.smoothscale(
            render_surface,
            (
                window_width,
                window_height
            )
        )

        screen.blit(
            scaled_surface,
            (0, 0)
        )

        pygame.display.flip()

    pygame.quit()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
import pygame, sys, random, time
from utils.robot import Robot
from utils.behavior_tree import Sequence, Selector, Repeater, Condition
from utils.behaviors import MoveTo, Refill, Recharge, FindDryPlant, Water, NEED_THIRST, AllPlantsWatered

# --- Konstanta ---
WIDTH, HEIGHT = 1000, 600
THIRST_MULTIPLIER = 3.0
NUM_PLANTS = 8

# --- Inisialisasi Pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Behavior Tree - Plant Watering Robot")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Segoe UI", 22)

def draw_station(screen, pos, color, label):
    """Gambar stasiun pengisian daya atau air"""
    x, y = pos
    pygame.draw.rect(screen, (50, 50, 50), (x - 4, y - 4, 48, 48), border_radius=8)
    pygame.draw.rect(screen, color, (x, y, 40, 40), border_radius=10)

    label_font = pygame.font.SysFont("Arial", 16, bold=True)
    text = label_font.render(label, True, (0, 0, 0))
    text_rect = text.get_rect(center=(x + 20, y + 20))
    screen.blit(text, text_rect)


def draw_plant(screen, plant):
    thirst = plant["thirst"]
    g = max(0, 255 - int(thirst * 2))
    color_leaf = (50, g, 35) if thirst < NEED_THIRST else (160, 80, 40)
    color_shadow = (max(0, color_leaf[0] - 40),
                    max(0, color_leaf[1] - 40),
                    max(0, color_leaf[2] - 40))
    x, y = int(plant["x"]), int(plant["y"])

    # leaf shadow
    pygame.draw.circle(screen, color_shadow, (x - 14, y - 9), 12)
    pygame.draw.circle(screen, color_shadow, (x + 14, y - 9), 12)
    pygame.draw.circle(screen, color_shadow, (x, y - 17), 13)

    # branch
    pygame.draw.rect(screen, (85, 55, 35), (x - 4, y, 8, 28))

    # leaf
    pygame.draw.circle(screen, color_leaf, (x - 14, y - 9), 12)
    pygame.draw.circle(screen, color_leaf, (x + 14, y - 9), 12)
    pygame.draw.circle(screen, color_leaf, (x, y - 17), 13)
    pygame.draw.circle(screen, color_leaf, (x, y - 25), 10)

    # humidity bar
    pygame.draw.rect(screen, (180, 180, 180), (x - 16, y + 32, 32, 6))
    pygame.draw.rect(screen, (0, 200, 0), (x - 16, y + 32, 32 * (1 - thirst / 100.0), 6))


def create_plants():
    plants = []
    cols, rows = 4, 2
    margin_x, margin_y = 150, 180
    spacing_x, spacing_y = 200, 160
    for row in range(rows):
        for col in range(cols):
            x = margin_x + col * spacing_x
            y = margin_y + row * spacing_y
            plants.append({
                "x": x + random.randint(-15, 15),
                "y": y + random.randint(-10, 10),
                "thirst": random.randint(40, 100),
                "last_watered": None
            })
    return plants

def main():
    # --- Setup environment ---
    plants = create_plants()
    charging_station = (120, HEIGHT - 120)
    water_station = (WIDTH - 140, HEIGHT - 120)
    robot = Robot(WIDTH // 2, HEIGHT // 2)

    # --- Setup Behavior Tree ---
    low_battery = Condition(lambda: robot.battery < 20.0)
    low_water = Condition(lambda: robot.water < 20.0)
    go_charge = Sequence([MoveTo(robot, lambda: charging_station), Recharge(robot)])
    go_refill = Sequence([MoveTo(robot, lambda: water_station), Refill(robot)])
    go_water = Sequence([
        FindDryPlant(robot, plants),
        MoveTo(robot, lambda: (robot.target["x"], robot.target["y"]) if robot.target else None),
        Water(robot, plants)
    ])
    all_watered_sequence = Sequence([
        AllPlantsWatered(plants),
        MoveTo(robot, lambda: charging_station),
        Recharge(robot)
    ])
    root = Repeater(Selector([
        all_watered_sequence,
        Sequence([low_battery, go_charge]),
        Sequence([low_water, go_refill]),
        go_water
    ]))

    # --- Main Loop ---
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # --- environment update ---
        for p in plants:
            if p.get("last_watered"):
                age = time.time() - p["last_watered"]
                base_rate = min(0.0005 + age * 0.0001, 0.003)
            else:
                base_rate = 0.0015 + random.uniform(-0.0003, 0.0003)
            p["thirst"] = min(100.0, p["thirst"] + base_rate * THIRST_MULTIPLIER)

        # resources consumption
        robot.battery = max(0.0, robot.battery - 0.05)
        robot.water = max(0.0, robot.water - 0.005)

        # run bt
        root.tick()

        # --- Draw all the Object ---
        screen.fill((230, 245, 230))
        draw_station(screen, charging_station, (230, 255, 120), "CHG")
        draw_station(screen, water_station, (130, 210, 255), "H2O")

        for p in plants:
            draw_plant(screen, p)

        robot.draw(screen)

        # --- UI info ---
        ui_text = f"Battery: {robot.battery:.1f}%   Water: {robot.water:.1f}%   Task: {robot.active_task or 'Idle'}"
        screen.blit(font.render(ui_text, True, (30, 30, 30)), (15, 15))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

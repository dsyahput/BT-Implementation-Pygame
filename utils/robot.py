import pygame
import math

class Robot:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 20
        self.speed = 2.0
        self.angular_speed = 0.04  
        self.theta = 0.0           
        self.battery = 100.0
        self.water = 100.0
        self.target = None
        self.action = "Idle"
        self.active_task = None

    def move_towards(self, target, tolerance=6):
        if target is None:
            return False

        tx, ty = target
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < tolerance:
            return True

        # --- orientation ---
        desired_angle = math.atan2(dy, dx)
        angle_diff = (desired_angle - self.theta + math.pi) % (2 * math.pi) - math.pi

        # angular movement
        if abs(angle_diff) > 0.05:
            turn = max(-self.angular_speed, min(self.angular_speed, angle_diff))
            self.theta += turn
        else:
            self.x += math.cos(self.theta) * self.speed
            self.y += math.sin(self.theta) * self.speed

        return False

    def draw(self, screen):
        # --- main body ---
        pygame.draw.circle(screen, (70, 160, 255), (int(self.x), int(self.y)), self.radius)

        front_x = self.x + math.cos(self.theta) * (self.radius + 10)
        front_y = self.y + math.sin(self.theta) * (self.radius + 10)
        pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (front_x, front_y), 3)

        # --- wheel ---
        wheel_offset = self.radius - 5
        perp = self.theta + math.pi / 2
        left_wheel = (self.x + math.cos(perp) * wheel_offset,
                      self.y + math.sin(perp) * wheel_offset)
        right_wheel = (self.x - math.cos(perp) * wheel_offset,
                       self.y - math.sin(perp) * wheel_offset)

        pygame.draw.line(screen, (40, 40, 40), left_wheel,
                         (left_wheel[0] + math.cos(self.theta) * 10, left_wheel[1] + math.sin(self.theta) * 10), 4)
        pygame.draw.line(screen, (40, 40, 40), right_wheel,
                         (right_wheel[0] + math.cos(self.theta) * 10, right_wheel[1] + math.sin(self.theta) * 10), 4)
        
        pygame.draw.circle(screen, (0, 90, 190), (int(self.x), int(self.y)), self.radius, 2)

        # --- battery bar ---
        pygame.draw.rect(screen, (80, 80, 80), (self.x - 22, self.y + 28, 44, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 22, self.y + 28, 44 * self.battery / 100, 5))

        # --- water bar ---
        pygame.draw.rect(screen, (80, 80, 80), (self.x - 22, self.y + 36, 44, 5))
        pygame.draw.rect(screen, (0, 130, 255), (self.x - 22, self.y + 36, 44 * self.water / 100, 5))

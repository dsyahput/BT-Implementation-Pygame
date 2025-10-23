import time
from utils.behavior_tree import Node, Status

NEED_THIRST = 30

class MoveTo(Node):
    def __init__(self, robot, target_getter, tolerance=6):
        self.robot = robot
        self.target_getter = target_getter
        self.tolerance = tolerance

    def tick(self):
        tgt = self.target_getter()
        if tgt is None:
            return Status.FAILURE
        arrived = self.robot.move_towards(tgt, tolerance=self.tolerance)
        if arrived:
            return Status.SUCCESS
        return Status.RUNNING

class Recharge(Node):
    def __init__(self, robot):
        self.robot = robot

    def tick(self):
        if self.robot.active_task is None:
            self.robot.active_task = "charging"
        self.robot.action = "Recharging"
        self.robot.battery = min(100.0, self.robot.battery + 1.5)
        if self.robot.battery >= 100.0:
            self.robot.active_task = None
            self.robot.target = None
            return Status.SUCCESS
        return Status.RUNNING

class Refill(Node):
    def __init__(self, robot):
        self.robot = robot

    def tick(self):
        if self.robot.active_task is None:
            self.robot.active_task = "refilling"
        self.robot.action = "Refilling Water"
        self.robot.water = min(100.0, self.robot.water + 2.0)
        if self.robot.water >= 100.0:
            self.robot.active_task = None
            self.robot.target = None
            return Status.SUCCESS
        return Status.RUNNING

class FindDryPlant(Node):
    def __init__(self, robot, plants):
        self.robot = robot
        self.plants = plants

    def tick(self):
        if self.robot.target:
            if self.robot.target["thirst"] >= NEED_THIRST:
                if self.robot.active_task is None:
                    self.robot.active_task = "watering"
                return Status.SUCCESS
            else:
                self.robot.target = None

        dry = [p for p in self.plants if p["thirst"] >= NEED_THIRST]
        if not dry:
            return Status.FAILURE

        chosen = max(dry, key=lambda p: p["thirst"])
        self.robot.target = chosen
        if self.robot.active_task is None:
            self.robot.active_task = "watering"
        return Status.SUCCESS

class Water(Node):
    def __init__(self, robot, plants):
        self.robot = robot
        self.plants = plants

    def tick(self):
        if not self.robot.target:
            return Status.FAILURE
        self.robot.action = "Watering"
        self.robot.water = max(0.0, self.robot.water - 0.6)
        self.robot.target["thirst"] = max(0.0, self.robot.target["thirst"] - 2.0)
        if self.robot.target["thirst"] <= 5.0:
            self.robot.target["thirst"] = 0.0
            self.robot.target["last_watered"] = time.time()
            self.robot.active_task = None
            self.robot.target = None
            return Status.SUCCESS
        if self.robot.water <= 0.0:
            self.robot.active_task = None
            return Status.FAILURE
        return Status.RUNNING

class AllPlantsWatered(Node):
    def __init__(self, plants):
        self.plants = plants

    def tick(self):
        if all(p["thirst"] < NEED_THIRST for p in self.plants):
            return Status.SUCCESS
        return Status.FAILURE

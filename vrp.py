import math
import re
import sys
from pathlib import Path


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class Load:
    def __init__(self, id: int, start: Point, end: Point):
        self.id = id
        self.start = start
        self.end = end
        self.delivery_cost = math.sqrt((self.start.x - self.end.x) ** 2 + (self.start.y - self.end.y) ** 2)
        self.end_distance_from_depot = math.sqrt((self.end.x ** 2) + (self.end.y ** 2))


class Driver:
    def __init__(self):
        self.loads: list[Load] = []
        self.location = Point(0.0, 0.0)
        self.time_worked = 0
        self.clocked_out = False

    def distance_squared(self, destination: Point) -> float:
        return (self.location.x - destination.x) ** 2 + (self.location.y - destination.y) ** 2

    def distance_from_depot_squared(self) -> float:
        return self.location.x ** 2 + self.location.y ** 2

    def load_cost(self, load: Load) -> float:
        arrival = math.sqrt(self.distance_squared(load.start))
        delivery = load.delivery_cost
        return_to_depot = load.end_distance_from_depot
        return arrival + delivery + return_to_depot

    def add_load(self, load: Load):
        self.loads.append(load)

        # Add time worked
        arrival = math.sqrt(self.distance_squared(load.start))
        self.time_worked += arrival
        self.time_worked += load.delivery_cost

        # Set new location
        self.location = load.end

    def time_left(self) -> float:
        return 12 * 60 - self.time_worked

    def clock_out(self):
        self.time_worked += math.sqrt(self.distance_from_depot_squared())
        self.clocked_out = True


if __name__ == '__main__':
    """
    Handle CLI arguments
    """
    if not (len(sys.argv) == 2):
        print("Invalid arguments. Usage: python vrp.py input_file.txt", file=sys.stderr)
        exit(-1)

    input_file = sys.argv[1]
    input_file_path = Path(input_file)

    """
    Load file
    """
    loads: list[Load] = []
    # Pattern to match a line containing the load ID and its start/end points
    pattern = r'(\d+) \((-?\d*(?:\.\d+)?),(-?\d*(?:\.\d+)?)\) \((-?\d*(?:\.\d+)?),(-?\d*(?:\.\d+)?)\) *$'
    compiled = re.compile(pattern=pattern)
    with open(file=input_file_path, mode="r", encoding="utf8") as opened:
        for line in opened.readlines():
            # Skip headers
            if "loadNumber" in line:
                continue

            # Parse the load line into an object
            matched = compiled.match(string=line)
            if matched:
                load_id = int(matched.group(1))
                start = Point(float(matched.group(2)), float(matched.group(3)))
                end = Point(float(matched.group(4)), float(matched.group(5)))
                loads.append(Load(load_id, start, end))

    """
    Main algorithm loop
    
    1. Create a new driver.
    2. For all loads, calculate the cost of going to and delivering the order.
    3. Select and complete the cheapest load.
    4. Repeat until the only possibility is returning to the depot (not enough time for anything else).
    5. Repeat until all loads are delivered.
    """
    # Create initial driver
    drivers: list[Driver] = []
    driver = Driver()
    drivers.append(driver)

    while True:
        # Check if all loads done
        if len(loads) == 0:
            break

        # Check if we need a new driver
        if driver.clocked_out:
            driver = Driver()
            drivers.append(driver)

        # Calculate cost of each load
        load_costs = {driver.load_cost(load): load for load in loads}
        # Filter to only loads the driver can complete
        load_costs = {cost: load for (cost, load) in load_costs.items() if cost <= driver.time_left()}

        if len(load_costs) == 0:
            # Driver cannot complete any more jobs
            driver.clock_out()
        else:
            # Find cheapest job
            cheapest_loads = dict(sorted(load_costs.items()))  # Sort dict by cheapest job
            cheapest: Load = list(cheapest_loads.values())[0]

            # Find closest job
            closest_loads = {driver.distance_squared(load.start): load for (cost, load) in
                             load_costs.items()}  # Calculate distance to each load
            closest_loads = dict(sorted(closest_loads.items()))  # Sort dict by closest job
            closest: Load = list(closest_loads.values())[0]

            # Determine which one is furthest from the depot
            if cheapest.end_distance_from_depot > closest.end_distance_from_depot:
                chosen_load = cheapest
            else:
                chosen_load = closest

            driver.add_load(chosen_load)
            loads.remove(chosen_load)

    """
    Output driver loads
    """
    minutes_sum = 0
    for driver in drivers:
        print(
            f"[{','.join([str(load.id) for load in driver.loads])}]")  # debugging:  ({driver.time_worked}{' !!!' if driver.time_worked > 12 * 60 else ''})
        minutes_sum += driver.time_worked

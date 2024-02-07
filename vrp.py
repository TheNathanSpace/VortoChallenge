import math
import re
import sys
from pathlib import Path


class Point:
    def __init__(self, x: float, y: float):
        """
        A simple object representing Cartesian coordinates.
        """
        self.x = x
        self.y = y


class Load:
    def __init__(self, id: int, start: Point, end: Point):
        """
        An object representing a load to be delivered.

        :param id: The load's ID (as an integer, probably between 1 and 200)
        :param start: The load's starting location as Cartesian coordinates
        :param end: The load's ending location as Cartesian coordinates
        """
        self.id = id
        self.start = start
        self.end = end

        # These values will be used a lot for many drivers, so calculate them up-front.
        self.delivery_cost = math.sqrt((self.start.x - self.end.x) ** 2 + (self.start.y - self.end.y) ** 2)
        self.end_distance_from_depot = math.sqrt((self.end.x ** 2) + (self.end.y ** 2))

        # Check that the load is possible to complete within a 12-hour shift
        cost = self.delivery_cost + self.end_distance_from_depot + math.sqrt((self.start.x ** 2) + (self.start.y ** 2))
        if cost > 12 * 60:
            print(f"Impossible load. Cost: {cost}", file=sys.stderr)
            exit(-1)


class Driver:
    def __init__(self):
        """
        An object representing a driver, containing loads they've delivered,
        their current location, and how long they've worked.
        """
        self.loads: list[Load] = []
        self.location = Point(0.0, 0.0)  # Drivers start at the depot
        self.time_worked = 0
        self.clocked_out = False

    def distance_squared(self, destination: Point) -> float:
        """
        Returns the distance squared between the driver's current location
        and a given destination. The square-root of this value is not calculated
        for optimization, since it's not needed for straight comparison. If
        necessary, that will be done by whatever uses this value.

        :param destination: The destination to calculate the distance to.
        :return: The distance squared
        """
        return (self.location.x - destination.x) ** 2 + (self.location.y - destination.y) ** 2

    def distance_from_depot_squared(self) -> float:
        """
        Returns the distance squared between the driver's current location
        and the starting depot. The square-root of this value is not calculated
        for optimization, since it's not needed for straight comparison. If
        necessary, that will be done by whatever uses this value.

        :return: The distance squared
        """
        return self.location.x ** 2 + self.location.y ** 2

    def load_cost(self, load: Load) -> float:
        """
        Calculates the overall cost of the load, including:
        - Cost to get to load from driver's location
        - Cost to transport load
        - Cost to return to depot

        :param load: The load to calculate the cost of
        :return: The load's cost
        """
        arrival = math.sqrt(self.distance_squared(load.start))
        delivery = load.delivery_cost
        return_to_depot = load.end_distance_from_depot
        return arrival + delivery + return_to_depot

    def add_load(self, load: Load):
        """
        Assigns a load to the driver. Adds it to the
        driver's list of loads, increment's the driver's
        time worked, and updates the driver's new location.

        :param load: The load to assign
        """
        self.loads.append(load)

        # Add time worked
        arrival = math.sqrt(self.distance_squared(load.start))
        self.time_worked += arrival
        self.time_worked += load.delivery_cost

        # Set new location
        self.location = load.end

    def time_left(self) -> float:
        """
        :return: How much more time the driver can work
        """
        return 12 * 60 - self.time_worked

    def clock_out(self):
        """
        Increments the driver's worked time to get them
        back to the depot and marks them as clocked out.
        """
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
    # Will store all loads from file
    loads: list[Load] = []

    # Pattern to match a line containing the load ID and its start/end points
    pattern = r'(\d+) \((-?\d*(?:\.\d+)?),(-?\d*(?:\.\d+)?)\) \((-?\d*(?:\.\d+)?),(-?\d*(?:\.\d+)?)\) *$'
    compiled = re.compile(pattern=pattern)

    # Reads the file line-by-line
    with open(file=input_file_path, mode="r", encoding="utf8") as opened:
        for line in opened.readlines():
            # Skip headers
            if "loadNumber" in line:
                continue

            # Parse the load line into an object
            matched = compiled.match(string=line)
            if matched:
                # Add new load object to list
                load_id = int(matched.group(1))
                start = Point(float(matched.group(2)), float(matched.group(3)))
                end = Point(float(matched.group(4)), float(matched.group(5)))
                loads.append(Load(load_id, start, end))

    """
    Main algorithm loop
    
    1. Create a new driver.
    2. For all loads, calculate the distance between the driver and the load start location.
    3. Assign the closest load to the driver and remove it from the list.
    4. Repeat until the driver's only option is returning to the depot (not enough time for anything else).
    5. Repeat with a new driver until all loads are delivered.
    """
    # Create initial driver
    drivers: list[Driver] = []
    driver = Driver()
    drivers.append(driver)

    # Loop to assign loads and create new drivers when necessary
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

            # Assign the selected load to the driver
            driver.add_load(chosen_load)
            loads.remove(chosen_load)

    """
    Output driver loads
    """
    for driver in drivers:
        print(f"[{','.join([str(load.id) for load in driver.loads])}]")

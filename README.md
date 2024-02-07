# Vorto AI Coding Challenge

My solution to the Vorto AI 2023/2024 coding challenge.

## Execution

The program is all contained in `vrp.py`, and depends only on the Python Standard Library (no other dependencies).

```shell
# Run on single input file
python vrp.py [input file]

# Run on directory of input files
python evaluateShared.py --cmd "python vrp.py" --problemDir [test data directory]
```

## Algorithm

The problem is a variant of the "Vehicle Routing Problem with Pickup and Delivery," which is a variant of the "Vehicle
Routing Problem," which is a variant of the "Travelling Salesman Problem". Since it's a variation of TSP, which is
NP-hard, I would assume that an exact algorithmic solution for this problem _could_ be constructed.

However, given the implementation constraints (24 hours while in the midst of college classes, etc.), I opted to use a
much simpler heuristic technique. The algorithm steps are as follows:

1. Create a new driver.
2. For all remaining loads, calculate the distance between the driver and the load's starting position.
3. Assign a load to the driver and remove it from the list.
    - First, filter all loads that cost too much (i.e., the time taken is greater than the driver's remaining shift
      time).
    - Second, find the load with the start position closest to the driver's location.
    - Third, find the load with the cheapest total cost (arrival + transportation + return to depot).
    - Out of these two loads, choose the one with an end position furthest from the depot.
4. Repeat until the driver's only option is returning to the depot (i.e., there's not enough shift time for them to
   deliver anything else).
5. Repeat with a new driver until all loads are delivered.

I tried a few different criteria for #3 before settling on this method. The below values are based on the provided test
data:

| Method                      | Mean Cost              | Mean Time              |
|-----------------------------|------------------------|------------------------|
| Cheapest overall cost       | 56484.8752497138       | 64.58051204681396ms    |
| Start closest to driver     | 47963.81284400135      | 73.84626865386963ms    |
| **End furthest from depot** | **47894.524588592176** | **77.5111198425293ms** |
| End closest to depot        | 55610.08419697672      | 76.62986516952515ms    |

Since the "end furthest from depot" criteria resulted in the lowest cost with a minimal increase in time, I selected
that for the final implementation. Since "closest to driver" and "end furthest from depot" are so similar in cost and
time, the best heuristic probably depends on the dataset.
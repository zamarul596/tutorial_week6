import csv
from pathlib import Path
import random
import sys

# Function to read the CSV file and convert it to the desired format
def read_csv_to_dict(file_path):
    """
    Reads CSV and returns dict mapping program -> list of ratings (floats).
    Accepts file path (str or Path). Raises FileNotFoundError if not found.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found at: {p}")

    program_ratings = {}
    with p.open(mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        # Read header to get/validate time slots (we ignore header content except to advance)
        try:
            header = next(reader)
        except StopIteration:
            return program_ratings  # empty file

        for row in reader:
            if not row:
                continue
            program = row[0].strip()
            # Convert the ratings to floats; ignore empty strings
            try:
                ratings = [float(x) for x in row[1:] if x != ""]
            except ValueError as e:
                raise ValueError(f"Invalid numeric value in CSV for program '{program}': {e}")
            program_ratings[program] = ratings

    return program_ratings


# --- Connect to CSV in repository ---
# Use the CSV that's in the same repo folder as this script: program_ratings.csv
script_dir = Path(__file__).resolve().parent
file_path = script_dir / "program_ratings.csv"

try:
    program_ratings_dict = read_csv_to_dict(file_path)
except FileNotFoundError as e:
    print(e)
    print("Ensure 'program_ratings.csv' is located in the same folder as main.py.")
    sys.exit(1)
except Exception as e:
    print("Error reading CSV:", e)
    sys.exit(1)

# Print the result (you can also return or process it further)
for program, ratings in program_ratings_dict.items():
    print(f"'{program}': {ratings},")


##################################### DEFINING PARAMETERS AND DATASET ################################################################
# Sample rating programs dataset for each time slot.
ratings = program_ratings_dict

GEN = 100
POP = 50
CO_R = 0.8
MUT_R = 0.2
EL_S = 2

all_programs = list(ratings.keys())  # all programs
all_time_slots = list(range(6, 6 + len(next(iter(ratings.values())))))  # time slots length matches CSV columns

######################################### DEFINING FUNCTIONS ########################################################################
# defining fitness function
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating

# initializing the population (generate all permutations) -- careful: factorial growth
def initialize_pop(programs):
    if not programs:
        return [[]]

    all_schedules = []
    for i in range(len(programs)):
        for schedule in initialize_pop(programs[:i] + programs[i + 1:]):
            all_schedules.append([programs[i]] + schedule)

    return all_schedules

# selection: find best schedule from list
def finding_best_schedule(all_schedules):
    best_schedule = []
    max_ratings = float("-inf")

    for schedule in all_schedules:
        total_ratings = fitness_function(schedule)
        if total_ratings > max_ratings:
            max_ratings = total_ratings
            best_schedule = schedule

    return best_schedule

# calling the pop func.
all_possible_schedules = initialize_pop(all_programs)

# callin the schedule func.
best_schedule = finding_best_schedule(all_possible_schedules)


############################################# GENETIC ALGORITHM #############################################################################

# Crossover
def crossover(schedule1, schedule2):
    if len(schedule1) < 3:
        return schedule1.copy(), schedule2.copy()
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2

# mutating
def mutate(schedule):
    if not schedule:
        return schedule
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule

# calling the fitness func.
def evaluate_fitness(schedule):
    return fitness_function(schedule)

def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP, crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    population = [initial_schedule]

    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    for generation in range(generations):
        new_population = []

        # Elitism
        population.sort(key=lambda schedule: fitness_function(schedule), reverse=True)
        new_population.extend(population[:elitism_size])

        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()

            if random.random() < mutation_rate:
                child1 = mutate(child1)
            if random.random() < mutation_rate:
                child2 = mutate(child2)

            new_population.extend([child1, child2])

        population = new_population[:population_size]

    return population[0]

##################################################### RESULTS ###################################################################################

# brute force
initial_best_schedule = finding_best_schedule(all_possible_schedules)

rem_t_slots = len(all_time_slots) - len(initial_best_schedule)
genetic_schedule = genetic_algorithm(initial_best_schedule, generations=GEN, population_size=POP, elitism_size=EL_S)

final_schedule = initial_best_schedule + genetic_schedule[:rem_t_slots]

print("\nFinal Optimal Schedule:")
for time_slot, program in enumerate(final_schedule):
    hour = all_time_slots[time_slot] if time_slot < len(all_time_slots) else f"slot{time_slot}"
    print(f"Time Slot {hour:02d}:00 - Program {program}")

print("Total Ratings:", fitness_function(final_schedule))

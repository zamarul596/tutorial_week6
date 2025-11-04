import csv
from pathlib import Path
import random
import sys


#######################################
# 1. Read CSV File
#######################################
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
        try:
            header = next(reader)
        except StopIteration:
            return program_ratings  # empty file

        for row in reader:
            if not row:
                continue
            program = row[0].strip()
            try:
                ratings = [float(x) for x in row[1:] if x != ""]
            except ValueError as e:
                raise ValueError(f"Invalid numeric value in CSV for program '{program}': {e}")
            program_ratings[program] = ratings

    return program_ratings


#######################################
# 2. Load CSV
#######################################
script_dir = Path(__file__).resolve().parent
file_path = script_dir / "program_ratings.csv"

print("🔍 Looking for:", file_path)

try:
    program_ratings_dict = read_csv_to_dict(file_path)
except FileNotFoundError as e:
    print(e)
    print("⚠️ Ensure 'program_ratings.csv' is located in the same folder as main.py.")
    sys.exit(1)
except Exception as e:
    print("❌ Error reading CSV:", e)
    sys.exit(1)

if not program_ratings_dict:
    print("⚠️ CSV file is empty or has no valid data.")
    sys.exit(1)

print("\n✅ Programs and Ratings Loaded:")
for program, ratings in program_ratings_dict.items():
    print(f"  {program}: {ratings}")

#######################################
# 3. Define Parameters
#######################################
ratings = program_ratings_dict

GEN = 100        # Number of generations
POP = 50         # Population size
CO_R = 0.8       # Crossover rate
MUT_R = 0.2      # Mutation rate
EL_S = 2         # Elitism size

all_programs = list(ratings.keys())
num_slots = len(next(iter(ratings.values())))
all_time_slots = list(range(6, 6 + num_slots))


#######################################
# 4. Fitness Function
#######################################
def fitness_function(schedule):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        total_rating += ratings[program][time_slot]
    return total_rating


#######################################
# 5. Genetic Algorithm
#######################################
def crossover(schedule1, schedule2):
    if len(schedule1) < 3:
        return schedule1.copy(), schedule2.copy()
    crossover_point = random.randint(1, len(schedule1) - 2)
    child1 = schedule1[:crossover_point] + schedule2[crossover_point:]
    child2 = schedule2[:crossover_point] + schedule1[crossover_point:]
    return child1, child2


def mutate(schedule):
    if not schedule:
        return schedule
    mutation_point = random.randint(0, len(schedule) - 1)
    new_program = random.choice(all_programs)
    schedule[mutation_point] = new_program
    return schedule


def genetic_algorithm(initial_schedule, generations=GEN, population_size=POP,
                      crossover_rate=CO_R, mutation_rate=MUT_R, elitism_size=EL_S):
    population = [initial_schedule.copy()]

    # Initialize population with random shuffles
    for _ in range(population_size - 1):
        random_schedule = initial_schedule.copy()
        random.shuffle(random_schedule)
        population.append(random_schedule)

    print("\n🚀 Starting Genetic Algorithm Optimization...")

    for generation in range(generations):
        population.sort(key=lambda s: fitness_function(s), reverse=True)
        new_population = population[:elitism_size]  # Elitism

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

        # Optional: print progress every 10 generations
        if (generation + 1) % 10 == 0:
            best_fit = fitness_function(population[0])
            print(f"Generation {generation + 1}: Best Fitness = {best_fit:.2f}")

    print("✅ Optimization Complete.")
    return population[0]


#######################################
# 6. Run Optimization
#######################################
initial_schedule = all_programs.copy()
random.shuffle(initial_schedule)

best_schedule = genetic_algorithm(initial_schedule)

#######################################
# 7. Display Results
#######################################
print("\n🎯 Final Optimal Schedule:")
total_rating = 0
for time_slot, program in enumerate(best_schedule):
    hour = all_time_slots[time_slot]
    rating = ratings[program][time_slot]
    total_rating += rating
    print(f"Time Slot {hour:02d}:00 - Program {program} (Rating: {rating})")

print(f"\n🏆 Total Ratings: {total_rating:.2f}")

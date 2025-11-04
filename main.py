import streamlit as st
import csv
from pathlib import Path
import random

#######################################
# 1. Read CSV File
#######################################
def read_csv_to_dict(file_path):
    p = Path(file_path)
    if not p.exists():
        st.error(f"CSV file not found at: {p}")
        return {}

    program_ratings = {}
    with p.open(mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        try:
            header = next(reader)
        except StopIteration:
            return {}

        for row in reader:
            if not row:
                continue
            program = row[0].strip()
            try:
                ratings = [float(x) for x in row[1:] if x != ""]
            except ValueError as e:
                st.error(f"Invalid numeric value in CSV for program '{program}': {e}")
                return {}
            program_ratings[program] = ratings

    return program_ratings


#######################################
# 2. Streamlit UI Setup
#######################################
st.title("📺 Optimal TV Program Scheduler (Genetic Algorithm)")
st.write("Upload your program ratings CSV file below:")

uploaded_file = st.file_uploader("Upload program_ratings.csv", type=["csv"])

#######################################
# 3. Once File Uploaded
#######################################
if uploaded_file:
    # Save uploaded file temporarily
    temp_path = Path("program_ratings.csv")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    ratings = read_csv_to_dict(temp_path)

    if not ratings:
        st.warning("No valid data found in CSV.")
        st.stop()

    st.subheader("Programs and Ratings Loaded")
    st.dataframe(ratings)

    #######################################
    # 4. Parameter Input Section
    #######################################
    st.subheader("⚙️ Genetic Algorithm Parameters")

    CO_R = st.slider(
        "Crossover Rate (CO_R)",
        min_value=0.0,
        max_value=0.95,
        value=0.8,
        step=0.01,
        help="Controls how often crossover occurs between parents (0 to 0.95)."
    )

    MUT_R = st.slider(
        "Mutation Rate (MUT_R)",
        min_value=0.01,
        max_value=0.05,
        value=0.02,
        step=0.01,
        help="Controls how often mutations occur in offspring (0.01 to 0.05)."
    )

    st.info(f"Selected → Crossover Rate: **{CO_R}**, Mutation Rate: **{MUT_R}**")

    GEN = 100
    POP = 50
    EL_S = 2

    all_programs = list(ratings.keys())
    num_slots = len(next(iter(ratings.values())))
    all_time_slots = list(range(6, 6 + num_slots))

    #######################################
    # 5. Genetic Algorithm Components
    #######################################
    def fitness_function(schedule):
        total_rating = 0
        for time_slot, program in enumerate(schedule):
            total_rating += ratings[program][time_slot]
        return total_rating

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
        for _ in range(population_size - 1):
            random_schedule = initial_schedule.copy()
            random.shuffle(random_schedule)
            population.append(random_schedule)

        progress_bar = st.progress(0)
        for generation in range(generations):
            population.sort(key=lambda s: fitness_function(s), reverse=True)
            new_population = population[:elitism_size]

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
            progress_bar.progress((generation + 1) / generations)

        return population[0]

    #######################################
    # 6. Run Algorithm Button
    #######################################
    if st.button("🚀 Run Genetic Algorithm"):
        st.subheader("Running Genetic Algorithm...")
        initial_schedule = all_programs.copy()
        random.shuffle(initial_schedule)

        best_schedule = genetic_algorithm(initial_schedule)

        #######################################
        # 7. Display Results
        #######################################
        st.subheader("🏆 Final Optimal Schedule")
        total_rating = 0
        results = []
        for time_slot, program in enumerate(best_schedule):
            hour = all_time_slots[time_slot]
            rating = ratings[program][time_slot]
            total_rating += rating
            results.append({"Time Slot": f"{hour:02d}:00", "Program": program, "Rating": rating})

        st.dataframe(results)
        st.success(f"Total Ratings: {total_rating:.2f}")

else:
    st.info("Upload a CSV file to start.")

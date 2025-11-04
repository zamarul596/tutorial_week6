import streamlit as st
import csv
from pathlib import Path
import random
import pandas as pd

st.set_page_config(page_title="TV Scheduler", layout="wide")

#######################################
# Read CSV Function
#######################################
def read_csv_to_dict(file_path):
    program_ratings = {}
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # first row (time slots)
        for row in reader:
            if not row or not row[0].strip():
                continue
            program = row[0].strip()
            # keep ALL columns (not stopping at empty)
            ratings = []
            for val in row[1:]:
                try:
                    ratings.append(float(val.strip()) if val.strip() != "" else 0.0)
                except ValueError:
                    ratings.append(0.0)
            program_ratings[program] = ratings
    return program_ratings, header


#######################################
# Genetic Algorithm Functions
#######################################
def fitness_function(schedule, ratings):
    total_rating = 0
    for time_slot, program in enumerate(schedule):
        if time_slot < len(ratings[program]):
            total_rating += ratings[program][time_slot]
    return total_rating


def crossover(schedule1, schedule2):
    if len(schedule1) < 3:
        return schedule1.copy(), schedule2.copy()
    point = random.randint(1, len(schedule1) - 2)
    return (schedule1[:point] + schedule2[point:], schedule2[:point] + schedule1[point:])


def mutate(schedule, all_programs):
    point = random.randint(0, len(schedule) - 1)
    schedule[point] = random.choice(all_programs)
    return schedule


def genetic_algorithm(ratings, all_programs, generations=100, population_size=50,
                      crossover_rate=0.8, mutation_rate=0.2, elitism_size=2):
    initial_schedule = all_programs.copy()
    random.shuffle(initial_schedule)
    population = [initial_schedule.copy() for _ in range(population_size)]

    for _ in range(generations):
        population.sort(key=lambda s: fitness_function(s, ratings), reverse=True)
        new_population = population[:elitism_size]

        while len(new_population) < population_size:
            p1, p2 = random.choices(population, k=2)
            if random.random() < crossover_rate:
                c1, c2 = crossover(p1, p2)
            else:
                c1, c2 = p1.copy(), p2.copy()
            if random.random() < mutation_rate:
                c1 = mutate(c1, all_programs)
            if random.random() < mutation_rate:
                c2 = mutate(c2, all_programs)
            new_population += [c1, c2]

        population = new_population[:population_size]

    return population[0]


#######################################
# Display Schedule Function
#######################################
def display_schedule(schedule, ratings, title, co_r, mut_r, header):
    num_slots = max(len(v) for v in ratings.values())
    all_time_slots = list(range(6, 6 + num_slots))  # dynamic hours

    total_rating = 0
    data = []
    for i, program in enumerate(schedule):
        if i >= num_slots:
            break
        hour = all_time_slots[i]
        rating = ratings[program][i]
        total_rating += rating
        data.append({
            "Time Slot": f"{hour:02d}:00",
            "Program": program,
            "Rating": rating
        })

    df = pd.DataFrame(data)
    st.subheader(title)
    st.write(f"**Crossover Rate:** {co_r} | **Mutation Rate:** {mut_r}")
    st.dataframe(df, use_container_width=True, height=600)
    st.success(f"Total Ratings: {total_rating:.2f}")


#######################################
# Streamlit Interface
#######################################
st.title("🎬 Optimal TV Program Scheduler (Genetic Algorithm)")

st.markdown("### Step 1: Set Parameters for Each Trial")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Default Parameters (Trial 0)**")
    default_CO_R, default_MUT_R = 0.8, 0.2
    st.write(f"Crossover Rate: **{default_CO_R}**")
    st.write(f"Mutation Rate: **{default_MUT_R}**")
with col2:
    st.markdown("**Parameter Ranges**")
    st.write("- Crossover Rate (CO_R): 0.0 – 0.95")
    st.write("- Mutation Rate (MUT_R): 0.01 – 0.05")

trial_params = []
st.markdown("---")
for i in range(1, 4):
    st.subheader(f"Trial {i}")
    co_r = st.slider(f"Trial {i} - Crossover Rate", 0.0, 0.95, 0.8, 0.01, key=f"co_r_{i}")
    mut_r = st.slider(f"Trial {i} - Mutation Rate", 0.01, 0.05, 0.02, 0.01, key=f"mut_r_{i}")
    trial_params.append((co_r, mut_r))

st.markdown("---")
st.markdown("### Step 2: Upload CSV File")

uploaded = st.file_uploader("Upload your program_ratings.csv file", type=["csv"])

if uploaded:
    temp_path = Path("program_ratings.csv")
    temp_path.write_bytes(uploaded.getbuffer())

    ratings, header = read_csv_to_dict(temp_path)
    all_programs = list(ratings.keys())

    st.markdown("### Step 3: Run Algorithm")
    if st.button("Run All Trials"):
        st.header("📊 Final Optimal Schedules")

        # Default run
        best_default = genetic_algorithm(ratings, all_programs,
                                         crossover_rate=default_CO_R,
                                         mutation_rate=default_MUT_R)
        display_schedule(best_default, ratings, "Default Run", default_CO_R, default_MUT_R, header)

        # 3 User Trials
        for i, (co_r, mut_r) in enumerate(trial_params, start=1):
            best_trial = genetic_algorithm(ratings, all_programs,
                                           crossover_rate=co_r,
                                           mutation_rate=mut_r)
            display_schedule(best_trial, ratings, f"Trial {i} Results", co_r, mut_r, header)
else:
    st.info("Upload your CSV file to continue.")

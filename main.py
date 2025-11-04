import streamlit as st
import pandas as pd
import random

# --- Function to read CSV file ---
def read_csv_to_dict(file_path):
    df = pd.read_csv(file_path)
    program_ratings = {}
    for _, row in df.iterrows():
        program = row["Program"]
        rating = row["Rating"]
        if program in program_ratings:
            program_ratings[program].append(float(rating))
        else:
            program_ratings[program] = [float(rating)]
    return program_ratings


# --- Simple Genetic Algorithm simulation (replace with your logic) ---
def genetic_algorithm(program_ratings, crossover_rate, mutation_rate):
    programs = list(program_ratings.keys())
    schedule = []

    # Simulate schedule generation with all time slots
    times = [
        "06:00", "07:00", "08:00", "09:00", "10:00",
        "11:00", "12:00", "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"
    ]

    for t in times:
        program = random.choice(programs)
        rating = random.choice(program_ratings[program])
        schedule.append((t, program, rating))

    df_schedule = pd.DataFrame(schedule, columns=["Time", "Program", "Rating"])
    return df_schedule


# --- Streamlit App ---
st.title("Genetic Algorithm TV Scheduling")

# Step 1: Parameter selection for 3 trials
st.header("Set Parameters for Each Trial")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Trial 1")
    co_r1 = st.slider("Crossover Rate (Trial 1)", 0.0, 0.95, 0.8)
    mut_r1 = st.slider("Mutation Rate (Trial 1)", 0.01, 0.05, 0.02)

with col2:
    st.subheader("Trial 2")
    co_r2 = st.slider("Crossover Rate (Trial 2)", 0.0, 0.95, 0.85)
    mut_r2 = st.slider("Mutation Rate (Trial 2)", 0.01, 0.05, 0.03)

st.subheader("Trial 3")
co_r3 = st.slider("Crossover Rate (Trial 3)", 0.0, 0.95, 0.9)
mut_r3 = st.slider("Mutation Rate (Trial 3)", 0.01, 0.05, 0.04)

# Step 2: Upload file
uploaded_file = st.file_uploader("Upload Program Ratings CSV", type=["csv"])

# Step 3: Run GA
if uploaded_file is not None:
    program_ratings = read_csv_to_dict(uploaded_file)

    st.markdown("---")
    st.subheader("📊 Default Run (CO_R=0.8, MUT_R=0.2)")
    default_schedule = genetic_algorithm(program_ratings, 0.8, 0.2)
    st.dataframe(default_schedule)

    # Trial 1
    st.markdown("---")
    st.subheader(f"🧪 Trial 1 Results (CO_R={co_r1}, MUT_R={mut_r1})")
    schedule1 = genetic_algorithm(program_ratings, co_r1, mut_r1)
    st.dataframe(schedule1)

    # Trial 2
    st.markdown("---")
    st.subheader(f"🧪 Trial 2 Results (CO_R={co_r2}, MUT_R={mut_r2})")
    schedule2 = genetic_algorithm(program_ratings, co_r2, mut_r2)
    st.dataframe(schedule2)

    # Trial 3
    st.markdown("---")
    st.subheader(f"🧪 Trial 3 Results (CO_R={co_r3}, MUT_R={mut_r3})")
    schedule3 = genetic_algorithm(program_ratings, co_r3, mut_r3)
    st.dataframe(schedule3)

else:
    st.info("Please upload a CSV file to start.")

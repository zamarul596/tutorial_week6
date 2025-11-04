import streamlit as st
import pandas as pd
import random

# Title
st.title("TV Program Scheduling Optimization")

# Step 1: User selects crossover and mutation rates for 3 trials
st.subheader("Step 1: Enter GA Parameters for Trials")
col1, col2 = st.columns(2)
with col1:
    co1 = st.slider("Trial 1 Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.01)
    co2 = st.slider("Trial 2 Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.01)
    co3 = st.slider("Trial 3 Crossover Rate (CO_R)", 0.0, 0.95, 0.8, 0.01)
with col2:
    mu1 = st.slider("Trial 1 Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)
    mu2 = st.slider("Trial 2 Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)
    mu3 = st.slider("Trial 3 Mutation Rate (MUT_R)", 0.01, 0.05, 0.02, 0.01)

# Step 2: Upload CSV
st.subheader("Step 2: Upload the Program Ratings CSV")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.write("### Uploaded Data Preview")
    st.dataframe(data)

    # Ensure 'Hour' or 'Time Slot' column sorted properly
    if 'Hour' in data.columns:
        data = data.sort_values(by='Hour')
    elif 'Time Slot' in data.columns:
        data['Hour'] = data['Time Slot'].str.extract('(\d+)').astype(int)
        data = data.sort_values(by='Hour')

    hours = sorted(data['Hour'].unique())

    def run_genetic_algorithm(data, co_rate, mut_rate):
        """Mock simple scheduling optimizer — just random shuffle."""
        programs = list(data['Program'].unique())
        random.shuffle(programs)
        schedule = []
        for hour in hours:
            prog = random.choice(programs)
            rating = data[data['Program'] == prog]['Rating'].mean()
            schedule.append({'Hour': hour, 'Program': prog, 'Rating': round(rating, 2)})
        df = pd.DataFrame(schedule)
        return df

    # Step 3: Run Trials
    if st.button("Run Optimization"):
        st.write("### Default Trial (CO_R=0.8, MUT_R=0.2)")
        default_df = run_genetic_algorithm(data, 0.8, 0.2)
        st.dataframe(default_df)

        st.write("### Trial 1 Results")
        df1 = run_genetic_algorithm(data, co1, mu1)
        st.dataframe(df1)

        st.write("### Trial 2 Results")
        df2 = run_genetic_algorithm(data, co2, mu2)
        st.dataframe(df2)

        st.write("### Trial 3 Results")
        df3 = run_genetic_algorithm(data, co3, mu3)
        st.dataframe(df3)
else:
    st.info("Please upload a CSV file to continue.")

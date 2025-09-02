import streamlit as st
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import plotly.express as px

# DB Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0420",
    database="securecheck"
)
cursor = mydb.cursor()
st.set_page_config(page_title="🚦 Multi-National Traffic Data Insights", layout="wide")
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📋 Vehicle Logs", "🧾 Add Police Log + Predict", "📒Immediate Data Insights"])

# Function to set background image from a URL
def set_bg_image():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("https://static.vecteezy.com/system/resources/thumbnails/060/283/822/small_2x/calm-beach-gradient-background-abstract-ocean-coast-wallpaper-smooth-wavy-seaside-line-backdrop-pastel-light-blue-and-yellow-blurred-waves-concept-soft-summer-vacation-banner-template-vector.jpg");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_bg_image()

# Streamlit app content here
st.title("Welcome to the Multi National Traffic Data")

st.sidebar.markdown("## 🔎 SQL Filters")
def fetch_options(col_name):
    cursor.execute(f"SELECT DISTINCT {col_name} FROM trafficlogs")
    return [row[0] for row in cursor.fetchall()]
selected_country = st.sidebar.selectbox("Country", ["All"] + fetch_options("country_name"))
selected_gender = st.sidebar.selectbox("Gender", ["All"] + fetch_options("driver_gender"))
selected_violation = st.sidebar.selectbox("Violation", ["All"] + fetch_options("violation"))
def apply_filters(df):
    if selected_country != "All":
        df = df[df['country_name'] == selected_country]
    if selected_gender != "All":
        df = df[df['driver_gender'] == selected_gender]
    if selected_violation != "All":
        df = df[df['violation_raw'] == selected_violation]
    return df
if page == "🏠 Home":
    st.title("🚦 Multi-National Traffic Data Insights")
    st.markdown("### Welcome to the Real-Time Traffic Log and Analytics Platform")
    cursor.execute("SELECT * FROM trafficlogs")
    df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)

    st.subheader("📈 Violation Frequency")
    violation_counts = df['violation'].value_counts().reset_index()
    violation_counts.columns = ['violation', 'count']
    violation_fig = px.bar(
        violation_counts,
        x='violation',
        y='count',
        labels={'violation': 'Violation', 'count': 'Count'},
        color_discrete_sequence=['#800000']  # Maroon color
    )
    st.plotly_chart(violation_fig, use_container_width=True)


    search_counts = df['stop_outcome'].value_counts().reset_index()
    search_counts.columns = ['stop_outcome', 'count']

    st.subheader("📈 Search Outcome Breakdown")
    search_fig = px.pie(df, names=df['stop_outcome'].unique(), title='Search Outcome Share')
    st.plotly_chart(search_fig, use_container_width=True)

    st.subheader("📈 Arrest Outcome Count")
    arrest_fig = px.histogram(df, x='stop_outcome', color='is_arrested', barmode='group')
    st.plotly_chart(arrest_fig, use_container_width=True)

    st.subheader("🚘 Countrywise Violations and Outcomes")

    # Filter and count drug-related stops per vehicle
    #risky_vehicles = df[df['drugs_related_stop'] == "Yes"]['vehicle_number'].value_counts().reset_index()
    #risky_vehicles.columns = ['vehicle_number', 'drug_related_stops']

    sunburst_data = (
    df.groupby(['country_name', 'violation_raw', 'stop_outcome'])
    .size()
    .reset_index(name='count')
    )

# Create the sunburst chart
    sunburst_fig = px.sunburst(
    sunburst_data,
    path=['country_name', 'violation_raw', 'stop_outcome'],
    values='count',
    title='Sunburst Chart: Country, Violation, and Stop Outcome'
    )

    st.plotly_chart(sunburst_fig, use_container_width=True)


elif page == "📋 Vehicle Logs":
    st.header("📋 Traffic Stop Logs, Violations, and Officer Reports")
    cursor.execute("SELECT * FROM trafficlogs")
    df = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
    df_filtered = apply_filters(df)
    st.dataframe(df_filtered, use_container_width=True)

    if not df_filtered.empty:
        st.download_button("📅 Export Filtered Data", data=df_filtered.to_csv(index=False), file_name="filtered_logs.csv", mime="text/csv")

        st.subheader("📈 Violation Frequency")
        violation_counts_filtered = df_filtered['violation'].value_counts().reset_index()
        violation_counts_filtered.columns = ['violation', 'count']
        fig = px.bar(violation_counts_filtered, x='violation', y='count', labels={'violation': 'Violation', 'count': 'Count'})
        fig.update_traces(marker_color='#FFD700')  # Gold color
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📰 Officer Narrative Report")
        selected_row = st.selectbox("Select a row to generate a narrative:", df_filtered.index)
        row = df_filtered.loc[selected_row]

        narrative = f"🚗 A {row['driver_age_raw']}-year-old {row['driver_gender']} driver was stopped for {row['violation']} at {row['stop_time']}. "
        narrative += "No search was conducted, " if row['search_conducted'] == "No" else "A search was conducted, "
        narrative += f"and he received a {row['stop_outcome'].lower()}. "
        narrative += f"The stop lasted {row['stop_duration']} and was "
        narrative += "drug-related." if row['drugs_related_stop'] == "Yes" else "not drug-related."
        st.success(narrative)
    else:
        st.warning("No records match the selected filters.")

elif page == "🧾 Add Police Log + Predict":
    st.header("📝 Add New Police Log & Predict Outcome and Violation")
    with st.form("police_log_form"):
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")
        country_name = st.text_input("Country Name")
        driver_gender = st.selectbox("Driver Gender", ["male", "female"])
        driver_age_raw = st.number_input("Driver Age", min_value=16, max_value=100, step=1)
        driver_race = st.text_input("Driver Race")
        violation_raw = st.text_input("Violation Raw")
        violation = st.text_input("Violation")
        search_conducted = st.selectbox("Was a Search Conducted?", ["Yes", "No"])
        search_type = st.text_input("Search Type")
        is_arrested = st.selectbox("Was Arrest Made?", ["Yes", "No"])
        drugs_related_stop = st.selectbox("Was it Drug Related?", ["Yes", "No"])
        stop_duration = st.text_input("Stop Duration (e.g., 0-15 Min)")
        vehicle_number = st.text_input("Vehicle Number")
        submitted = st.form_submit_button("Predict Stop Outcome & Violation")

        if submitted:
            st.success("✅ Prediction complete (this is a placeholder). ML model will be integrated here.")
            try:
                gender_short = "M" if driver_gender.lower().startswith("m") else "F"
                summary_query = """
                    SELECT violation, stop_outcome, COUNT(*) as freq
                    FROM trafficlogs
                    WHERE driver_gender = %s AND driver_race = %s AND country_name = %s
                    GROUP BY violation, stop_outcome
                    ORDER BY freq DESC
                    LIMIT 1;
                """
                cursor.execute(summary_query, (gender_short, driver_race, country_name))
                result = cursor.fetchone()
                if result:
                    top_violation, top_outcome, freq = result
                    search_phrase = "A search was conducted" if search_conducted == "Yes" else "No search was conducted"
                    drug_phrase = "and was drug-related." if drugs_related_stop == "Yes" else "and was not drug-related."
                    detailed_summary = f"🚗 A {driver_age_raw}-year-old {driver_race} {driver_gender} driver was stopped for {top_violation} at {stop_time}. "
                    detailed_summary += f"{search_phrase}, and received a {top_outcome.lower()}. "
                    detailed_summary += f"The stop lasted {stop_duration} {drug_phrase}"
                    st.success(detailed_summary)
                else:
                    st.info("No historical data found to summarize this combination.")
            except Exception as e:
                st.error(f"❌ Error generating summary: {e}")

elif page == "📒 Immediate Data Insights":
    st.header("🚦 Overall Traffic Insights")  # Updated header

selected_query = st.selectbox("**Select a Query to Run**", [
    "Top 10 vehicle numbers involved in drug-related stops",
    "Vehicle most frequantly searched",
    "Which driver age group had the highest arrest rate?",
    "What is the gender distribution of drivers stopped in each country?",
    "Which race and gender combination has the highest search rate?",
    "What time of day sees the most traffic stops?",
    "What is the average stop duration for different violations?",
    "Are stops during the night more likely to lead to arrests?",
    "Which violations are most associated with searches or arrests?",
    "Which violations are most common among younger drivers (<25)?",
    "Is there a violation that rarely results in search or arrest?",
    "Which countries report the highest rate of drug-related stops?",
    "What is the arrest rate by country and violation?",
    "Which country has the most stops with search conducted?",
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops (Year, Month, Hour)",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country (Age, Gender, and Race)",
    "Top 5 Violations with Highest Arrest Rates"
])

query_map = {
    "Top 10 vehicle numbers involved in drug-related stops":"SELECT vehicle_number, COUNT(*) AS drug_related_stops FROM trafficlogs WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY drug_related_stops DESC LIMIT 10;",
    "Vehicle most frequantly searched":"SELECT vehicle_number, COUNT(*) AS search_count FROM trafficlogs WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY search_count DESC;",
    "Which driver age group had the highest arrest rate?":"SELECT driver_age_raw, COUNT(*) AS arrest_count FROM trafficlogs WHERE is_arrested = TRUE GROUP BY driver_age_raw ORDER BY arrest_count DESC;",
    "What is the gender distribution of drivers stopped in each country?":"SELECT country_name, driver_gender, COUNT(*) AS total_stops FROM trafficlogs GROUP BY country_name, driver_gender;",
    "Which race and gender combination has the highest search rate?":"SELECT driver_race, driver_gender,  COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches, ROUND(SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS search_rate FROM trafficlogs GROUP BY driver_race, driver_gender ORDER BY search_rate DESC;",
    "What time of day sees the most traffic stops?":"SELECT HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) AS hour_of_day, COUNT(*) AS stop_count FROM trafficlogs GROUP BY hour_of_day ORDER BY stop_count DESC;",
    "What is the average stop duration for different violations?":"SELECT violation, AVG(CASE stop_duration WHEN '0-15 Min' THEN 15 WHEN '16-30 Min' THEN 30 WHEN '30+ Min' THEN 45 END) AS avg_duration_minutes FROM trafficlogs GROUP BY violation;",
    "Are stops during the night more likely to lead to arrests?":"SELECT CASE WHEN HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) BETWEEN 20 AND 23 OR HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) BETWEEN 0 AND 5 THEN 'Night' ELSE 'Day' END AS time_period, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM trafficlogs GROUP BY time_period;",
    "Which violations are most associated with searches or arrests?":"SELECT violation, COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests FROM trafficlogs GROUP BY violation ORDER BY total_searches DESC, total_arrests DESC;",
    "Which violations are most common among younger drivers (<25)?":"SELECT violation, COUNT(*) AS count FROM trafficlogs WHERE driver_age_raw < 25 GROUP BY violation ORDER BY count DESC;",
    "Is there a violation that rarely results in search or arrest?":"SELECT violation, COUNT(*) AS total, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests FROM trafficlogs GROUP BY violation HAVING searches = 0 AND arrests = 0;",
    "Which countries report the highest rate of drug-related stops?":"SELECT country_name, COUNT(*) AS total_stops, SUM(CASE WHEN drugs_related_stop = TRUE THEN 1 ELSE 0 END) AS drug_related, ROUND(SUM(CASE WHEN drugs_related_stop = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS drug_rate FROM trafficlogs GROUP BY country_name ORDER BY drug_rate DESC;",
    "What is the arrest rate by country and violation?":"SELECT country_name, violation, COUNT(*) AS total, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM trafficlogs GROUP BY country_name, violation;",
    "Which country has the most stops with search conducted?":"SELECT country_name, COUNT(*) AS search_stops FROM trafficlogs WHERE search_conducted = TRUE GROUP BY country_name ORDER BY search_stops DESC;",
    "Yearly Breakdown of Stops and Arrests by Country":"SELECT country_name, YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS year, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, RANK() OVER (PARTITION BY country_name ORDER BY YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d'))) AS year_rank FROM trafficlogs GROUP BY country_name, year;",
    "Driver Violation Trends Based on Age and Race":"SELECT driver_age_raw, driver_race, violation, COUNT(*) AS total FROM ( SELECT driver_age_raw, driver_race, violation FROM trafficlogs WHERE driver_age_raw IS NOT NULL AND driver_race IS NOT NULL) AS sub GROUP BY driver_age_raw, driver_race, violation ORDER BY total DESC;",
    "Time Period Analysis of Stops (Year, Month, Hour)":"SELECT YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS year, MONTH(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS month, HOUR(STR_TO_DATE(stop_time, '%H:%i:%s')) AS hour, COUNT(*) AS stop_count FROM trafficlogs GROUP BY year, month, hour ORDER BY year, month, hour;",
    "Violations with High Search and Arrest Rates":"SELECT violation, COUNT(*) AS total, SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, RANK() OVER (ORDER BY SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) DESC) AS search_rank, RANK() OVER (ORDER BY SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) DESC) AS arrest_rank FROM trafficlogs GROUP BY violation;",
    "Driver Demographics by Country (Age, Gender, and Race)":"SELECT country_name, driver_age_raw, driver_gender, driver_race, COUNT(*) AS count FROM trafficlogs GROUP BY country_name, driver_age_raw, driver_gender, driver_race;",
    "Top 5 Violations with Highest Arrest Rates":"SELECT violation, COUNT(*) AS total, SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS arrest_rate FROM trafficlogs GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5;"
}


# Run the query and show results
if st.button("Run Query"):
    sql_query = query_map[selected_query]
    cursor.execute(sql_query)
    results = cursor.fetchall()
    df_result = pd.DataFrame(results, columns=cursor.column_names)
    st.dataframe(df_result, use_container_width=True)
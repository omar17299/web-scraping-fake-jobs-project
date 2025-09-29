import streamlit as st
import pandas as pd



df = pd.read_csv("jops.csv")

st.title("Omar Fake Jobs")
st.markdown("تطبيق تفاعلي لعرض الوظائف ومواصفاتها باستخدام Streamlit")


companies = df['company'].unique().tolist()
selected_company = st.selectbox("اختر الشركة:", ["All"] + companies)

if selected_company != "All":
    df = df[df['company'] == selected_company]


skills = ["python","javascript","django","flask","sql","aws","docker"]
selected_skills = st.multiselect("اختر المهارات:", skills)

for skill in selected_skills:
    df = df[df[f"skill_{skill}"] == True]


st.dataframe(df) 
st.download_button(
    label="Download CSV",
    data=df.to_csv(index=False),
    file_name="filtered_jobs.csv",
    mime="text/csv"
)

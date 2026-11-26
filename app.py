import streamlit as st

from loader import load_profiles, load_scholarships
from models import Scholarship, StudentProfile


# ===== Main Page =====
st.title(":material/school: Unclaimed")
st.write("Find hidden scholarships for high school, undergraduate, and graduate students. \
         \nThis demo includes configurable student profiles for testing.")

st.header("Matches")

st.header("Partial Matches")


# ===== Sidebar =====
# Load profiles in the sidebar
sidebar_header = st.sidebar.header(":material/person: Demo Profiles")

profiles = load_profiles()
profile_names = [p.name for p in profiles]

current_name = st.sidebar.selectbox("Select Profile", profile_names)
current_profile = next((d for d in profiles if d.name == current_name), None)

with st.sidebar.container(border=True):
    education_level = st.text_input("Education Level", value=current_profile.education_level.value)
    class_standing = st.text_input("Class Standing", value=(current_profile.class_standing.value) if current_profile.class_standing is not None else "")
    gpa = st.text_input("GPA", value=current_profile.gpa)
    institution = st.text_input("Institution", value=current_profile.institution)
    credits = st.text_input("Credits Per Term", value=current_profile.credits_per_term)
    fields_of_study = st.text_input("Fields of Study", value=", ".join(current_profile.fields_of_study))
    
    financial_need = st.checkbox("Has financial need?", current_profile.has_financial_need)
    fafsa = st.checkbox("Completed FAFSA?", current_profile.completed_fafsa)




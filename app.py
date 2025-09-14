import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Tutoring School Manager", layout="wide")
st.title("📚 Tutoring School Management")

if 'students' not in st.session_state:
    st.session_state.students = pd.DataFrame(columns=["Name", "Phone", "Next Payment Due", "Attendance", "Last Payment Amount"])

with st.sidebar:
    st.header("💾 Save / Load Data")
    if st.button("💾 Download Student List"):
        st.download_button("Download CSV", st.session_state.students.to_csv(index=False), "students.csv", "text/csv")
    uploaded_file = st.file_uploader("Upload Student CSV", type=["csv"])
    if uploaded_file is not None:
        st.session_state.students = pd.read_csv(uploaded_file)
        st.success("Student list loaded!")

with st.sidebar:
    st.header("➕ Add Student")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    payment_date = st.date_input("Next Payment Due")
    payment_amount = st.number_input("Last Payment Amount", min_value=0.0, step=1.0)
    if st.button("Add Student"):
        if name:
            new_student = pd.DataFrame([[name, phone, payment_date, False, payment_amount]],
                                       columns=["Name", "Phone", "Next Payment Due", "Attendance", "Last Payment Amount"])
            st.session_state.students = pd.concat([st.session_state.students, new_student], ignore_index=True)
            st.success(f"Added {name}!")
        else:
            st.error("Name is required!")

with st.sidebar:
    st.header("💰 Update Payment")
    if len(st.session_state.students) > 0:
        student_names = st.session_state.students["Name"].tolist()
        selected_student = st.selectbox("Select Student", student_names)
        new_payment_amount = st.number_input("Payment Amount", min_value=0.0, step=1.0, key='payment_input')
        new_payment_date = st.date_input("Next Payment Due", key='payment_date_input')
        if st.button("Update Payment"):
            idx = st.session_state.students.index[st.session_state.students["Name"] == selected_student][0]
            st.session_state.students.at[idx, "Last Payment Amount"] = new_payment_amount
            st.session_state.students.at[idx, "Next Payment Due"] = new_payment_date
            st.success(f"Updated payment for {selected_student}!")

today = datetime.today().date()
total_students = len(st.session_state.students)
overdue = len(st.session_state.students[pd.to_datetime(st.session_state.students["Next Payment Due"]).dt.date < today])
upcoming = len(st.session_state.students[(pd.to_datetime(st.session_state.students["Next Payment Due"]).dt.date >= today) & (pd.to_datetime(st.session_state.students["Next Payment Due"]).dt.date <= today + timedelta(days=3))])
total_collected = st.session_state.students['Last Payment Amount'].sum()

st.subheader("📊 Dashboard")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Students", total_students)
col2.metric("Overdue Payments", overdue)
col3.metric("Upcoming Payments", upcoming)
col4.metric("Total Collected", f"${total_collected}")

st.subheader("👩‍🎓 Students List")
if total_students == 0:
    st.info("No students yet. Add some from the sidebar.")
else:
    for i in range(len(st.session_state.students)):
        student = st.session_state.students.loc[i]
        next_due = pd.to_datetime(student["Next Payment Due"]).date()
        if next_due < today:
            bg_color = '#FFCCCC'
        elif next_due <= today + timedelta(days=3):
            bg_color = '#FFF2CC'
        else:
            bg_color = '#CCFFCC'
        col1, col2, col3, col4, col5 = st.columns([3,3,3,2,3])
        with col1:
            st.markdown(f"<div style='background-color:{bg_color}; padding:5px'>{student['Name']}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='background-color:{bg_color}; padding:5px'>{student['Phone']}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='background-color:{bg_color}; padding:5px'>{student['Next Payment Due']}</div>", unsafe_allow_html=True)
        with col4:
            new_attendance = st.checkbox("Present", value=student['Attendance'], key=f"att_{i}")
            st.session_state.students.at[i,'Attendance'] = new_attendance
        with col5:
            st.markdown(f"<div style='background-color:{bg_color}; padding:5px'>${student['Last Payment Amount']}</div>", unsafe_allow_html=True)

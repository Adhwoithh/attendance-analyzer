import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Attendance Intelligence System", layout="wide")

st.title("📊 Attendance Intelligence System")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
elif os.path.exists("attendance.csv"):
    df = pd.read_csv("attendance.csv")
elif os.path.exists("data/attendance.csv"):
    df = pd.read_csv("data/attendance.csv")
else:
    st.error("Dataset not found")
    st.stop()

df["attendance_percentage"] = (df["attended_classes"] / df["total_classes"]) * 100

threshold = st.sidebar.slider("Attendance Threshold (%)", 50, 100, 75)

df["classes_needed"] = (
    (threshold/100 * df["total_classes"]) - df["attended_classes"]
).apply(lambda x: int(x) if x > 0 else 0)

col1, col2, col3 = st.columns(3)

col1.metric("Total Students", len(df))
col2.metric("Average Attendance", f"{df['attendance_percentage'].mean():.2f}%")
col3.metric("At Risk", len(df[df["attendance_percentage"] < threshold]))

st.subheader("📋 Attendance Data")
st.dataframe(df, use_container_width=True)

st.subheader("📈 Attendance Visualization")

fig, ax = plt.subplots()
colors = ["red" if x < threshold else "green" for x in df["attendance_percentage"]]
ax.bar(df["name"], df["attendance_percentage"], color=colors)
ax.axhline(y=threshold, linestyle='--')
st.pyplot(fig)

st.subheader("⚠️ Students at Risk")

risk_df = df[df["attendance_percentage"] < threshold]
st.dataframe(risk_df, use_container_width=True)

st.subheader("🎯 Recommendation System")

selected_student = st.selectbox("Select Student", df["name"])
student = df[df["name"] == selected_student].iloc[0]

if student["attendance_percentage"] < threshold:
    needed = max(0, int(((threshold/100)*student["total_classes"]) - student["attended_classes"]))
    st.warning(f"You need to attend next {needed} classes continuously to reach {threshold}%")
else:
    st.success("You are already above the required attendance")

st.subheader("📚 Subject-wise Analysis")

subjects = {
    "Math": student["math"],
    "Physics": student["physics"],
    "CS": student["cs"]
}

fig2, ax2 = plt.subplots()
ax2.bar(subjects.keys(), subjects.values())
ax2.axhline(y=threshold, linestyle='--')
st.pyplot(fig2)

low_subjects = [sub for sub, val in subjects.items() if val < threshold]

if low_subjects:
    st.error(f"Focus on improving: {', '.join(low_subjects)}")
else:
    st.success("All subjects are above threshold")

st.subheader("🔮 Future Risk Simulation")

missed_classes = st.slider("Classes you might miss", 0, 20, 5)

future_attended = student["attended_classes"]
future_total = student["total_classes"] + missed_classes

future_percentage = (future_attended / future_total) * 100

st.write(f"Future Attendance: {future_percentage:.2f}%")

if future_percentage < threshold:
    st.error("⚠️ Attendance will fall below threshold")
else:
    st.success("✅ Safe attendance level")

st.subheader("🔍 Search")

name = st.text_input("Search student")

if name:
    st.dataframe(df[df["name"].str.contains(name, case=False)])

csv = risk_df.to_csv(index=False).encode("utf-8")

st.download_button("Download Risk Students", csv, "risk_students.csv")

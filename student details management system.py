import streamlit as st
import sqlite3
import pandas as pd


def get_connection():
    return sqlite3.connect("students.db")


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT UNIQUE NOT NULL,
            email TEXT,
            phone TEXT,
            course TEXT,
            year TEXT,
            attendance REAL,
            marks REAL
        )
    """)

    conn.commit()
    conn.close()


def add_student(name, roll_number, email, phone, course, year, attendance, marks):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO students
            (name, roll_number, email, phone, course, year, attendance, marks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            roll_number,
            email,
            phone,
            course,
            year,
            attendance,
            marks
        ))

        conn.commit()
        st.success("Student added successfully!")

    except sqlite3.IntegrityError:
        st.error("Roll number already exists!")

    finally:
        conn.close()



def get_students():
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    conn.close()

    return df



def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()




def update_student(student_id, name, email, phone, course, year, attendance, marks):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET name = ?,
            email = ?,
            phone = ?,
            course = ?,
            year = ?,
            attendance = ?,
            marks = ?
        WHERE id = ?
    """, (
        name,
        email,
        phone,
        course,
        year,
        attendance,
        marks,
        student_id
    ))

    conn.commit()
    conn.close()



create_table()

st.set_page_config(
    page_title="Student Details Management System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Details Management System")
st.write("Manage student information easily")


menu = st.sidebar.selectbox(
    "Select Operation",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Search Student",
        "Update Student",
        "Delete Student"
    ]
)



if menu == "Dashboard":

    st.header("📊 Dashboard")

    students = get_students()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Students",
            len(students)
        )

    with col2:
        if len(students) > 0:
            average_marks = students["marks"].mean()
            st.metric(
                "Average Marks",
                f"{average_marks:.2f}"
            )
        else:
            st.metric("Average Marks", "0")

    with col3:
        if len(students) > 0:
            average_attendance = students["attendance"].mean()
            st.metric(
                "Average Attendance",
                f"{average_attendance:.2f}%"
            )
        else:
            st.metric("Average Attendance", "0%")



elif menu == "Add Student":

    st.header("➕ Add Student")

    name = st.text_input("Student Name")
    roll_number = st.text_input("Roll Number")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    course = st.text_input("Course")

    year = st.selectbox(
        "Year",
        [
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year"
        ]
    )

    attendance = st.number_input(
        "Attendance (%)",
        min_value=0.0,
        max_value=100.0,
        value=75.0
    )

    marks = st.number_input(
        "Marks (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0
    )

    if st.button("Add Student"):

        if name == "" or roll_number == "":
            st.warning("Please enter Name and Roll Number.")

        else:
            add_student(
                name,
                roll_number,
                email,
                phone,
                course,
                year,
                attendance,
                marks
            )


# ---------------- VIEW STUDENTS ----------------

elif menu == "View Students":

    st.header("👨‍🎓 All Students")

    students = get_students()

    if students.empty:
        st.info("No student records found.")

    else:
        st.dataframe(
            students,
            use_container_width=True
        )


# ---------------- SEARCH STUDENT ----------------

elif menu == "Search Student":

    st.header("🔍 Search Student")

    search = st.text_input(
        "Enter student name or roll number"
    )

    if search:

        students = get_students()

        result = students[
            students["name"].str.contains(
                search,
                case=False,
                na=False
            )
            |
            students["roll_number"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

        if result.empty:
            st.warning("Student not found.")

        else:
            st.dataframe(
                result,
                use_container_width=True
            )


# ---------------- UPDATE STUDENT ----------------

elif menu == "Update Student":

    st.header("✏️ Update Student")

    students = get_students()

    if students.empty:
        st.info("No students available.")

    else:

        student_id = st.number_input(
            "Enter Student ID",
            min_value=1,
            step=1
        )

        student = students[
            students["id"] == student_id
        ]

        if not student.empty:

            data = student.iloc[0]

            name = st.text_input(
                "Name",
                value=data["name"]
            )

            email = st.text_input(
                "Email",
                value=data["email"] or ""
            )

            phone = st.text_input(
                "Phone",
                value=data["phone"] or ""
            )

            course = st.text_input(
                "Course",
                value=data["course"] or ""
            )

            year = st.text_input(
                "Year",
                value=data["year"] or ""
            )

            attendance = st.number_input(
                "Attendance (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(data["attendance"])
            )

            marks = st.number_input(
                "Marks (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(data["marks"])
            )

            if st.button("Update Student"):

                update_student(
                    student_id,
                    name,
                    email,
                    phone,
                    course,
                    year,
                    attendance,
                    marks
                )

                st.success(
                    "Student details updated successfully!"
                )

        else:
            st.info(
                "Enter a valid Student ID to update."
            )


# ---------------- DELETE STUDENT ----------------

elif menu == "Delete Student":

    st.header("🗑️ Delete Student")

    students = get_students()

    if students.empty:
        st.info("No students available.")

    else:

        student_id = st.number_input(
            "Enter Student ID to delete",
            min_value=1,
            step=1
        )

        if st.button("Delete Student"):

            if student_id in students["id"].values:

                delete_student(student_id)

                st.success(
                    "Student deleted successfully!"
                )

            else:

                st.error(
                    "Student ID not found."
                )
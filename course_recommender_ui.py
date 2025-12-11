import pandas as pd
import streamlit as st
import requests

FASTAPI_URL = "http://localhost:8000" #https://mist460-course-recommender-apis-lastname.azurewebsites.net" 

def fetch_data(endpoint : str, params : dict, method: str = "get") -> pd.DataFrame:
    if method == "get":
        response = requests.get(f"{FASTAPI_URL}/{endpoint}", params=params)
    elif method == "post":
        response = requests.post(f"{FASTAPI_URL}/{endpoint}", params=params)
    else:
        st.error(f"Unsupported HTTP method: {method}")
        return None

    if response.status_code == 200:
        payload = response.json()
        rows = payload.get("data", [])
        df = pd.DataFrame(rows)
        return df

    else:
        st.error(f"Error fetching data: {response.status_code}")
        return None
    
st.sidebar.markdown(
    """
    <style>
    .sidebar-card {
        padding: 15px 18px;
        background-color: #f8f9fa;
        border: 1px solid #dfe0e1;
        border-radius: 10px;
        margin-top: 10px;
    }
    .sidebar-card h2 {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("<div class='sidebar-card'><h2>Course Recommender</h2>", unsafe_allow_html=True)

    api_endpoint = st.sidebar.pills(
    "Select functionality:",
    [
        "Validate User",
        "Find Current Semester Course Offerings",
        "Find Prerequisites",
        "Get Recommendations for Job Description",
        "Check Prerequisite Completion",
        "Enroll Student",
        "Get Enrolled Courses",
        "Drop Course"
    ]
)
    st.markdown("</div>", unsafe_allow_html=True)

if api_endpoint == "Validate User":
    st.header("Validate User")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Validate"):
        df = fetch_data("validate_user/", {"username": username, "password": password})
        if df is not None:
            st.success("User validated successfully!")
            output_string = "App User ID: " + str(df["AppUserID"].values[0]) + ", Full Name: " + df["FullName"].iloc[0]
            st.write(output_string)
            st.session_state.app_user_id = df["AppUserID"].values[0]

        else:
            st.error("Invalid username or password.")

elif api_endpoint == "Find Current Semester Course Offerings":
    st.header("Find Current Semester Course Offerings")
    subject_code = st.text_input("Subject Code")
    course_number = st.text_input("Course Number")
    if st.button("Find Offerings"):
        df = fetch_data("find_current_semester_course_offerings/", {"subjectCode": subject_code, "courseNumber": course_number})
        if df is not None and not df.empty:
            st.dataframe(df, hide_index=True)
        else:
            st.info("No course offerings found for the specified course.")

elif api_endpoint == "Enroll Student":
    st.header("Enroll Student in Course Offering")
    student_id = st.number_input("Student ID", value=st.session_state.app_user_id, disabled=True)
    course_offering_id = st.number_input("Course Offering ID", min_value=1, step=1)
    if st.button("Enroll"):
        df = fetch_data(
            "enroll_student_in_course_offering/",
            {"studentID": student_id, "courseOfferingID": course_offering_id},
            method="get"
        )
        if df is not None and not df.empty:
            if df["EnrollmentSucceeded"].values[0] == True:
                st.success("Enrollment successful.")
            else:
                output_string = "Enrollment failed. " + df["EnrollmentResponse"].values[0]
                st.error(output_string)
        else:
            st.error("Could not complete enrollment request")

elif api_endpoint == "Get Enrolled Courses":
    st.header("Get Enrolled Courses for Student")
    student_id = st.number_input("Student ID", value=st.session_state.app_user_id, disabled=True)
    if st.button("Get Student's Enrollments"):
        df = fetch_data("get_student_enrolled_course_offerings/", {"studentID": student_id})
        if df is not None and not df.empty:
            st.dataframe(df, hide_index=True)
        else:
            st.info("No enrolled course offerings found for the specified student.")

elif api_endpoint == "Find Prerequisites":
    st.header("Find Prerequisites for a Course")
    subject_code = st.text_input("Subject Code")
    course_number = st.text_input("Course Number")
    if st.button("Find Prerequisites"):
        df = fetch_data("find_prerequisites/", {"subjectCode": subject_code, "courseNumber": course_number})
        if df is not None and not df.empty:
            st.dataframe(df, hide_index=True)
        else:
            st.info("No prerequisites found for the specified course.")

elif api_endpoint == "Check Prerequisite Completion":
    st.header("Has Student Taken All Prerequisites For a Course?")
    student_id = st.number_input("Student ID", value=st.session_state.app_user_id, disabled=True)
    subject_code = st.text_input("Subject Code")
    course_number = st.text_input("Course Number")
    if st.button("Check Prerequisites"):
        df = fetch_data(
            "check_if_student_has_taken_all_prerequisites_for_course/",
            {"studentID": student_id, "subjectCode": subject_code, "courseNumber": course_number}
        )
        if df is not None:
            if df.empty:
                st.success("The student has taken all prerequisites for the specified course.")
            else:
                st.warning("The student has NOT taken all prerequisites for the specified course. Missing prerequisites:")
                st.dataframe(df, hide_index=True)
        else:
            st.error("Error checking prerequisites.")

elif api_endpoint == "Drop Course":
    st.header("Drop Course")
    student_id = st.number_input("Student ID", value=st.session_state.app_user_id, disabled=True)
    course_offering_id = st.number_input("Course Offering ID", min_value=1, step=1)
    if st.button("Drop"):
        df = fetch_data(
            "drop_student_from_course_offering/",
            {"studentID": student_id, "courseOfferingID": course_offering_id},
            method="post"
        )
        if df["EnrollmentStatus"].values[0] == "Dropped":
             st.success("Drop successful.")
        else:
             output_string = "Drop failed. " + df["EnrollmentStatus"].values[0]
             st.error(output_string)

elif api_endpoint == "Get Recommendations for Job Description":
    #st.header("Course Recommendations for Job")
    # ---- Fetch data ----
    resp = requests.get(f"{FASTAPI_URL}/get_job_descriptions/")
    payload = resp.json()
    rows = payload.get("data", [])

    # ---- Build dropdown ----
    # Streamlit dropdown expects: st.selectbox(label, options, format_func)
    # We want the option object to hold both fields.
    selected = st.selectbox(
        "Select Job Description",
        options=rows,
        format_func=lambda r: r["JobDescription"]  # text shown to user
    )

    st.write("You selected:")
    st.write("Job:", selected["JobDescription"])
    job_description = st.text_area("Detailed Job Description", value=selected["DetailedJobDescription"], height=150)
    if st.button("Get Recommendations"):
        endpoint = "get_recommendations_for_job_description/"
        student_id = st.session_state.get('app_user_id')
        if not student_id:
            st.error("Please log in first")
            st.stop()
        params = {"jobDescription": job_description, "studentID": student_id}
        response = requests.get(
                    f"{FASTAPI_URL}/get_recommendations_for_job_description/",
                    params=params
                )
                
        if response.status_code == 200:
            result = response.json()
            
            st.success("✅ Recommendations retrieved!")
            
            # Display the AI-generated recommendations
            st.subheader("Recommended Courses")
            st.markdown(result, unsafe_allow_html=True)
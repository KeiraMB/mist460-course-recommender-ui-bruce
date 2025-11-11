import pandas as pd
import streamlit as st
import requests

FASTAPI_URL = "https://mist460-course-recommender-apis-bruce.azurewebsites.net/docs"

def fetch_data(endpoint: str, params: dict, method: str = "get"):
    if method == "get":
        response = requests.get(f"{FASTAPI_URL}/{endpoint}", params=params)
    elif method == "post":
        response = requests.post(f"{FASTAPI_URL}/{endpoint}", params==params)
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

#create a sidebar with a dropdown to select the api endpoint
st.sidebar.title("API Endpoint Selector")
api_endpoint = st.sidebar.selectbox( 
    "Select API Endpoint", [
        "validate_user",
        "find_current_semester_course_offerings",
        "find_prerequisites",
        "check_if_student_has_taken_all_prerequisites_for_course",
        "enroll_student_in_course",
        "get_student_enrolled_course_offerings",
        "drop_student_from_course_offering"
    ]
)

if api_endpoint == "validate_user":
    st.header("Validate User")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Validate"):
        df = fetch_data("validate_user/", {"username": username, "password": password}, method="post")
        if df is not None and not df.empty:
            st.success("User validated successfully!")
            output_string = "App User ID: " + str(df["AppUserID"].values[0]) + ", Full Name: " + df["FullName"].iloc[0] + "\n"
            st.write(output_string)
            st.session_state.app_user_id = df["AppUserID"].values[0]
        else:
            st.error("Invalid username or password.")

elif api_endpoint == "get_student_enrolled_course_offerings":
    st.header("Get Student Enrolled Course Offerings")
    student_id = st.number_input("Student ID", value=st.session_state.app_user_id, disabled=True)
    if st.button("Fetch Enrolled Courses"):
        df = fetch_data("get_student_enrolled_course_offerings/", {"student_id": student_id}, method="get")
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.info("No enrolled courses found for the student.")

elif api_endpoint == "enroll_student_in_course_offering":
    st.header("Enroll Student in Course Offering")
    student_id = st.number_input("Student ID", value=st.session_state.app_user_id, disabled=True)
    course_offering_id = st.text_input("Course Offering ID")
    if st.button("Enroll"):
        df = fetch_data("enroll_student_in_course_offering/", {"student_id": student_id, "course_offering_id": course_offering_id}, method="post")
        if df is not None:
            st.success("Enrollment processed.")
            #st.dataframe(df)
        else:
            st.error("Enrollment failed.")
            st.write(df["EnrollmentResponse"].values[0])


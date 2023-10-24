import streamlit as st 
import streamlit_authenticator as stauth 
import streamlit_survey as ss

import os
from supabase import create_client, Client

import datetime


# --- page background ---

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.unsplash.com/photo-1615469309489-0a464a9925cb?auto=format&fit=crop&q=80&w=2462&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
background-size: 100%;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}


</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


# --- submit functions ---

def determine_ltip_tool(responses):
    # Map the responses to the appropriate response code
    response_code = ''.join([responses.get(key, '')[0] for key in ['q1', 'q2', 'q3', 'q4'] if responses.get(key) is not None])

    # Define the conditions for each ltip tool
    ltip_tools_conditions = {
        'Restricted Share': ['AAAA', 'ABAA'],
        'Share Option': ['AAAB', 'ABAB', 'BAAB', 'BBAB'],
        'Phantom Share': ['AABA', 'ABBA', 'BABA', 'BBBA'],
        'Share Appreciation Right': ['AABB', 'ABBB', 'BABB', 'BBBB'],
        'Performance Share': ['BAAA', 'BBAA']
    }

    # Determine the appropriate ltip tool for the user
    for tool, conditions in ltip_tools_conditions.items():
        if response_code in conditions:
            return tool

    return None

def generate_responses(survey_data, user_id):
    timestamp = datetime.datetime.now().isoformat()

    # Create a dictionary with the timestamp and user id
    responses = {
        'timestamp': timestamp,
        'id': user_id,
    }

    # Flatten the nested dictionaries from the survey data
    for question, response in survey_data.items():
        if 'value' in response:
            responses[question] = response['value']

    return responses



def on_submit():
    responses = generate_responses(survey.data, st.session_state["name"])
    st.write(responses)

    # After the submit button is clicked
    if all(responses.values()):
            insert_data(supabase, responses)
            st.success('Your responses have been recorded!')

            # Map the responses to the appropriate response code
            
            ltip_tool = determine_ltip_tool(responses)

            if ltip_tool is not None:
                st.write(f'The suitable LTIP tool for you is: {ltip_tool}')
                # Determine the file name of the term sheet
                term_sheet_file = f"{ltip_tool.replace(' ', '_')}.docx"
                
                # Check if the file exists
                if os.path.exists(term_sheet_file):
                    with open(term_sheet_file, "rb") as file:
                        btn = st.download_button(
                            label=f"Download {ltip_tool} Term Sheet",
                            data=file,
                            file_name=term_sheet_file,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                else:
                    st.error(f"Term sheet for {ltip_tool} not found.")
            else:
                st.write('The suitable LTIP tool for you could not be determined based on your responses.')




# --- database setup ---
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

def insert_data(supabase: Client, data: dict):
    insert_res = supabase.table("survey").insert(data).execute()
    print(insert_res)  
    if 'error' in insert_res:
        print(insert_res['error'])



# --- login page setup ---
# using secrets management

authenticator = stauth.Authenticate(
    dict(st.secrets['credentials']),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)


authenticator.login('Login', 'main')

if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

if st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')



# --- Main Page ---
if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main', key='unique_key')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.header('Long-Term Incentive Design Tool')
    st.caption('Please complete the following questions')
    st.divider()

    # Define question flows:
    survey = ss.StreamlitSurvey("Survey")
    pages = survey.pages(3, on_submit=on_submit)

    with pages:
        if pages.current == 0:
            st.write("What is the key purpose of your company's equity plan?")
            Q1 = survey.radio(
                label= "q1",
                options=["A. Retention-Focused", "B. Performance-Focused"],
                index = 0,
                horizontal=True,
                label_visibility = "collapsed"
                )
            

        elif pages.current == 1:
            st.write("Who do you want to reward?")
            Q2 = survey.radio(
                label= "q2",
                options=["A. Retention-Focused", "B. Performance-Focused"],
                index = 0,
                horizontal=True,
                label_visibility = "collapsed"
                )
            
            

        elif pages.current == 2:
            st.write("Is your company publicly listed?")
            Q3 = survey.radio(
                label= "q3",
                options=["A. Yes", "B. No"],
                index = 0,
                horizontal=True,
                label_visibility = "collapsed"
                )
            
            if Q3 == "B. No":
                st.write("Do you plan to go IPO? Can you elaborate more?")
                survey.text_area(
                    label="q3_1",
                    max_chars = 200,
                    label_visibility = "collapsed"
                )


            st.write("How does your company want to reward?")
            Q3 = survey.radio(
                label= "q4",
                options=["A. Yes", "B. No"],
                index = 0,
                horizontal=True,
                label_visibility = "collapsed"
                )

            

        
    

import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd

#from data_import import FILE_USER

def authenticate(df_users):

	st.session_state['authentication_status'] = None
	#1. retrieve user credentials
	credentials = {'usernames':{}}

	names = df_users['name'].tolist()
	passwords = df_users['password'].tolist()

	#2. create a hash for each passwords so that we do not send these in the clear
	hashed_passwords = stauth.Hasher(passwords).generate()

	for name, pw in zip(names, hashed_passwords):
		user_dict = {"name":name, 'password':pw}
		credentials['usernames'].update({name:user_dict})

	#3. create the authenticator which will create an authentication session cookie with an expiry interval
	authenticator = stauth.Authenticate(credentials, 'streamlit-auth-0','streamlit-auth-0-key',cookie_expiry_days=1)

	#4. display the login form in the sidebar 
	name, authentication_status, username = authenticator.login('Login','sidebar')

	#5. the streamlit_authenticator library keeps state of the authentication status in streamlit's st.session_state['authentication_status']

	# > if the authentication succeeded (i.e. st.session_state['authentication_status'] == True)
	if st.session_state['authentication_status']:
		# display name on the sidebar
		with st.sidebar:
			st.text(name)

		authenticator.logout('Logout', 'sidebar')			

		# set user id in session state
		user_id = int(df_users[df_users['name'] == name]['id'].iloc[0])
		st.session_state['user'] = user_id
		
	# > if the authentication failed
	elif st.session_state['authentication_status'] == False:
		# write an error message on the sidebar
		with st.sidebar:
			st.error('Username/password is incorrect')

	# > if there are no authentication attempts yet (e.g., first time visitors)
	elif st.session_state['authentication_status'] == None:
		# write an warning message on the sidebar
		with st.sidebar:			
			st.warning('Please enter your username and password in the sidebar')
   
   

# # Define a function that modifies the session state when the user logs out
# def on_logout():
#     # Set the session state to the default value when the user logs out
#     st.session_state.user = 0
   
#    # Register the on_logout function to be called when the user logs out
# st.session_state['_on_logout'] = on_logout

#    # Check if the user is logged in
# if st.session_state.get('user', 0) > 0:
#     st.write("You are logged in.")
# else:
#     # If the user is not logged in, call the on_logout function
#     st.session_state['_on_logout']()
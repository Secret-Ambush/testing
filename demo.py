import streamlit as st

# Add elements to the sidebar
st.sidebar.title('Sidebar Title')
st.sidebar.subheader('Sidebar Subheader')
st.sidebar.text('Sidebar Text')

# Add input controls to the sidebar
selected_option = st.sidebar.selectbox('Select an Option', ['Option 1', 'Option 2', 'Option 3'])

# Display content in the main area
st.title('Main Content')
st.write('Selected Option:', selected_option)

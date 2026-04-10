import streamlit as st

# Add robot image uploader
st.sidebar.title("⚙️ Background Settings")
uploaded_file = st.sidebar.file_uploader("Upload Robot Image (optional)", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Save the uploaded file
    import os
    os.makedirs('static/images', exist_ok=True)
    with open('static/images/robot.png', 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("✅ Robot image uploaded!")

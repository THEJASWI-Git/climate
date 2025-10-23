import streamlit as st
import matplotlib.pyplot as plt
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="EcoVision 🌿", page_icon="🌍", layout="wide")

# Sidebar navigation
st.sidebar.title("🌿 EcoVision Dashboard")
page = st.sidebar.radio("Go to:", ["Home", "Air Conservation", "Water Conservation", "Soil Conservation", "AI Chatbot"])

# ========== HOME ==========
if page == "Home":
    st.title("🌎 EcoVision - Environmental Conservation App")
    st.write("""
    Welcome to **EcoVision**, your environmental companion.  
    Explore real-time insights on Air, Water, and Soil conservation efforts across major cities.
    """)

    st.image("https://upload.wikimedia.org/wikipedia/commons/7/7a/Environmental_Protection.jpg", use_column_width=True)

    st.subheader("💡 About the Project")
    st.write("""
    **EcoVision** is a sustainability-focused web app designed to:
    - Visualize environmental data (Air, Water, and Soil)
    - Spread awareness about conservation
    - Provide AI-powered environmental assistance through an integrated chatbot
    """)

    # Team Information Section
    st.markdown("---")
    st.header("👨‍💻 Our Team")
    st.subheader("Team Name: **Winfinity** 🌱")

    team_cols = st.columns(2)
    with team_cols[0]:
        st.write("""
        **Members:**
        - Thejaswi V R  
        - Chiranth K L 
        - Madhusudan  
        - Likhtih  
        """)

    with team_cols[1]:
        st.write("""
        **About Us:**  
        We are a passionate team of innovators participating in the **Hackathon 2025**.  
        Our mission is to leverage **AI and Data Science** to make environmental conservation more accessible, insightful, and actionable.
        """)

    st.markdown("---")
    st.success("✅ Explore the other tabs to see visual insights and chat with our AI EcoBot!")

# ========== AIR CONSERVATION ==========
elif page == "Air Conservation":
    st.title("💨 Air Pollution and Conservation")
    st.write("Air quality monitoring across major cities.")
    cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"]
    aqi = [180, 110, 90, 95, 130]

    fig, ax = plt.subplots()
    ax.bar(cities, aqi, color='lightgreen')
    ax.set_title("Air Quality Index (lower is better)")
    ax.set_ylabel("AQI Level")
    st.pyplot(fig)
    st.info("✅ Use public transport, plant trees, and reduce industrial emissions to improve air quality.")

# ========== WATER CONSERVATION ==========
elif page == "Water Conservation":
    st.title("💧 Water Pollution and Conservation")
    st.write("Water purity levels in major cities.")
    cities = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata"]
    purity = [60, 70, 85, 80, 65]

    fig, ax = plt.subplots()
    ax.bar(cities, purity, color='skyblue')
    ax.set_title("Water Purity Levels (%)")
    ax.set_ylabel("Purity %")
    st.pyplot(fig)
    st.info("✅ Promote rainwater harvesting and avoid dumping waste into water bodies.")

# ========== SOIL CONSERVATION ==========
elif page == "Soil Conservation":
    st.title("🌱 Soil Health and Conservation")
    st.write("Soil quality index in major agricultural zones.")
    zones = ["Punjab", "Maharashtra", "Karnataka", "Tamil Nadu", "Bihar"]
    soil_index = [82, 68, 75, 70, 65]

    fig, ax = plt.subplots()
    ax.plot(zones, soil_index, marker='o', color='brown')
    ax.set_title("Soil Quality Index (higher is better)")
    ax.set_ylabel("Soil Index")
    st.pyplot(fig)
    st.info("✅ Prevent soil erosion, reduce chemical fertilizers, and practice crop rotation.")

# ========== AI CHATBOT ==========
elif page == "AI Chatbot":
    st.title("🤖 EcoBot - Environmental Chat Assistant")
    st.write("Ask any question about air, water, or soil conservation!")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about environmental conservation...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert environmental assistant giving advice on air, water, and soil conservation."},
                    {"role": "user", "content": user_input}
                ]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "⚠️ Error connecting to OpenAI API. Check your API key or internet connection."

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

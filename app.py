import streamlit as st
import openai

# Set OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit app configuration
st.set_page_config(page_title="Chat-Based Travel Planner", layout="centered")

# Initializing session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "You are an AI travel assistant. Your job is to collect details step by step from the user to create a detailed, personalized travel itinerary. "
                "Ask one question at a time and gather the following details:\n\n"
                "1. Destination\n"
                "2. Travel dates\n"
                "3. Budget (low, moderate, or high)\n"
                "4. Number of people traveling\n"
                "5. Trip duration (number of days, if not implied by travel dates)\n"
                "6. Specific interests (e.g., culture, adventure, food, relaxation, nightlife, nature, shopping)\n"
                "7. Dietary preferences or restrictions (e.g., vegetarian, gluten-free, halal)\n"
                "8. Mobility concerns or walking tolerance\n"
                "9. Accommodation preferences (e.g., luxury, budget-friendly, centrally located)\n\n"
                "If any information is missing, ask only one follow-up question at a time. Use polite and conversational language. "
                "Once all details are collected, confirm the inputs with the user before generating the itinerary. "
                "Ensure the final itinerary includes:\n"
                "1. Hotel recommendations (name, location, notable features).\n"
                "2. Suggestions for local restaurants and meals, highlighting dietary preferences.\n"
                "3. A list of daily attractions and activities, grouped by location for convenience.\n"
                "4. Transportation options between cities or attractions.\n"
                "5. Shopping opportunities and cultural experiences.\n"
                "6. Activities suitable for kids or mobility limitations, if applicable."
            )
        }
    ]

# Title and description
st.title("AI Travel Planner 🗺️")
st.write("Chat with the AI to plan your perfect trip! The assistant will ask questions step by step to ensure all details are collected.")

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        st.markdown(f"**AI Assistant:** {message['content']}")

# User input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message:", placeholder="Type your reply here...")
    submit = st.form_submit_button("Send")

# Handle user input
if submit and user_input:
    # Add user input to the conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Check for missing details in the conversation
    try:
        # Build a prompt to analyze missing information
        analysis_prompt = (
            "You are assisting with planning a personalized travel itinerary. Based on the following conversation, "
            "identify which details are still missing for the itinerary: destination, travel dates, budget, number of people traveling, "
            "trip duration, specific interests, dietary preferences, mobility concerns, or accommodation preferences. "
            "Ask only one follow-up question to collect the next missing detail.\n\n"
        )
        for message in st.session_state.messages:
            analysis_prompt += f"{message['role'].capitalize()}: {message['content']}\n"
        
        # Call OpenAI to analyze and ask the next question
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant tasked with identifying missing travel details."},
                {"role": "user", "content": analysis_prompt}
            ]
        )
        assistant_message = response["choices"][0]["message"]["content"]
        
        # Add the assistant's response to the conversation history
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    except Exception as e:
        st.error(f"Error: {e}")

# Generate final itinerary
if st.button("Generate Final Itinerary"):
    try:
        # Construct a final prompt based on the conversation
        final_prompt = (
            "Using the following conversation, generate a detailed day-by-day travel itinerary. The itinerary must include:\n"
            "1. Specific hotel recommendations (name, location, notable features).\n"
            "2. Suggested restaurants for meals, highlighting dietary preferences.\n"
            "3. A list of daily attractions and activities, grouped logically by location for convenience.\n"
            "4. Transportation options between cities or attractions.\n"
            "5. Shopping opportunities for souvenirs or local crafts.\n"
            "6. Cultural experiences or leisure activities (e.g., local shows, guided tours).\n"
            "7. Activities suitable for kids or accommodating mobility limitations, if applicable.\n\n"
        )
        for message in st.session_state.messages:
            final_prompt += f"{message['role'].capitalize()}: {message['content']}\n"
        
        # Call OpenAI to generate the itinerary
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": final_prompt}]
        )
        
        # Extract the final itinerary
        final_itinerary = response["choices"][0]["message"]["content"]
        
        st.markdown("### Your Travel Itinerary:")
        st.markdown(final_itinerary)
        
        # Save the itinerary for session state
        st.session_state.final_itinerary = final_itinerary
    except Exception as e:
        st.error(f"Error generating itinerary: {e}")

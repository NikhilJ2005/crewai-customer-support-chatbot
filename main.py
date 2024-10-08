import streamlit as st
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
# Load environment variables
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(
    temperature=0.7, 
    model_name="groq/llama-3.1-70b-versatile", 
    api_key=GROQ_API_KEY,
    provider="Meta"
)

def create_agent(role, goal, backstory):
    return Agent(
        llm=llm,
        role=role,
        goal=goal,
        backstory=backstory,
        allow_delegation=False,
        verbose=True,
    )

# Updated agent for customer support
support_agent = create_agent(
    role="Customer Support Agent",
    goal=(
        "Provide helpful responses to customer queries: {input}. "
        "Assist with managing bookings, and provide accurate product information as requested. "
        "Ensure responses are concise, informative, and professional, directly addressing the customer's needs."
    ),
    backstory=(
        "You are a customer support agent for a small business. "
        "Your goal is to assist customers with their inquiries, including handling common questions, managing bookings, and providing detailed information about products or services. "
        "You strive to provide excellent customer service to improve customer satisfaction and operational efficiency."
    ),
)

def create_task(description, expected_output, agent):
    return Task(description=description, expected_output=expected_output, agent=agent)

# Updated task description for customer support
support_task = create_task(
    description=(
        "Engage with the customer based on their query: {input}. "
        "Provide accurate and helpful information, assist with booking requests, and answer any product-related questions. "
        "Ensure the response is clear, professional, and directly addresses the customer's needs."
    ),
    expected_output=(
        "A response that directly addresses the customer's query, provides accurate information, assists with bookings if needed, and enhances the overall customer experience."
    ),
    agent=support_agent,
)

crew = Crew(agents=[support_agent], tasks=[support_task], verbose=True)

# Initialize session state for chat histories per page
if 'chat_histories' not in st.session_state:
    st.session_state['chat_histories'] = {}

# Initialize session state for current chats per page
if 'current_chats' not in st.session_state:
    st.session_state['current_chats'] = {}

def main():
    st.set_page_config(page_title="Customer Support Chatbot", layout="wide")
    st.title("🛍️ AI-Powered Customer Support Chatbot")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    pages = ["Home", "Product Categories", "Booking", "Support FAQs", "Product Features", "Chat History"]
    selected_page = st.sidebar.radio("Go to", pages)

    # Initialize chat history and current chat for the selected page
    if selected_page not in st.session_state['chat_histories']:
        st.session_state['chat_histories'][selected_page] = []
    if selected_page not in st.session_state['current_chats']:
        st.session_state['current_chats'][selected_page] = []

    if selected_page == "Home":
        st.header("Welcome to our Customer Support")
        st.write("How can we assist you today?")
        
        # Quick query options
        st.subheader("Common Queries")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Product Information"):
                topic = "Tell me about your products."
                process_query(topic, selected_page)
        with col2:
            if st.button("Make a Booking"):
                topic = "I want to make a booking."
                process_query(topic, selected_page)
        with col3:
            if st.button("Support Request"):
                topic = "I need help with a product."
                process_query(topic, selected_page)

        # Add a button to redirect to Product Features page
        st.subheader("Explore Our Products")
        if st.button("View Product Features"):
            # Redirect to Product Features page
            st.session_state['page'] = "Product Features"
            st.experimental_rerun()
        
        # Display the chat interface
        display_chat_interface(selected_page)

    elif selected_page == "Product Categories":
        st.header("Product Categories")
        st.write("Browse our product categories:")
        categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports"]
        for category in categories:
            if st.button(category):
                topic = f"Tell me more about {category.lower()} products."
                process_query(topic, selected_page)
        # Add a button to redirect to Product Features page
        st.subheader("Learn More About Our Products")
        if st.button("View Product Features"):
            # Redirect to Product Features page
            st.session_state['page'] = "Product Features"
            st.experimental_rerun()
        # Display the chat interface
        display_chat_interface(selected_page)

    elif selected_page == "Booking":
        st.header("Booking Services")
        st.write("Manage your bookings:")
        booking_options = ["Make a Booking", "Reschedule Booking", "Cancel Booking"]
        for option in booking_options:
            if st.button(option):
                topic = option
                process_query(topic, selected_page)
        # Display the chat interface
        display_chat_interface(selected_page)

    elif selected_page == "Support FAQs":
        st.header("Frequently Asked Questions")
        faqs = {
            "What is your return policy?": "Our return policy lasts 30 days...",
            "How can I track my order?": "You can track your order by...",
            "Do you offer international shipping?": "Yes, we ship to over 50 countries..."
        }
        for question, answer in faqs.items():
            with st.expander(question):
                st.write(answer)
        st.write("Didn't find what you're looking for? Ask us directly.")
        # Display the chat interface
        display_chat_interface(selected_page)
    
    elif selected_page == "Product Features":
        st.header("Product Features")
        st.write("Discover our range of products and their exclusive features.")
        
        # Provide an overview of products, models, and exclusive features
        product_info = {
            "Electronics": {
                "Smartphone X1": "Features a 6.5-inch display, triple camera system, and 5G connectivity.",
                "Laptop Pro 15": "Comes with a powerful processor, 16GB RAM, and 1TB SSD storage."
            },
            "Clothing": {
                "Eco-Friendly T-Shirt": "Made from 100% organic cotton, available in various colors.",
                "Stylish Denim Jeans": "Comfortable fit with a modern look, suitable for all occasions."
            },
            "Home & Kitchen": {
                "Blender Max": "High-speed blender with multiple settings and durable blades.",
                "Air Purifier Plus": "Removes 99% of airborne particles, ensuring clean indoor air."
            }
            # Add more categories and products as needed
        }

        for category, products in product_info.items():
            st.subheader(category)
            for product_name, description in products.items():
                st.markdown(f"**{product_name}**: {description}")

        st.write("Interested in a product? Feel free to ask us for more details.")
        # Display the chat interface
        display_chat_interface(selected_page)

    elif selected_page == "Chat History":
        st.header("Chat History")

        # Option to clear all chat histories
        if st.button("Clear All Chat Histories"):
            st.session_state['chat_histories'] = {}
            st.success("All chat histories cleared.")

        # Display chat histories per page
        for page, histories in st.session_state['chat_histories'].items():
            if histories:
                st.subheader(f"Chat Histories for {page}")
                for i, chat_session in enumerate(histories):
                    with st.expander(f"Session {i+1}"):
                        for entry in chat_session:
                            with st.chat_message("user"):
                                st.markdown(entry['topic'])
                            with st.chat_message("assistant"):
                                st.markdown(entry['response'])
            else:
                st.write(f"No chat history for {page}.")

def process_query(user_input, page_name):
    if user_input:
        with st.spinner("Connecting to customer support agent..."):
            result = crew.kickoff(inputs={"input": user_input})
        try:
            support_output = result.tasks_output[0].raw

            # Display the outputs in a readable format
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                st.markdown(support_output)

            # Store the query and response in the current chat session for the page
            chat_summary = {
                "topic": user_input,
                "response": support_output,
            }
            st.session_state['current_chats'][page_name].append(chat_summary)

        except Exception as e:
            st.error(f"An error occurred while processing your request: {e}")

def display_chat_interface(page_name):
    # Display current chat
    st.subheader("Chat with Us")

    # Display previous messages for the current page
    for entry in st.session_state['current_chats'][page_name]:
        with st.chat_message("user"):
            st.markdown(entry['topic'])
        with st.chat_message("assistant"):
            st.markdown(entry['response'])

    # Input for user's query
    user_input = st.chat_input("Enter your query or request")
    if user_input:
        process_query(user_input, page_name)

    if st.button("End Chat"):
        if st.session_state['current_chats'][page_name]:
            st.session_state['chat_histories'][page_name].append(list(st.session_state['current_chats'][page_name]))
            st.session_state['current_chats'][page_name] = []
            st.success("Chat ended and saved to history.")

if __name__ == "__main__":
    # Check if a page redirect is requested
    if 'page' in st.session_state:
        st.experimental_set_query_params(page=st.session_state['page'])
        selected_page = st.session_state['page']
        del st.session_state['page']
    else:
        selected_page = None
    main()

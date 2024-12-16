import streamlit as st
import openai
from road_trip_function import road_trip_function
from one_way_trip_with_flights import one_way_trip_with_flights
from road_trip_round_trip_function import road_trip_round_trip_function
import IPython

# API Keys (Replace with your actual key)
openai.api_key = st.secrets["openai_api_key"]  # Replace with your actual API key
API_KEY = st.secrets["google_api_key"]     # Google Distance Matrix API key

# Streamlit App
st.title("Travel Planner App! 🌍✈️🚗")

# Add the message on how to use the
st.markdown(
    """
    <div style="border: 2px solid #d3d3d3; padding: 15px; border-radius: 10px; background-color: #f8f8f8; color: #000;">
        <h4 style="text-align: center;">How to use:</h4>
        <p style="text-align: left; font-size: 16px;">
            Plan your perfect trip effortlessly! Whether you’re road-tripping or flying, our app helps you:
        </p>
        <ul style="padding-left: 20px; font-size: 16px;">
            <li>Create Itineraries: Enter cities you want to visit, and we’ll calculate the best routes.</li>
            <li>Find Flights: Get top flight options for one-way or round trips.</li>
            <li>Explore Activities: Discover events, foods, and attractions in each destination.</li>
            <li>Visualize Your Journey: View interactive maps of your routes.</li>
        </ul>
        <p style="text-align: left; font-size: 16px; margin-top: 20px;">
            Simply input your travel details (cities, dates, and preferences), and let us do the planning. Start your adventure today! 🚀
        </p>
        <h4 style="text-align: center; margin-top: 30px;">⚠️ Attention!</h4>
        <p style="text-align: left; font-size: 16px; margin-top: 10px;">
            If you need the app to search for your flights, make sure to input your dates and maximum and minimum days of your trip properly.
        </p>
        <p style="text-align: left; font-size: 16px; margin-top: 10px;">
            For example, if you input your dates between <b>2025-01-01</b> and <b>2025-01-15</b>, with days of your trip between <b>1</b> and <b>14</b>, it will look for all the combinations.
        </p>
        <p style="text-align: left; font-size: 16px; margin-top: 10px;">
            Keep in mind that each flight search takes approximately  <b>25 seconds per flight scraped</b>. Therefore, our example would take over <b>1 hour</b> to fetch the flights, and the results won't be usable.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)




# User Inputs
residency = st.text_input("Where do you live?", placeholder="Enter your home city").strip()

cities_to_visit = st.text_area(
    "Enter the cities you want to visit, separated by commas:",
    placeholder="e.g., Paris, Berlin, Rome"
).strip()
cities_to_visit = list(map(str.strip, cities_to_visit.split(',')))

road_trip = st.radio("Are you doing a land trip (no flights) from where you live?", ["Yes", "No"]).lower()

trip_mode = st.selectbox(
    "How are you going to move around?",
    options=["Driving", "Walking", "Bicycling", "Public Transit"]
).lower()

transit_mode = None
if trip_mode == "public transit":
    transit_mode = st.radio("Which type of public transit do you want to take?", ["Bus", "Rail (Train/Tram/Subway)"]).lower()


# Create two columns for the departure date inputs
col1, col2 = st.columns(2)
with col1:
    earliest_departure_date = st.date_input("Earliest Departure Date")
    earliest_return_date = st.date_input("Earliest Return Date")
    minimum_days = st.number_input("Minimum Number of Days Traveling", min_value=1, value=1)
with col2:
    latest_departure_date = st.date_input("Latest Departure Date")
    latest_return_date = st.date_input("Latest Return Date")
    maximum_days = st.number_input("Maximum Number of Days Traveling", min_value=1, value=14)


# Function to display the HTML map later
def map_function(map_route):
    if isinstance(map_route, str):
        st.components.v1.html(map_route, height=600)
    elif isinstance(map_route, IPython.core.display.HTML):
        # Extract the HTML from the IPython HTML object
        map_route_html = map_route.data  # Extract raw HTML content
        st.components.v1.html(map_route_html, height=600)
    else:
        st.error("map_route is not in a valid format for display.")

# Function to query ChatGPT for seasonal events and food recommendations with a sassy comment
def get_chatgpt_comments(cities, earliest_departure_date, latest_departure_date):
    # Format the list of cities and travel dates
    cities_str = ", ".join(cities)
    
    # Create a custom prompt to get a sassy first response followed by the event and food suggestions
    prompt = f"""
    Respond to the user with a sassy comment about their trip first, then provide helpful information. Make fun of the user if you deem it funny.
    If no cities are provided, do not answer anything else. 
    The trip is to the following cities: {cities_str}. 
    The trip will take place from {earliest_departure_date} to {latest_departure_date}. 
    After your sassy comment, please provide any seasonal events or festivals that might occur during this time in those cities.
    Also, what are some must-try foods in these cities during this time of the year?
    Also, what things can the user do or visit in these cities?
    Provide the information in a structured manned, separating the information by cities
    """
    
    # Send the prompt to OpenAI's GPT model using gpt-3.5-turbo (or gpt-4)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Using gpt-3.5-turbo or gpt-4
        messages=[{"role": "system", "content": "You are a witty and sassy assistant."},
                  {"role": "user", "content": prompt}]
    )
    
    # Extract the response text
    return response['choices'][0]['message']['content'].strip()


# Main Logic for Land Trip or Flights Planning
if road_trip in ["yes", "y"]:
    origin = (residency,)
    final_destination = (residency,)
    chatgpt_comments = get_chatgpt_comments(cities_to_visit, earliest_departure_date, latest_departure_date)
    st.markdown("## Jessica, The Travel Sassystant:")
    st.write(chatgpt_comments)

    if st.button("Plan Land Trip"):
        with st.spinner("Calculating road trip routes..."):
            potential_routes, shortest_route, best_itinerary, map_route = road_trip_function(
                cities_to_visit, road_trip, origin, final_destination, trip_mode, transit_mode, API_KEY
            )
        st.success("Land trip planned!")
        st.write("Potential Routes Calculated:", potential_routes.shape[0])
        st.write("Shortest Route:", shortest_route)
        st.write("Best Itinerary:", best_itinerary)

        map_function(map_route)

elif road_trip in ["no", "n"]:
    round_trip = st.radio("In destination, do you want to do a round trip or one-way?", ["Round Trip", "One Way"]).lower()

    # Get comments from ChatGPT about seasonal events and food
    if cities_to_visit and earliest_departure_date and latest_departure_date:
        chatgpt_comments = get_chatgpt_comments(cities_to_visit, earliest_departure_date, latest_departure_date)
        st.markdown("## Jennifer, The Travel Sassystant:")
        st.write(chatgpt_comments)

    if round_trip in ["one way", "one"]:
        if st.button("Plan One-Way Trip"):
            with st.spinner("Finding flights and routes..."):
                origin = None
                final_destination = None
                potential_routes, shortest_route, best_itinerary, map_route = road_trip_function(
                    cities_to_visit, road_trip, origin, final_destination, trip_mode, transit_mode, API_KEY
                )
                destination_city_arrival = best_itinerary[0]
                destination_city_departure = best_itinerary[-1]
                best_flight_dates = one_way_trip_with_flights(
                    residency, destination_city_arrival, destination_city_departure,
                    earliest_departure_date, latest_departure_date,
                    earliest_return_date, latest_return_date, minimum_days, maximum_days
                )
            st.success("One-way trip planned!")
            st.write("Top 5 Best Flight Dates:", best_flight_dates)
            st.write("Potential Land Routes Calculated:", len(potential_routes))
            st.write("Shortest Route:", shortest_route)
            st.write("Best Itinerary:", best_itinerary)
            map_function(map_route)

    elif round_trip in ["round trip", "round"]:
        if st.button("Plan Round Trip"):
            with st.spinner("Calculating round trip options..."):
                flight_prices, travel_times_df, shortest_route, top_5_cheapest_flights_info_df, best_itinerary, map_route = road_trip_round_trip_function(
                    residency, cities_to_visit, trip_mode, transit_mode, road_trip, API_KEY,
                    earliest_departure_date, latest_departure_date,
                    earliest_return_date, latest_return_date, minimum_days, maximum_days
                )
            total_flights_checked = len(flight_prices)*(flight_prices.shape[1]-2)
            st.success("Round trip planned!")
            st.write("Total Flights Scraped:", total_flights_checked)
            st.write("Top 5 Cheapest Flights:", top_5_cheapest_flights_info_df)
            st.write("Shortest Route:", travel_times_df)
            map_function(map_route)

# Add "Buy Me a Coffee" Button
st.markdown("---")

# Add the message to the app
st.markdown(
    """
    <div style="border: 2px solid #FFDD00; padding: 15px; border-radius: 10px; background-color: #FFF9C4; color: #000;">
        <p style="text-align: center; font-size: 16px;">
            Unfortunately, this service is not free. It requires OpenAI and Google APIs to run.
        </p>
        <p style="text-align: center; font-size: 16px;">
            If you enjoyed it, please consider 
            <a href="https://buymeacoffee.com/xaviersamper" target="_blank" style="text-decoration: none; color: #FF6600; font-weight: bold;">
                buying me a coffee ☕
            </a>. 
            Thank you, and have a safe trip!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Add LinkedIn Icon
col1, col2 = st.columns([1, 1])  # Adjust column width as necessary
with col1:
    st.components.v1.html("""
    <script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" 
        data-name="bmc-button" data-slug="xaviersamper" 
        data-color="#FFDD00" data-emoji="" 
        data-font="Cookie" data-text="Buy me a coffee" 
        data-outline-color="#000000" 
        data-font-color="#000000" 
        data-coffee-color="#ffffff">
    </script>
    """, height=70)

with col2:
    st.components.v1.html("""
    <div style="text-align: center; margin-top: 20px;">
        <a href="https://www.linkedin.com/in/xaviersamper/" target="_blank" 
        style="text-decoration: none; font-family: Arial, sans-serif; padding: 10px 20px; 
                background-color: #0077b5; color: white; font-size: 16px; border-radius: 5px; 
                display: inline-block">
            Connect on LinkedIn
        </a>
    </div>
    """)


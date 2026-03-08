import streamlit as st
import pandas as pd
from tools import get_city_distance
import io

# ------------------------------
# 1️⃣ Page Config
# ------------------------------
st.set_page_config(
    page_title="Route Distance & Cost Estimator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------
# 2️⃣ Custom CSS
# ------------------------------
st.markdown("""
<style>
body { background-color: #0E1117; font-family: 'Helvetica', sans-serif; }
h1 {
    color: #FFD700 !important;
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
}
h2 { color: #FAFAFA; margin-bottom: 10px; }
div.stAlert > div[data-baseweb="alert"] > div { background-color: #262730; color: #FFD700; font-weight: bold; }
.stButton>button { background-color: #FFD700; color: #0E1117; border-radius:12px; padding:10px 24px; font-size:16px; font-weight:bold; }
.stDownloadButton>button { background-color: #1E90FF; color:#FAFAFA; border-radius:12px; padding:10px 24px; font-size:16px; font-weight:bold; }
.stSelectbox, .stTextInput, .stRadio, .stFileUploader > div > div > input { border-radius:12px; background-color:#262730; color:#FAFAFA; }
.dataframe tbody tr:hover { background-color: #1a1c23; }
.invalid { color: red; font-weight: bold; }
.valid { color: #32CD32; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 3️⃣ Main Heading
# ------------------------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: center; gap: 30px;">
    <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzF6b3Vnb2U3Ymh4aGNycGJjYnJhbHpieG16aHp1MWhjcGQ5ZjE1eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/4T1yKz1IpdcvCi9o6e/giphy.gif" width="60"/>
    <h1>Route Distance & Cost Estimator</h1>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# 4️⃣ Select Mode
# ------------------------------
mode = st.selectbox(
    "Select Calculation Mode:",
    ['Single Trip Between Two Cities', 'Batch Calculation via CSV/Excel']
)

# ------------------------------
# 5️⃣ Single Trip Mode
# ------------------------------
if mode == 'Single Trip Between Two Cities':
    st.subheader("Single Trip: Distance & Travel Cost")
    starting_address_value = st.text_input("Enter starting address:", value="Delhi")
    destination_address_value = st.text_input("Enter destination address:", value="Chennai")
    transport_mode = st.selectbox(
        "Mode of transport:",
        ['car', 'bike', 'foot', 'hgv']
    )
    distance_unit = st.selectbox('Distance unit:', ['km','miles']).lower()
    cost_rate_input = st.text_input("Travel cost per unit distance:", value="200")

    if st.button("Calculate Distance & Travel Cost"):
        distance_value = get_city_distance.run(
            starting_address=starting_address_value,
            destination_address=destination_address_value,
            mode_of_transport=transport_mode,
            given_unit=distance_unit
        )
        if distance_value != "Distance not found":
            try:
                distance_float = float(distance_value)
                travel_cost = distance_float * float(cost_rate_input)
                st.success(f"Distance: {distance_float} {distance_unit}")
                st.success(f"Estimated Travel Cost: {travel_cost}")
            except ValueError:
                st.error("Error converting distance or cost.")
        else:
            st.error("Distance not found between the given addresses.")

# ------------------------------
# 6️⃣ Batch Mode
# ------------------------------
else:
    file_type = st.selectbox("Select file type:", ['CSV', 'Excel'])
    upload_file = st.file_uploader(f"Upload your {file_type} file:", type=['csv','xlsx'])

    if upload_file:
        df = pd.read_csv(upload_file) if file_type=='CSV' else pd.read_excel(upload_file)
        st.success("File loaded successfully!")

        col1, col2 = st.columns(2)
        with col1:
            starting_address_column = st.selectbox("Select column for starting address:", df.columns)
            distance_unit = st.selectbox('Distance unit:', ['km','miles']).lower()
            cost_rate_input = st.text_input("Travel cost per unit distance:", value="200")

        with col2:
            destination_option = st.radio("Destination address option:", ['Single Fixed Address', 'Select Column from File'])
            if destination_option == 'Single Fixed Address':
                fixed_destination_address = st.text_input("Enter destination address:", value="Chennai")
                use_destination_column = False
            else:
                destination_address_column = st.selectbox("Select column for destination address:", df.columns)
                use_destination_column = True

            transport_mode = st.selectbox("Mode of transport:", [
                'driving-car','driving-hgv','foot-walking','foot-hiking',
                'cycling-regular','cycling-road','cycling-mountain','cycling-electric'
            ])

        df['Distance'] = None
        df['Travel Cost'] = None

        if st.button("Calculate Distance & Travel Cost"):
            for idx, row in df.iterrows():
                start_val = row[starting_address_column]
                dest_val = row[destination_address_column] if use_destination_column else fixed_destination_address

                distance_value = get_city_distance.run(
                    starting_address=start_val,
                    destination_address=dest_val,
                    mode_of_transport=transport_mode,
                    given_unit=distance_unit
                )

                if distance_value != "Distance not found":
                    try:
                        distance_float = float(distance_value)
                        travel_cost = distance_float * float(cost_rate_input)
                        df.at[idx, "Distance"] = f"{distance_float} {distance_unit}"
                        df.at[idx, "Travel Cost"] = f"{travel_cost}"
                    except ValueError:
                        df.at[idx, "Distance"] = "NA"
                        df.at[idx, "Travel Cost"] = "NA"
                else:
                    df.at[idx, "Distance"] = "NA"
                    df.at[idx, "Travel Cost"] = "NA"

            st.success("Processing complete!")

            # Highlight invalid distances
            def highlight_invalid(val):
                if val == "NA":
                    return 'color: red; font-weight:bold'
                return 'color: #32CD32; font-weight:bold'

            st.dataframe(df.style.applymap(highlight_invalid, subset=["Distance"]))

            # ------------------------------
            # Download button + GIF inline properly
            # ------------------------------
            col_button, col_gif = st.columns([4,1])  # 4:1 ratio

            with col_button:
                if file_type=='CSV':
                    output_data = df.to_csv(index=False).encode('utf-8')
                    file_name = "City_distances_updated.csv"
                    mime_type = "text/csv"
                else:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    output_data = buffer.getvalue()
                    file_name = "City_distances_updated.xlsx"
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                st.download_button(
                    label="Click to Download",
                    data=output_data,
                    file_name=file_name,
                    mime=mime_type
                )
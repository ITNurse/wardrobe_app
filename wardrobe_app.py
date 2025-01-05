import streamlit as st
import pandas as pd
from PIL import Image
import os
import base64
import io  # Import the io module for BytesIO

__version__ = "1.1.1"

# Paths to your files
metadata_file = r"C:\Users\lisat\OneDrive\008 Inventory\Inventory.xlsx"
image_folder = r"C:\Users\lisat\OneDrive\008 Inventory\Apparel Images"

# Load your metadata from Excel
sheet_name = "Apparel Acces Footwear Inv"
df = pd.read_excel(metadata_file, sheet_name=sheet_name)

# Streamlit app setup
st.title("My Wardrobe Viewer")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "grid"
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# Fixed thumbnail height
thumbnail_height = 150

def get_image_base64(image_path, height):
    """
    Load an image, resize it to the specified height while maintaining aspect ratio,
    and return the base64-encoded string for embedding in HTML.
    """
    with Image.open(image_path) as img:
        aspect_ratio = img.width / img.height
        width = int(height * aspect_ratio)
        img = img.resize((width, height))
        # Encode the image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
    return img_base64

def show_grid():
    """
    Display the grid of items.
    """
    st.sidebar.title("Filters")
    categories = df['Category'].dropna().unique()  # Handle missing values if present
    selected_category = st.sidebar.selectbox("Select Category", sorted(categories))

    # Filter data by selected category
    filtered_df = df[df['Category'] == selected_category]

    # Display filtered items in a grid layout
    st.write(f"Showing items for: **{selected_category}**")
    items_per_row = 4
    rows = [filtered_df.iloc[i:i+items_per_row] for i in range(0, len(filtered_df), items_per_row)]

    for row in rows:
        cols = st.columns(items_per_row)  # Create new columns for the row
        for col, (_, item) in zip(cols, row.iterrows()):
            item_id = item['Item ID']
            image_path = os.path.join(image_folder, f"{item_id}.jpg")  # Adjust if images are in different format

            if os.path.exists(image_path):
                # Encode the image to base64
                img_base64 = get_image_base64(image_path, thumbnail_height)

                # Display the image and a form for selection
                with col:
                    with st.form(key=f"form_{item_id}"):
                        # Display the image
                        image_html = f"""
                            <img src="data:image/jpeg;base64,{img_base64}" style="height:{thumbnail_height}px; border-radius: 5px; border: 1px solid #ccc;" />
                        """
                        st.markdown(image_html, unsafe_allow_html=True)

                        # Submit button for selection
                        if st.form_submit_button("Select"):
                            st.session_state.page = "details"
                            st.session_state.selected_item = item_id
                            st.rerun()


def show_details(item_id):
    """
    Display the details of a specific item.
    """
    item = df[df['Item ID'] == item_id].iloc[0]
    st.write(f"### Details for Item ID: {item_id}")
    
    # Display the item's image
    image_path = os.path.join(image_folder, f"{item_id}.jpg")
    if os.path.exists(image_path):
        with Image.open(image_path) as img:
            st.image(img, caption=item['Category'], use_container_width=True)

    # Display all metadata
    st.write("#### Item Details:")
    for col in df.columns:
        st.write(f"**{col}:** {item[col]}")

    # Back button to return to the grid
    if st.button("Back"):
        st.session_state.page = "grid"
        st.rerun()

# Handle navigation between grid and details view
if st.session_state.page == "grid":
    show_grid()
elif st.session_state.page == "details":
    show_details(st.session_state.selected_item)

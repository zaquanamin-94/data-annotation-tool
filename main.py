import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# Connect to SQLite database
def connect_to_db():
    conn = sqlite3.connect("mydata.db")  # Update with your SQLite file
    return conn

# Get all tables in the SQLite database
def get_sqlite_tables():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return [table[0] for table in tables]

# Update data in the selected SQLite table
def update_table(feedback, rating, id, zp_tags, target_table):
    now = datetime.now()
    
    query = f"""
        UPDATE {target_table}
        SET rating = ?, feedback = ?, update_at = ?
        WHERE id = ? AND zp_tags = ?
    """
    
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, (rating, feedback, now, id, zp_tags))
        conn.commit()
        st.success("Row updated successfully!")
    except Exception as e:
        st.error(f"Error updating SQLite: {e}")
    finally:
        conn.close()

# Fetch data from the selected SQLite table
def display_data(selected_table):
    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"SELECT * FROM {selected_table} WHERE rating IS NULL"
    cursor.execute(query)
    data = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]  # Fetch column names
    conn.close()

    # Create a DataFrame for easier display
    df = pd.DataFrame(data, columns=columns)

    total_rows = len(df)

    # Initialize session state for index
    if "row_index" not in st.session_state:
        st.session_state.row_index = 0

    # Navigation buttons
    col1, col2, col3 = st.columns([12, 1, 1])

    with col2:
        if st.button("⬅️ Previous"):
            if st.session_state.row_index == 0:
                st.session_state.row_index = total_rows
            st.session_state.row_index -= 1

    with col3:
        if st.button("Next ➡️"):
            if st.session_state.row_index == total_rows - 1:
                st.session_state.row_index = 0
            else:
                st.session_state.row_index += 1

    # Display current row
    row = df.iloc[st.session_state.row_index]
    id = row['id']
    zp_tags = row['zp_tags']

    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.subheader(f"📝 Total Q/A Pair: {total_rows}")
        st.subheader(f"Q/A pair ID ---> {id}")
        st.subheader("Question")
        st.write(f"{row['prompt']}")
        st.subheader("Answer")
        st.write(f"{row['response']}")

    with right_col:
        with st.form(f"feedback_form_{st.session_state.row_index}"):
            feedback = st.text_area("💬 Feedback on this QA pair")
            rating = st.radio("Rating", ['please choose','Poor', 'Fair', 'Average', 'Good', 'Excellent'], horizontal=True)
            category = st.radio("Category", ['please choose','', 'Informational', 'Creative', 'Instructional', 'Technical', 'Conversational'], horizontal=True)
            submit = st.form_submit_button("Submit Feedback")
            
            if submit:
                if rating == 'please choose' or category == 'please choose':
                    st.warning("Please select a rating and category.")
                else:
                    st.success("Feedback submitted! ✅  \n *note: will automatically update comment and rating and categoty in DataBase*")
                    # update_table(feedback, rating, id, zp_tags, selected_table)

def main():
    st.set_page_config(page_title="SFT Data Tagging", layout="wide")
    st.title("Annotation Tool")
    
    # Get table names from SQLite
    table_names = get_sqlite_tables()
    
    if table_names:
        selected_table = st.selectbox("Select data source", table_names)
        display_data(selected_table)
    else:
        st.write("No tables found in the database.")

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# ------------------------ DATABASE CONFIGURATION ------------------------
from sqlalchemy import create_engine

# Use Render PostgreSQL connection string
DATABASE_URL = "postgresql://foodwaste_db_user:0tFgqsbEBjUEahV83y8jbruY5kcCbUJ1@dpg-d25191p5pdvs73ccfn2g-a.oregon-postgres.render.com/foodwaste_db"
engine = create_engine(DATABASE_URL)


# ------------------------ QUERY DEFINITIONS ------------------------
ANALYSIS_QUERIES = {
    "1. Providers count per city": "SELECT \"City\", COUNT(*) AS provider_count FROM providers GROUP BY \"City\" ORDER BY provider_count DESC;",
    "2. Top provider type by contribution": "SELECT \"Type\", COUNT(*) AS total_contributions FROM food_listings JOIN providers ON food_listings.\"Provider_ID\" = providers.\"Provider_ID\" GROUP BY \"Type\" ORDER BY total_contributions DESC;",
    "3. Contact info of providers by city": "SELECT \"Name\", \"Contact\" FROM providers WHERE \"City\" = 'Chennai';",
    "4. Receivers with most claims": "SELECT receivers.\"Name\", COUNT(*) AS total_claims FROM claims JOIN receivers ON claims.\"Receiver_ID\" = receivers.\"Receiver_ID\" GROUP BY receivers.\"Name\" ORDER BY total_claims DESC;",
    "5. Total food quantity available": "SELECT SUM(\"Quantity\") AS total_quantity FROM food_listings;",
    "6. City with highest food listings": "SELECT \"Location\", COUNT(*) AS listing_count FROM food_listings GROUP BY \"Location\" ORDER BY listing_count DESC LIMIT 1;",
    "7. Most common food types": "SELECT \"Food_Type\", COUNT(*) AS food_count FROM food_listings GROUP BY \"Food_Type\" ORDER BY food_count DESC;",
    "8. Claims per food item": "SELECT food_listings.\"Food_Name\", COUNT(*) AS claims_count FROM claims JOIN food_listings ON claims.\"Food_ID\" = food_listings.\"Food_ID\" GROUP BY food_listings.\"Food_Name\" ORDER BY claims_count DESC;",
    "9. Provider with most completed claims": "SELECT providers.\"Name\", COUNT(*) AS completed_claims FROM claims JOIN food_listings ON claims.\"Food_ID\" = food_listings.\"Food_ID\" JOIN providers ON food_listings.\"Provider_ID\" = providers.\"Provider_ID\" WHERE claims.\"Status\" = 'Completed' GROUP BY providers.\"Name\" ORDER BY completed_claims DESC;",
    "10. Claim status breakdown": "SELECT \"Status\", COUNT(*) FROM claims GROUP BY \"Status\";",
    "11. Avg food claimed per receiver": "SELECT receivers.\"Name\", AVG(food_listings.\"Quantity\") AS avg_claimed FROM claims JOIN receivers ON claims.\"Receiver_ID\" = receivers.\"Receiver_ID\" JOIN food_listings ON claims.\"Food_ID\" = food_listings.\"Food_ID\" GROUP BY receivers.\"Name\";",
    "12. Most claimed meal type": "SELECT \"Meal_Type\", COUNT(*) AS total_claims FROM claims JOIN food_listings ON claims.\"Food_ID\" = food_listings.\"Food_ID\" GROUP BY \"Meal_Type\" ORDER BY total_claims DESC;",
    "13. Total food donated per provider": "SELECT providers.\"Name\", SUM(food_listings.\"Quantity\") AS total_quantity FROM food_listings JOIN providers ON food_listings.\"Provider_ID\" = providers.\"Provider_ID\" GROUP BY providers.\"Name\" ORDER BY total_quantity DESC;"
}

# ------------------------ STREAMLIT UI ------------------------
st.set_page_config(layout="wide")
st.title("🍱 Local Food Wastage Management System")

engine = get_engine()

st.sidebar.header("📊 Analysis Panel")
selected_query = st.sidebar.selectbox("Choose an analysis question", list(ANALYSIS_QUERIES.keys()))

if st.sidebar.button("Run Query"):
    query = ANALYSIS_QUERIES[selected_query]
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
            st.subheader(f"Results for: {selected_query}")
            st.dataframe(df)
    except Exception as e:
        st.error(f"Error executing query: {e}")

# ------------------------ CRUD OPERATIONS ------------------------
st.sidebar.header("🛠️ CRUD Panel")
crud_table = st.sidebar.selectbox("Select table", ["providers", "receivers", "food_listings", "claims"])
crud_action = st.sidebar.selectbox("Action", ["View", "Insert", "Update", "Delete"])

with engine.connect() as conn:
    if crud_action == "View":
        st.subheader(f"📋 {crud_table.title()} Table")
        df = pd.read_sql_query(f"SELECT * FROM {crud_table}", conn)
        st.dataframe(df)

    elif crud_action == "Insert":
        st.subheader(f"➕ Add New Record to {crud_table.title()}")
        cols = pd.read_sql_query(f"SELECT * FROM {crud_table} LIMIT 0", conn).columns
        inputs = {col: st.text_input(col) for col in cols if col.lower() != 'claim_id'}
        if st.button("Insert Record"):
            cols_str = ", ".join(inputs.keys())
            values_str = ", ".join([f"'{v}'" for v in inputs.values()])
            try:
                conn.execute(f"INSERT INTO {crud_table} ({cols_str}) VALUES ({values_str})")
                st.success("Record inserted successfully")
            except Exception as e:
                st.error(f"Insert failed: {e}")

    elif crud_action == "Update":
        st.subheader(f"✏️ Update Record in {crud_table.title()}")
        key_col = pd.read_sql_query(f"SELECT * FROM {crud_table} LIMIT 1", conn).columns[0]
        record_id = st.text_input(f"Enter {key_col} to update")
        df = pd.read_sql_query(f"SELECT * FROM {crud_table} WHERE \"{key_col}\" = '{record_id}'", conn)
        if not df.empty:
            updates = {col: st.text_input(f"Update {col}", df[col][0]) for col in df.columns if col != key_col}
            if st.button("Update Record"):
                set_clause = ", ".join([f'"{k}" = \'{v}\'' for k, v in updates.items()])
                try:
                    conn.execute(f"UPDATE {crud_table} SET {set_clause} WHERE \"{key_col}\" = '{record_id}'")
                    st.success("Record updated successfully")
                except Exception as e:
                    st.error(f"Update failed: {e}")
        else:
            st.warning("No record found with that ID.")

    elif crud_action == "Delete":
        st.subheader(f"🗑️ Delete Record from {crud_table.title()}")
        key_col = pd.read_sql_query(f"SELECT * FROM {crud_table} LIMIT 1", conn).columns[0]
        record_id = st.text_input(f"Enter {key_col} to delete")
        if st.button("Delete Record"):
            try:
                conn.execute(f"DELETE FROM {crud_table} WHERE \"{key_col}\" = '{record_id}'")
                st.success("Record deleted successfully")
            except Exception as e:
                st.error(f"Delete failed: {e}")

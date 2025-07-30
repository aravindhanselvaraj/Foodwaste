import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- Database Connection ---
def get_engine():
    return create_engine(
        "postgresql://foodwaste_db_user:0tFgqsbEBjUEahV83y8jbruY5kcCbUJ1@dpg-d25191p5pdvs73ccfn2g-a.oregon-postgres.render.com/foodwaste_db"
    )

engine = get_engine()

# --- Sidebar Navigation ---
st.sidebar.title("🍽️ Local Food Wastage Management")
section = st.sidebar.radio("📌 Navigate to:", ["🏗️ CRUD Operations", "📊 Analysis Dashboard"])

if section == "🏗️ CRUD Operations":
    crud_table = st.sidebar.selectbox("📋 Select Table:", ["providers", "receivers", "food_donations", "food_claims"])
    st.title(f"🔧 Manage {crud_table.replace('_', ' ').title()}")

    # --- CRUD Operations ---
    with engine.connect() as conn:
        df = pd.read_sql_query(f'SELECT * FROM "{crud_table}"', conn)
        st.subheader("📄 Existing Records")
        st.dataframe(df, use_container_width=True)

        # Add new row
        st.subheader("➕ Add New Entry")
        new_data = {}
        for column in df.columns:
            if column == "id":
                continue
            new_data[column] = st.text_input(f"{column.title()}", key=f"add_{column}")

        if st.button("Add Entry"):
            cols = ", ".join([f'"{k}"' for k in new_data.keys()])
            vals = ", ".join([f':{k}' for k in new_data.keys()])
            insert_query = text(f"INSERT INTO \"{crud_table}\" ({cols}) VALUES ({vals})")
            conn.execute(insert_query, new_data)
            st.success("✅ New entry added successfully!")

        # Update entry
        st.subheader("✏️ Update Existing Entry")
        row_id = st.text_input("Enter ID to update:", key="update_id")
        updates = {}
        for column in df.columns:
            if column == "id":
                continue
            updates[column] = st.text_input(f"New {column.title()} (leave blank to skip)", key=f"update_{column}")
        updates = {k: v for k, v in updates.items() if v != ""}

        if st.button("Update Entry") and row_id:
            set_clause = ", ".join([f'"{k}" = :{k}' for k in updates.keys()])
            updates["id"] = row_id
            update_query = text(f"UPDATE \"{crud_table}\" SET {set_clause} WHERE id = :id")
            conn.execute(update_query, updates)
            st.success("🔄 Entry updated successfully!")

        # Delete entry
        st.subheader("🗑️ Delete Entry")
        delete_id = st.text_input("Enter ID to delete:", key="delete_id")
        if st.button("Delete Entry") and delete_id:
            delete_query = text(f"DELETE FROM \"{crud_table}\" WHERE id = :id")
            conn.execute(delete_query, {"id": delete_id})
            st.success("❌ Entry deleted successfully!")

elif section == "📊 Analysis Dashboard":
    st.title("📊 Food Waste Analysis Dashboard")
    st.caption("Visual insights from provider and receiver activity")

    query_options = [
        "Top 5 Food Providers",
        "Top 5 Receivers",
        "Most Donated Food Items",
        "Monthly Donation Summary",
        "Monthly Claim Summary",
        "Unclaimed Donations",
        "Claim Rate by Food Type",
        "Provider Donation Count",
        "Receiver Claim Count",
        "Average Donation Per Provider",
        "Most Active Provider (by count)",
        "Most Active Receiver (by count)",
        "Donations by City",
        "Claims by City",
        "Oldest Unclaimed Donations"
    ]

    selected_query = st.selectbox("📌 Choose an analysis:", query_options)

    query_dict = {
        "Top 5 Food Providers": "SELECT p.name, COUNT(d.id) AS total_donations FROM food_donations d JOIN providers p ON d.provider_id = p.id GROUP BY p.name ORDER BY total_donations DESC LIMIT 5",
        "Top 5 Receivers": "SELECT r.name, COUNT(c.id) AS total_claims FROM food_claims c JOIN receivers r ON c.receiver_id = r.id GROUP BY r.name ORDER BY total_claims DESC LIMIT 5",
        "Most Donated Food Items": "SELECT food_type, COUNT(*) AS count FROM food_donations GROUP BY food_type ORDER BY count DESC LIMIT 5",
        "Monthly Donation Summary": "SELECT DATE_TRUNC('month', donation_date) AS month, COUNT(*) AS total FROM food_donations GROUP BY month ORDER BY month DESC",
        "Monthly Claim Summary": "SELECT DATE_TRUNC('month', claim_date) AS month, COUNT(*) AS total FROM food_claims GROUP BY month ORDER BY month DESC",
        "Unclaimed Donations": "SELECT * FROM food_donations WHERE id NOT IN (SELECT donation_id FROM food_claims)",
        "Claim Rate by Food Type": "SELECT d.food_type, ROUND(COUNT(c.id)*100.0 / NULLIF(COUNT(d.id),0), 2) AS claim_rate_percent FROM food_donations d LEFT JOIN food_claims c ON d.id = c.donation_id GROUP BY d.food_type",
        "Provider Donation Count": "SELECT p.name, COUNT(d.id) AS total FROM providers p LEFT JOIN food_donations d ON p.id = d.provider_id GROUP BY p.name",
        "Receiver Claim Count": "SELECT r.name, COUNT(c.id) AS total FROM receivers r LEFT JOIN food_claims c ON r.id = c.receiver_id GROUP BY r.name",
        "Average Donation Per Provider": "SELECT p.name, ROUND(AVG(d.quantity), 2) AS avg_quantity FROM food_donations d JOIN providers p ON d.provider_id = p.id GROUP BY p.name",
        "Most Active Provider (by count)": "SELECT p.name, COUNT(d.id) AS donations FROM food_donations d JOIN providers p ON d.provider_id = p.id GROUP BY p.name ORDER BY donations DESC LIMIT 1",
        "Most Active Receiver (by count)": "SELECT r.name, COUNT(c.id) AS claims FROM food_claims c JOIN receivers r ON c.receiver_id = r.id GROUP BY r.name ORDER BY claims DESC LIMIT 1",
        "Donations by City": "SELECT city, COUNT(*) AS total FROM providers JOIN food_donations ON providers.id = food_donations.provider_id GROUP BY city",
        "Claims by City": "SELECT city, COUNT(*) AS total FROM receivers JOIN food_claims ON receivers.id = food_claims.receiver_id GROUP BY city",
        "Oldest Unclaimed Donations": "SELECT * FROM food_donations WHERE id NOT IN (SELECT donation_id FROM food_claims) ORDER BY donation_date ASC LIMIT 5"
    }

    with engine.connect() as conn:
        try:
            df = pd.read_sql_query(query_dict[selected_query], conn)
            st.subheader(f"📌 Result: {selected_query}")
            st.dataframe(df, use_container_width=True)
            st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name="analysis.csv")
        except Exception as e:
            st.error("⚠️ Error running the query. Please check your data.")

with engine.connect() as conn:
    tables_df = pd.read_sql_query(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'", conn
    )
    st.sidebar.markdown("### 🧪 Available Tables")
    st.sidebar.write(tables_df)

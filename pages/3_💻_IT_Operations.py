import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.getcwd())

from app.data.db import connect_database
from app.data.tickets import load_it_tickets_csv, update_ticket
from app.utils.stream_helpers import safe_rerun
from models.it_ticket import ITTicket 

def itops_hub_ui():
    st.markdown(
        """
        <div style="background:linear-gradient(90deg,#064e3b,#10b981);padding:12px;border-radius:8px;color:white;">
            <h2 style="margin:0">🛠️ IT Operations</h2>
            <div style="opacity:0.9">Service desk and tickets management</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    conn = connect_database()
    try:
        df = pd.read_sql_query("SELECT * FROM it_tickets", conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        df = pd.DataFrame()
    conn.close()

    ticket_objects = []
    if not df.empty:
        for _, row in df.iterrows():

            t = ITTicket(
                id=row.get('id'),
                ticket_id=row.get('ticket_id', 'Unknown'),
                subject=row.get('subject', row.get('title', 'No Subject')),
                priority=row.get('priority', 'Low'),
                status=row.get('status', 'Open'),
                category=row.get('category', 'General'),
                created_date=row.get('created_date'),
                assigned_to=row.get('assigned_to') 
            )
            ticket_objects.append(t)

    total = len(ticket_objects)
    open_cnt = len([t for t in ticket_objects if t.status.lower() == 'open'])
    waiting = len([t for t in ticket_objects if 'waiting' in t.status.lower()])

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Tickets", total)
    c2.metric("Open Tickets", open_cnt)
    c3.metric("Waiting for User", waiting)

    st.markdown("---")
    
    if total == 0:
        if st.button("Load tickets from CSV"):
            conn2 = connect_database()
            try:
                loaded = load_it_tickets_csv(conn2) 
                st.success(f"Loaded {loaded} rows")
                safe_rerun()
            except Exception as e:
                st.error(f"Error loading: {e}")
            conn2.close()

    st.subheader("Ticket Queue")

    if not ticket_objects:
        st.info("No tickets found.")
    else:
        for ticket in ticket_objects[:5]:
            with st.expander(f"{ticket.get_status_emoji()} {ticket.ticket_id}: {ticket.subject}"):
                c_a, c_b = st.columns(2)
                c_a.write(f"**Priority:** {ticket.priority}")
                c_a.write(f"**Category:** {ticket.category}")
                
                assignee_display = ticket.assigned_to if ticket.is_assigned() else "Unassigned"
                c_b.write(f"**Assigned To:** `{assignee_display}`")
                
        if len(ticket_objects) > 5:
            st.caption(f"And {len(ticket_objects)-5} more...")

    st.markdown("---")


    if not df.empty:
        st.subheader("Analytics")
        if "created_date" in df.columns:
            df["created_date"] = pd.to_datetime(df["created_date"], errors="coerce")
            now = pd.Timestamp.now()
            df["age_days"] = (now - df["created_date"]).dt.total_seconds() / 86400.0
            
            open_df = df[df["status"].str.lower() != "closed"].copy()
            if not open_df.empty:
                st.bar_chart(open_df["status"].value_counts())

    st.subheader("Update Ticket")
    if not df.empty:
        ticket_ids = [t.id for t in ticket_objects]
        display_map = {t.id: f"{t.ticket_id} - {t.subject}" for t in ticket_objects}
        
        selected_db_id = st.selectbox("Select Ticket", ticket_ids, format_func=lambda x: display_map[x])
        
        selected_ticket = next((t for t in ticket_objects if t.id == selected_db_id), None)
        
        if selected_ticket:
            new_assignee = st.text_input("Assign to", value=selected_ticket.assigned_to if selected_ticket.assigned_to else "")
            new_status = st.selectbox("Status", ["open", "closed", "waiting_user"], index=0)
            
            if st.button("Update"):
                connu = connect_database()
                update_ticket(connu, selected_ticket.id, status=new_status)
                connu.close()
                st.success("Updated!")
                safe_rerun()

itops_hub_ui()
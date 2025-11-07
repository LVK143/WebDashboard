import streamlit as st
import pandas as pd
import json
import os
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Neo CRM Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for advanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
def init_database():
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            company TEXT,
            industry TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize session state
if 'customers' not in st.session_state:
    init_database()
    st.session_state.customers = []

def main():
    # Header with navigation
    st.markdown('<h1 class="main-header">🚀 Neo CRM Pro</h1>', unsafe_allow_html=True)
    
    # Navigation
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Dashboard", "👥 Customers", "📈 Analytics", "🎯 Segments", "⚙️ Settings"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "👥 Customers":
        show_customers()
    elif page == "📈 Analytics":
        show_analytics()
    elif page == "🎯 Segments":
        show_segments()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.header("🎯 Dashboard Overview")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(st.session_state.customers)
        st.metric("Total Customers", total_customers, "12%")
    
    with col2:
        unique_companies = len(set([c.get('company', '') for c in st.session_state.customers]))
        st.metric("Companies", unique_companies, "8%")
    
    with col3:
        today_count = len([c for c in st.session_state.customers 
                          if 'added_date' in c and 
                          datetime.fromisoformat(c['added_date']).date() == datetime.now().date()])
        st.metric("New Today", today_count)
    
    with col4:
        vip_count = len([c for c in st.session_state.customers 
                        if c.get('company') in ['Tech Corp', 'Global Inc']])
        st.metric("VIP Clients", vip_count)
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    if st.session_state.customers:
        recent_customers = sorted(st.session_state.customers, 
                                key=lambda x: x.get('added_date', ''), 
                                reverse=True)[:5]
        
        for customer in recent_customers:
            with st.expander(f"👤 {customer['name']} - {customer['company']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {customer['email']}")
                    st.write(f"**Phone:** {customer['phone']}")
                with col2:
                    st.write(f"**Added:** {datetime.fromisoformat(customer.get('added_date', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}")
                    if st.button("Quick Actions", key=f"action_{customer['name']}"):
                        st.session_state.editing_index = st.session_state.customers.index(customer)
                        st.session_state.current_page = "👥 Customers"
                        st.rerun()

def show_customers():
    st.header("👥 Customer Management")
    
    # Add customer form in sidebar
    with st.sidebar:
        st.header("➕ Add New Customer")
        with st.form("add_customer_form", clear_on_submit=True):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            company = st.text_input("Company")
            industry = st.selectbox("Industry", ["Technology", "Healthcare", "Finance", "Education", "Other"])
            
            if st.form_submit_button("Add Customer"):
                if name and email:
                    new_customer = {
                        'name': name, 'email': email, 'phone': phone, 
                        'company': company, 'industry': industry,
                        'added_date': datetime.now().isoformat()
                    }
                    st.session_state.customers.append(new_customer)
                    st.success("Customer added!")
                    st.rerun()
    
    # Search and filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search customers", placeholder="Name, email, company...")
    
    with col2:
        industry_filter = st.selectbox("Industry", ["All", "Technology", "Healthcare", "Finance", "Education", "Other"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest", "Name A-Z", "Company"])
    
    # Display customers
    if not st.session_state.customers:
        st.info("No customers yet. Add some using the sidebar form!")
        return
    
    filtered_customers = st.session_state.customers
    
    # Apply filters
    if search_term:
        filtered_customers = [c for c in filtered_customers 
                            if search_term.lower() in c['name'].lower() 
                            or search_term.lower() in c['email'].lower()
                            or search_term.lower() in c['company'].lower()]
    
    if industry_filter != "All":
        filtered_customers = [c for c in filtered_customers if c.get('industry') == industry_filter]
    
    # Apply sorting
    if sort_by == "Newest":
        filtered_customers.sort(key=lambda x: x.get('added_date', ''), reverse=True)
    elif sort_by == "Name A-Z":
        filtered_customers.sort(key=lambda x: x['name'].lower())
    elif sort_by == "Company":
        filtered_customers.sort(key=lambda x: x.get('company', '').lower())
    
    # Display as interactive table
    if filtered_customers:
        df = pd.DataFrame(filtered_customers)
        
        # Enhanced dataframe display
        st.dataframe(
            df[['name', 'email', 'phone', 'company', 'industry', 'added_date']],
            use_container_width=True,
            hide_index=True
        )
        
        # Action buttons for each customer
        st.subheader("🛠️ Customer Actions")
        for i, customer in enumerate(filtered_customers):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{customer['name']}** - {customer['company']}")
            
            with col2:
                if st.button("👀 View", key=f"view_{i}"):
                    st.session_state.viewing_customer = customer
                    show_customer_detail(customer)
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{i}"):
                    st.session_state.editing_customer = customer
                    st.session_state.edit_index = st.session_state.customers.index(customer)
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{i}"):
                    if st.button("✅ Confirm Delete", key=f"confirm_delete_{i}"):
                        st.session_state.customers.remove(customer)
                        st.success("Customer deleted!")
                        st.rerun()

def show_analytics():
    st.header("📈 Advanced Analytics")
    
    if not st.session_state.customers:
        st.info("Add some customers to see analytics!")
        return
    
    df = pd.DataFrame(st.session_state.customers)
    
    # Industry distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Industry Distribution")
        if 'industry' in df.columns:
            industry_counts = df['industry'].value_counts()
            fig = px.pie(values=industry_counts.values, names=industry_counts.index)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Company Size")
        company_counts = df['company'].value_counts().head(10)
        fig = px.bar(x=company_counts.values, y=company_counts.index, orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer growth timeline
    st.subheader("📈 Customer Growth")
    if 'added_date' in df.columns:
        df['added_date'] = pd.to_datetime(df['added_date'])
        daily_counts = df.groupby(df['added_date'].dt.date).size().cumsum()
        fig = px.line(x=daily_counts.index, y=daily_counts.values, title="Cumulative Customer Growth")
        st.plotly_chart(fig, use_container_width=True)

def show_segments():
    st.header("🎯 Customer Segments")
    
    if not st.session_state.customers:
        st.info("No customers to segment!")
        return
    
    # Define segments
    segments = {
        "🚀 VIP Clients": {
            "criteria": lambda x: x.get('company') in ['Tech Corp', 'Global Inc'],
            "count": 0,
            "customers": []
        },
        "⭐ High Value": {
            "criteria": lambda x: x.get('industry') == 'Technology',
            "count": 0,
            "customers": []
        },
        "📈 Growth Potential": {
            "criteria": lambda x: 'added_date' in x and 
                                 datetime.now() - datetime.fromisoformat(x['added_date']) < timedelta(days=30),
            "count": 0,
            "customers": []
        }
    }
    
    # Calculate segments
    for customer in st.session_state.customers:
        for segment_name, segment in segments.items():
            if segment['criteria'](customer):
                segment['count'] += 1
                segment['customers'].append(customer)
    
    # Display segments
    cols = st.columns(len(segments))
    for (segment_name, segment), col in zip(segments.items(), cols):
        with col:
            st.metric(segment_name, segment['count'])
            if st.button(f"View {segment_name}", key=segment_name):
                st.session_state.current_segment = segment_name
                st.session_state.segment_customers = segment['customers']

def show_settings():
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("🔧 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Export All Data"):
            df = pd.DataFrame(st.session_state.customers)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="customers_export.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🔄 Reset Demo Data"):
            st.session_state.customers = []
            st.success("Data reset!")
            st.rerun()
    
    st.subheader("🎨 Appearance")
    theme = st.selectbox("Color Theme", ["Light", "Dark", "Auto"])
    st.info(f"Selected theme: {theme}")

def show_customer_detail(customer):
    st.header(f"👤 {customer['name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contact Information")
        st.write(f"**Email:** {customer['email']}")
        st.write(f"**Phone:** {customer['phone']}")
        st.write(f"**Company:** {customer['company']}")
        st.write(f"**Industry:** {customer.get('industry', 'Not specified')}")
    
    with col2:
        st.subheader("Activity")
        st.write(f"**Added:** {datetime.fromisoformat(customer.get('added_date', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}")
        if 'updated_date' in customer:
            st.write(f"**Last Updated:** {datetime.fromisoformat(customer['updated_date']).strftime('%Y-%m-%d %H:%M')}")
    
    # Quick actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Send Email"):
            st.info("Email functionality would be implemented here")
    
    with col2:
        if st.button("📞 Call Customer"):
            st.info("Click to call functionality")
    
    with col3:
        if st.button("📝 Add Note"):
            st.text_area("Customer Notes", placeholder="Add notes about this customer...")

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page configuration - ONLY ONCE at the top
st.set_page_config(
    page_title="Neo CRM Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    .customer-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #3498db;
    }
    .section-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for customers
if 'customers' not in st.session_state:
    # Try to load from file, otherwise start empty
    try:
        if os.path.exists('customers.json'):
            with open('customers.json', 'r') as f:
                st.session_state.customers = json.load(f)
        else:
            st.session_state.customers = []
    except:
        st.session_state.customers = []

def save_customers():
    """Save customers to JSON file"""
    with open('customers.json', 'w') as f:
        json.dump(st.session_state.customers, f, indent=2)

def add_customer(name, email, phone, company):
    """Add a new customer"""
    new_customer = {
        'name': name,
        'email': email,
        'phone': phone,
        'company': company,
        'added_date': datetime.now().isoformat(),
        'id': len(st.session_state.customers) + 1
    }
    st.session_state.customers.append(new_customer)
    save_customers()
    return new_customer

def delete_customer(index):
    """Delete a customer"""
    if 0 <= index < len(st.session_state.customers):
        customer_name = st.session_state.customers[index]['name']
        st.session_state.customers.pop(index)
        save_customers()
        return customer_name
    return None

def update_customer(index, name, email, phone, company):
    """Update customer details"""
    if 0 <= index < len(st.session_state.customers):
        st.session_state.customers[index].update({
            'name': name,
            'email': email,
            'phone': phone,
            'company': company,
            'updated_date': datetime.now().isoformat()
        })
        save_customers()
        return True
    return False

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Neo CRM Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for Quick Actions and Add Customer form
    with st.sidebar:
        st.header("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Report", use_container_width=True):
                st.balloons()
                st.success("Report generated successfully!")
                
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        st.header("👥 Add New Customer")
        
        # UNIQUE FORM KEY: "add_customer_form"
        with st.form("add_customer_form", clear_on_submit=True):
            name = st.text_input("Customer Name", placeholder="Enter full name")
            email = st.text_input("Email", placeholder="Enter email address")
            phone = st.text_input("Phone", placeholder="Enter phone number")
            company = st.text_input("Company", placeholder="Enter company name")
            
            submitted = st.form_submit_button("Add Customer", use_container_width=True)
            if submitted:
                if name and email and phone and company:
                    new_customer = add_customer(name, email, phone, company)
                    st.success(f"✅ Customer **{new_customer['name']}** added successfully!")
                else:
                    st.error("❌ Please fill in all fields!")

    # Main dashboard metrics
    st.header("📊 Dashboard Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(st.session_state.customers)
        st.metric("Total Customers", total_customers)
    
    with col2:
        unique_companies = len(set([c.get('company', '') for c in st.session_state.customers]))
        st.metric("Unique Companies", unique_companies)
    
    with col3:
        today_count = len([c for c in st.session_state.customers 
                          if 'added_date' in c and 
                          datetime.fromisoformat(c['added_date']).date() == datetime.now().date()])
        st.metric("Added Today", today_count)
    
    with col4:
        st.metric("Active Users", total_customers)

    # Search and filters section
    st.header("🔍 Customer Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input("Search customers", 
                                  placeholder="Search by name, email, or company...",
                                  key="search_input")
    
    with col2:
        view_mode = st.radio("View Mode:", 
                           ["Table View", "Card View"], 
                           horizontal=True,
                           key="view_mode")

    # Display customers
    if not st.session_state.customers:
        st.info("🌟 No customers found. Add your first customer using the form in the sidebar!")
    else:
        # Filter customers based on search
        filtered_customers = st.session_state.customers
        if search_term:
            filtered_customers = [
                customer for customer in st.session_state.customers
                if search_term.lower() in customer['name'].lower() 
                or search_term.lower() in customer['email'].lower()
                or search_term.lower() in customer['company'].lower()
            ]
        
        if not filtered_customers:
            st.warning("🔍 No customers match your search criteria.")
        else:
            if view_mode == "Table View":
                # Table view with enhanced features
                df = pd.DataFrame(filtered_customers)
                
                # Reorder columns for better display
                column_order = ['name', 'email', 'phone', 'company', 'added_date']
                existing_columns = [col for col in column_order if col in df.columns]
                df = df[existing_columns + [col for col in df.columns if col not in column_order]]
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
            else:
                # Card view
                for i, customer in enumerate(filtered_customers):
                    original_index = st.session_state.customers.index(customer)
                    
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div class="customer-card">
                                <h4>👤 {customer['name']}</h4>
                                <p><strong>📧 Email:</strong> {customer['email']}</p>
                                <p><strong>📞 Phone:</strong> {customer['phone']}</p>
                                <p><strong>🏢 Company:</strong> {customer['company']}</p>
                                <p><small><strong>📅 Added:</strong> {datetime.fromisoformat(customer.get('added_date', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M')}</small></p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.write("")  # Spacing
                            
                            # Edit button
                            if st.button("✏️", key=f"edit_{i}", help="Edit customer"):
                                st.session_state.editing_index = original_index
                                st.session_state.edit_name = customer['name']
                                st.session_state.edit_email = customer['email']
                                st.session_state.edit_phone = customer['phone']
                                st.session_state.edit_company = customer['company']
                            
                            # Delete button
                            if st.button("🗑️", key=f"delete_{i}", help="Delete customer"):
                                customer_name = delete_customer(original_index)
                                if customer_name:
                                    st.success(f"✅ Customer **{customer_name}** deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Error deleting customer")

            # Show filtered results count
            if search_term and len(filtered_customers) != len(st.session_state.customers):
                st.info(f"🔍 Showing {len(filtered_customers)} of {len(st.session_state.customers)} customers")

    # Edit customer section (only show if editing)
    if 'editing_index' in st.session_state:
        st.markdown("---")
        st.header("✏️ Edit Customer")
        
        # UNIQUE FORM KEY: "edit_customer_form"
        with st.form("edit_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_name = st.text_input("Name", 
                                        value=st.session_state.get('edit_name', ''),
                                        key="edit_name")
                edit_email = st.text_input("Email", 
                                         value=st.session_state.get('edit_email', ''),
                                         key="edit_email")
            
            with col2:
                edit_phone = st.text_input("Phone", 
                                         value=st.session_state.get('edit_phone', ''),
                                         key="edit_phone")
                edit_company = st.text_input("Company", 
                                           value=st.session_state.get('edit_company', ''),
                                           key="edit_company")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                update_submitted = st.form_submit_button("💾 Update", use_container_width=True)
            
            with col2:
                cancel_submitted = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if update_submitted:
                if edit_name and edit_email and edit_phone and edit_company:
                    success = update_customer(
                        st.session_state.editing_index,
                        edit_name,
                        edit_email,
                        edit_phone,
                        edit_company
                    )
                    if success:
                        st.success(f"✅ Customer **{edit_name}** updated successfully!")
                        # Clear editing state
                        if 'editing_index' in st.session_state:
                            del st.session_state.editing_index
                        st.rerun()
                    else:
                        st.error("❌ Error updating customer")
                else:
                    st.error("❌ Please fill in all fields!")
            
            if cancel_submitted:
                if 'editing_index' in st.session_state:
                    del st.session_state.editing_index
                st.rerun()

    # Export functionality
    if st.session_state.customers:
        st.markdown("---")
        st.header("📤 Export Data")
        
        df = pd.DataFrame(st.session_state.customers)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV Export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="customers.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # JSON Export
            json_str = json.dumps(st.session_state.customers, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="customers.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col3:
            # Excel Export (if pandas supports it)
            try:
                excel_file = df.to_excel("customers.xlsx", index=False)
                with open("customers.xlsx", "rb") as f:
                    excel_data = f.read()
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="customers.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
            except:
                st.info("ℹ️ Excel export requires openpyxl")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "© 2025 Neo CRM | Built with ❤️ using Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

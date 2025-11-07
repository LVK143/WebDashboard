import streamlit as st
import pandas as pd
import json
import os

# Page configuration
st.set_page_config(
    page_title="Mini CRM Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
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
    .stButton button {
        width: 100%;
        border-radius: 5px;
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
        json.dump(st.session_state.customers, f)

def add_customer(name, email, phone, company):
    """Add a new customer"""
    new_customer = {
        'name': name,
        'email': email,
        'phone': phone,
        'company': company
    }
    st.session_state.customers.append(new_customer)
    save_customers()
    st.success(f"Customer {name} added successfully!")

def delete_customer(index):
    """Delete a customer"""
    customer_name = st.session_state.customers[index]['name']
    st.session_state.customers.pop(index)
    save_customers()
    st.success(f"Customer {customer_name} deleted successfully!")

def update_customer(index, name, email, phone, company):
    """Update customer details"""
    st.session_state.customers[index] = {
        'name': name,
        'email': email,
        'phone': phone,
        'company': company
    }
    save_customers()
    st.success(f"Customer {name} updated successfully!")

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">👥 Mini CRM Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for Add Customer form
    with st.sidebar:
        st.markdown('<h3 class="section-header">➕ Add New Customer</h3>', unsafe_allow_html=True)
        
        with st.form("customer_form"):
            name = st.text_input("Customer Name", placeholder="Enter full name")
            email = st.text_input("Email", placeholder="Enter email address")
            phone = st.text_input("Phone", placeholder="Enter phone number")
            company = st.text_input("Company", placeholder="Enter company name")
            
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                if name and email and phone and company:
                    add_customer(name, email, phone, company)
                else:
                    st.error("Please fill in all fields!")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h3 class="section-header">📋 Customer List</h3>', unsafe_allow_html=True)
        
        # Search and filter
        search_term = st.text_input("🔍 Search customers by name or company", placeholder="Type to search...")
    
    with col2:
        st.metric("Total Customers", len(st.session_state.customers))
    
    # Display customers
    if not st.session_state.customers:
        st.info("No customers found. Add your first customer using the form in the sidebar!")
    else:
        # Filter customers based on search
        filtered_customers = st.session_state.customers
        if search_term:
            filtered_customers = [
                customer for customer in st.session_state.customers
                if search_term.lower() in customer['name'].lower() 
                or search_term.lower() in customer['company'].lower()
            ]
        
        if not filtered_customers:
            st.warning("No customers match your search criteria.")
        else:
            # Display as cards or table based on user preference
            view_mode = st.radio("View Mode:", ["Cards", "Table"], horizontal=True)
            
            if view_mode == "Cards":
                # Card view
                for i, customer in enumerate(filtered_customers):
                    # Find original index for editing/deleting
                    original_index = st.session_state.customers.index(customer)
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div class="customer-card">
                                <h4>{customer['name']}</h4>
                                <p><strong>Email:</strong> {customer['email']}</p>
                                <p><strong>Phone:</strong> {customer['phone']}</p>
                                <p><strong>Company:</strong> {customer['company']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            # Edit and Delete buttons
                            st.write("")  # Spacing
                            st.write("")  # Spacing
                            
                            # Edit button
                            if st.button(f"✏️ Edit", key=f"edit_{i}"):
                                st.session_state.editing_index = original_index
                                st.session_state.edit_name = customer['name']
                                st.session_state.edit_email = customer['email']
                                st.session_state.edit_phone = customer['phone']
                                st.session_state.edit_company = customer['company']
                            
                            # Delete button
                            if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                                delete_customer(original_index)
                                st.rerun()
            
            else:
                # Table view
                df = pd.DataFrame(filtered_customers)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Edit/Delete options for table view
                st.markdown("---")
                st.subheader("Manage Customers")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    edit_index = st.number_input(
                        "Customer number to edit:",
                        min_value=0,
                        max_value=len(st.session_state.customers)-1 if st.session_state.customers else 0,
                        value=0,
                        step=1
                    )
                
                with col2:
                    if st.session_state.customers:
                        customer = st.session_state.customers[edit_index]
                        if st.button("Edit This Customer"):
                            st.session_state.editing_index = edit_index
                            st.session_state.edit_name = customer['name']
                            st.session_state.edit_email = customer['email']
                            st.session_state.edit_phone = customer['phone']
                            st.session_state.edit_company = customer['company']
                
                with col3:
                    delete_index = st.number_input(
                        "Customer number to delete:",
                        min_value=0,
                        max_value=len(st.session_state.customers)-1 if st.session_state.customers else 0,
                        value=0,
                        step=1,
                        key="delete_input"
                    )
                
                with col4:
                    if st.session_state.customers and st.button("Delete This Customer", type="secondary"):
                        delete_customer(delete_index)
                        st.rerun()
    
    # Edit customer modal
    if 'editing_index' in st.session_state:
        st.markdown("---")
        st.markdown('<h3 class="section-header">✏️ Edit Customer</h3>', unsafe_allow_html=True)
        
        with st.form("edit_form"):
            edit_name = st.text_input("Name", value=st.session_state.get('edit_name', ''))
            edit_email = st.text_input("Email", value=st.session_state.get('edit_email', ''))
            edit_phone = st.text_input("Phone", value=st.session_state.get('edit_phone', ''))
            edit_company = st.text_input("Company", value=st.session_state.get('edit_company', ''))
            
            col1, col2 = st.columns(2)
            
            with col1:
                update_submitted = st.form_submit_button("Update Customer")
                if update_submitted:
                    if edit_name and edit_email and edit_phone and edit_company:
                        update_customer(
                            st.session_state.editing_index,
                            edit_name,
                            edit_email,
                            edit_phone,
                            edit_company
                        )
                        # Clear editing state
                        if 'editing_index' in st.session_state:
                            del st.session_state.editing_index
                        st.rerun()
                    else:
                        st.error("Please fill in all fields!")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    if 'editing_index' in st.session_state:
                        del st.session_state.editing_index
                    st.rerun()

    # Export functionality
    st.markdown("---")
    st.markdown('<h3 class="section-header">📤 Export Data</h3>', unsafe_allow_html=True)
    
    if st.session_state.customers:
        df = pd.DataFrame(st.session_state.customers)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Export
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="customers.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON Export
            json_str = json.dumps(st.session_state.customers, indent=2)
            st.download_button(
                label="Download as JSON",
                data=json_str,
                file_name="customers.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()

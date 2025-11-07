// Advanced CRM JavaScript with all features
class CRM {
    constructor() {
        this.customers = JSON.parse(localStorage.getItem('customers')) || [];
        this.editingIndex = null;
        this.selectedCustomers = new Set();
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.filteredCustomers = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.applyTheme();
        this.displayCustomers();
        this.hideLoader();
    }

    setupEventListeners() {
        // Form submission
        document.getElementById('customerForm').addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Theme toggle
        document.getElementById('themeBtn').addEventListener('click', () => this.toggleTheme());
        
        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => this.handleSearch(e.target.value));
        document.getElementById('clearSearch').addEventListener('click', () => this.clearSearch());
        
        // Sorting
        document.getElementById('sortSelect').addEventListener('change', (e) => this.handleSort(e.target.value));
        
        // Bulk operations
        document.getElementById('selectAll').addEventListener('change', (e) => this.toggleSelectAll(e.target.checked));
        document.getElementById('bulkDeleteBtn').addEventListener('click', () => this.bulkDelete());
        
        // Export/Import
        document.getElementById('exportBtn').addEventListener('click', () => this.exportData());
        document.getElementById('importBtn').addEventListener('click', () => this.importData());
        
        // Refresh
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshData());
        
        // Form toggle
        document.getElementById('toggleForm').addEventListener('click', () => this.toggleForm());
        
        // Modal close
        document.querySelector('.close-modal').addEventListener('click', () => this.closeModal());
    }

    displayCustomers(customersToDisplay = this.customers) {
        const tbody = document.getElementById('customerList');
        const emptyState = document.getElementById('emptyState');
        
        this.filteredCustomers = customersToDisplay;
        
        if (customersToDisplay.length === 0) {
            tbody.innerHTML = '';
            emptyState.style.display = 'block';
            this.updateStats();
            this.updateSelectedCount();
            return;
        }
        
        emptyState.style.display = 'none';
        tbody.innerHTML = '';
        
        customersToDisplay.forEach((customer, displayIndex) => {
            const originalIndex = this.customers.findIndex(c => 
                c.email === customer.email && c.phone === customer.phone
            );
            
            const row = document.createElement('tr');
            row.className = 'fade-in';
            row.innerHTML = `
                <td>
                    <input type="checkbox" class="customer-checkbox" 
                           data-index="${originalIndex}"
                           ${this.selectedCustomers.has(originalIndex) ? 'checked' : ''}>
                </td>
                <td>${this.highlightText(customer.name)}</td>
                <td>${this.highlightText(customer.email)}</td>
                <td>${customer.phone}</td>
                <td>${this.highlightText(customer.company)}</td>
                <td>
                    <span class="status-badge status-active">Active</span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-view btn-sm" onclick="crm.viewCustomer(${originalIndex})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-edit btn-sm" onclick="crm.editCustomer(${originalIndex})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-delete btn-sm" onclick="crm.deleteCustomer(${originalIndex})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Add event listeners to checkboxes
        document.querySelectorAll('.customer-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => this.toggleCustomerSelection(e.target));
        });
        
        this.updateStats();
        this.updateSelectedCount();
    }

    handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const customerData = {
            name: formData.get('name').trim(),
            email: formData.get('email').trim(),
            phone: formData.get('phone').trim(),
            company: formData.get('company').trim(),
            createdAt: new Date().toISOString(),
            status: 'active'
        };

        if (!this.validateCustomer(customerData)) return;

        if (this.editingIndex === null) {
            this.addCustomer(customerData);
        } else {
            this.updateCustomer(this.editingIndex, customerData);
        }

        e.target.reset();
        this.showToast('Customer saved successfully!', 'success');
    }

    validateCustomer(customer) {
        if (!customer.name || !customer.email || !customer.phone || !customer.company) {
            this.showToast('Please fill in all fields', 'error');
            return false;
        }

        if (!this.isValidEmail(customer.email)) {
            this.showToast('Please enter a valid email address', 'error');
            return false;
        }

        return true;
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    addCustomer(customer) {
        this.customers.push(customer);
        this.saveToLocalStorage();
        this.displayCustomers();
        this.animateAdd();
    }

    updateCustomer(index, customer) {
        this.customers[index] = customer;
        this.saveToLocalStorage();
        this.displayCustomers();
        this.editingIndex = null;
        document.getElementById('submitBtn').innerHTML = '<i class="fas fa-plus"></i> Add Customer';
    }

    editCustomer(index) {
        const customer = this.customers[index];
        
        document.getElementById('name').value = customer.name;
        document.getElementById('email').value = customer.email;
        document.getElementById('phone').value = customer.phone;
        document.getElementById('company').value = customer.company;
        
        this.editingIndex = index;
        document.getElementById('submitBtn').innerHTML = '<i class="fas fa-save"></i> Save Changes';
        
        // Scroll to form
        document.querySelector('.form-section').scrollIntoView({ behavior: 'smooth' });
        this.showToast('Now editing customer: ' + customer.name, 'warning');
    }

    deleteCustomer(index) {
        const customerName = this.customers[index].name;
        
        if (confirm(`Are you sure you want to delete ${customerName}?`)) {
            this.customers.splice(index, 1);
            this.saveToLocalStorage();
            this.displayCustomers();
            this.showToast(`Customer ${customerName} deleted successfully`, 'success');
            this.animateDelete();
        }
    }

    viewCustomer(index) {
        const customer = this.customers[index];
        const modal = document.getElementById('customerModal');
        const modalBody = document.getElementById('modalBody');
        
        modalBody.innerHTML = `
            <div class="customer-details">
                <div class="detail-header">
                    <h3>${customer.name}</h3>
                    <span class="status-badge status-active">Active</span>
                </div>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label><i class="fas fa-envelope"></i> Email</label>
                        <p>${customer.email}</p>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-phone"></i> Phone</label>
                        <p>${customer.phone}</p>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-building"></i> Company</label>
                        <p>${customer.company}</p>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-calendar"></i> Added On</label>
                        <p>${new Date(customer.createdAt).toLocaleDateString()}</p>
                    </div>
                </div>
                <div class="modal-actions">
                    <button class="primary-btn" onclick="crm.editCustomer(${index}); crm.closeModal();">
                        <i class="fas fa-edit"></i> Edit Customer
                    </button>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    closeModal() {
        document.getElementById('customerModal').style.display = 'none';
    }

    handleSearch(searchTerm) {
        if (!searchTerm) {
            this.displayCustomers();
            return;
        }
        
        const filtered = this.customers.filter(customer =>
            customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
            customer.company.toLowerCase().includes(searchTerm.toLowerCase())
        );
        
        this.displayCustomers(filtered);
    }

    clearSearch() {
        document.getElementById('searchInput').value = '';
        this.displayCustomers();
    }

    handleSort(sortValue) {
        const [field, direction] = sortValue.split('-');
        
        const sorted = [...this.customers].sort((a, b) => {
            const aValue = a[field].toLowerCase();
            const bValue = b[field].toLowerCase();
            
            if (direction === 'asc') {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });
        
        this.displayCustomers(sorted);
    }

    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.customer-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            this.toggleCustomerSelection(checkbox);
        });
    }

    toggleCustomerSelection(checkbox) {
        const index = parseInt(checkbox.dataset.index);
        
        if (checkbox.checked) {
            this.selectedCustomers.add(index);
        } else {
            this.selectedCustomers.delete(index);
        }
        
        this.updateSelectedCount();
    }

    updateSelectedCount() {
        document.getElementById('selectedCount').textContent = 
            `${this.selectedCustomers.size} selected`;
    }

    bulkDelete() {
        if (this.selectedCustomers.size === 0) {
            this.showToast('Please select customers to delete', 'warning');
            return;
        }
        
        if (confirm(`Delete ${this.selectedCustomers.size} selected customers?`)) {
            // Convert to array and sort in descending order to avoid index issues
            const indices = Array.from(this.selectedCustomers).sort((a, b) => b - a);
            
            indices.forEach(index => {
                this.customers.splice(index, 1);
            });
            
            this.selectedCustomers.clear();
            this.saveToLocalStorage();
            this.displayCustomers();
            this.showToast(`Deleted ${indices.length} customers successfully`, 'success');
        }
    }

    exportData() {
        const dataStr = JSON.stringify(this.customers, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `crm-customers-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        this.showToast('Data exported successfully!', 'success');
    }

    importData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        
        input.onchange = e => {
            const file = e.target.files[0];
            const reader = new FileReader();
            
            reader.onload = event => {
                try {
                    const importedData = JSON.parse(event.target.result);
                    
                    if (Array.isArray(importedData)) {
                        this.customers = importedData;
                        this.saveToLocalStorage();
                        this.displayCustomers();
                        this.showToast('Data imported successfully!', 'success');
                    } else {
                        throw new Error('Invalid file format');
                    }
                } catch (error) {
                    this.showToast('Error importing file. Please check the format.', 'error');
                }
            };
            
            reader.readAsText(file);
        };
        
        input.click();
    }

    refreshData() {
        this.displayCustomers();
        this.showToast('Data refreshed!', 'success');
    }

    toggleForm() {
        const form = document.getElementById('customerForm');
        const toggleIcon = document.getElementById('toggleForm').querySelector('i');
        
        form.classList.toggle('form-expanded');
        
        if (form.classList.contains('form-expanded')) {
            toggleIcon.className = 'fas fa-chevron-up';
        } else {
            toggleIcon.className = 'fas fa-chevron-down';
        }
    }

    updateStats() {
        document.getElementById('totalCustomers').textContent = this.customers.length;
        
        const uniqueCompanies = new Set(this.customers.map(c => c.company)).size;
        document.getElementById('uniqueCompanies').textContent = uniqueCompanies;
        
        document.getElementById('customerCount').textContent = `Total Customers: ${this.customers.length}`;
    }

    highlightText(text) {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        if (!searchTerm) return text;
        
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
    }

    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        const themeIcon = document.querySelector('#themeBtn i');
        themeIcon.className = this.currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Remove toast after 4 seconds
        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    hideLoader() {
        setTimeout(() => {
            document.getElementById('loader').classList.add('hidden');
        }, 1000);
    }

    animateAdd() {
        const rows = document.querySelectorAll('#customerList tr');
        if (rows.length > 0) {
            const lastRow = rows[rows.length - 1];
            lastRow.style.animation = 'pulse 0.6s ease';
            setTimeout(() => lastRow.style.animation = '', 600);
        }
    }

    animateDelete() {
        // Add any delete animation here
    }

    saveToLocalStorage() {
        localStorage.setItem('customers', JSON.stringify(this.customers));
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    mark {
        background-color: #ffeb3b;
        color: #000;
        padding: 0.1rem 0.2rem;
        border-radius: 2px;
    }
    
    .customer-details {
        padding: 1rem 0;
    }
    
    .detail-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .detail-grid {
        display: grid;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .detail-item label {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
    }
    
    .detail-item p {
        font-size: 1.1rem;
        color: var(--text-primary);
        margin: 0;
    }
    
    .modal-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }
`;
document.head.appendChild(style);

// Initialize CRM when DOM is loaded
let crm;
document.addEventListener('DOMContentLoaded', () => {
    crm = new CRM();
});

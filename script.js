// Ultra-simple version - replace everything in script.js with this
let customers = JSON.parse(localStorage.getItem('customers')) || [];

function displayCustomers() {
    const tbody = document.getElementById('customerList');
    tbody.innerHTML = '';
    
    customers.forEach((customer, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${customer.name}</td>
            <td>${customer.email}</td>
            <td>${customer.phone}</td>
            <td>${customer.company}</td>
            <td>
                <button onclick="editCustomer(${index})">Edit</button>
                <button onclick="deleteCustomer(${index})" style="background:red;color:white;">DELETE</button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    document.getElementById('customerCount').textContent = `Total: ${customers.length}`;
}

function deleteCustomer(index) {
    console.log('DELETE CLICKED - Index:', index);
    if (confirm('Really delete?')) {
        customers.splice(index, 1);
        localStorage.setItem('customers', JSON.stringify(customers));
        displayCustomers();
        alert('Deleted!');
    }
}

function editCustomer(index) {
    const customer = customers[index];
    document.getElementById('name').value = customer.name;
    document.getElementById('email').value = customer.email;
    document.getElementById('phone').value = customer.phone;
    document.getElementById('company').value = customer.company;
    // Simple edit implementation
}

document.getElementById('customerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const newCustomer = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        company: document.getElementById('company').value
    };
    customers.push(newCustomer);
    localStorage.setItem('customers', JSON.stringify(customers));
    displayCustomers();
    this.reset();
});

// Initial display
displayCustomers();
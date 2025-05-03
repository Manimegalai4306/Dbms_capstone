from flask import Flask, render_template, request, redirect, url_for,flash
from db_connection import get_db_connection
from datetime import date
import mysql.connector

app = Flask(__name__)



# Home route
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add-sale', methods=['POST'])
def add_sale():
    sale_id = int(request.form['sale_id'])
    date = request.form['date']
    customer_id = int(request.form['customer_id'])
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    # Calculate total amount based on product price
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT Price FROM Products WHERE Product_ID = %s", (product_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        return "Invalid Product ID", 400

    price = result[0]
    total_amount = price * quantity

    cursor.execute('''
        INSERT INTO Sales (Sale_ID, Date, Customer_ID, Product_ID, Quantity, Total_Amount)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (sale_id, date, customer_id, product_id, quantity, total_amount))

    connection.commit()
    cursor.close()
    return redirect(url_for('sales'))


@app.route('/sales')
def sales():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Sales")
    sales = cursor.fetchall()

    # Auto-increment behavior for Sale_ID
    cursor.execute("SELECT MAX(Sale_ID) FROM Sales")
    max_id = cursor.fetchone()[0]
    next_sale_id = (max_id or 0) + 1

    cursor.close()
    return render_template('sales.html', sales=sales, next_sale_id=next_sale_id)



# Route to display all customers
@app.route('/customers')
def customers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()

    # Get next customer ID
    cur.execute("SELECT MAX(customer_id) FROM customers")
    max_id = cur.fetchone()[0]
    next_id = (max_id + 1) if max_id else 1

    cur.close()
    conn.close()
    return render_template('customers.html', customers=customers, next_customer_id=next_id)

# Route to add a new customer
@app.route('/add_customer', methods=['POST'])
def add_customer():
    customer_id = request.form['customer_id']
    name = request.form['name']
    email = request.form['email']
    contact_no = request.form['contact_no']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers (customer_id, name, email, contact_no)
        VALUES (%s, %s, %s, %s)
    """, (customer_id, name, email, contact_no))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('customers'))

# Route to show edit form
@app.route('/edit_customer/<int:customer_id>')
def edit_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
    customer = cur.fetchone()
    cur.execute("SELECT * FROM customers")
    customers = cur.fetchall()

    # For consistent form toggling
    cur.execute("SELECT MAX(customer_id) FROM customers")
    max_id = cur.fetchone()[0]
    next_id = (max_id + 1) if max_id else 1

    cur.close()
    conn.close()

    if customer:
        return render_template('edit_customer.html', customer=customer, customers=customers, next_customer_id=next_id)
    else:
        return "Customer not found", 404

# Route to update customer
@app.route('/update_customer/<int:customer_id>', methods=['POST'])
def update_customer(customer_id):
    name = request.form['name']
    email = request.form['email']
    contact_no = request.form['contact_no']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE customers
        SET name = %s, email = %s, contact_no = %s
        WHERE customer_id = %s
    """, (name, email, contact_no, customer_id))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('customers'))



@app.route('/employees')
def employees_list():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()

    # Calculate the next employee ID (if needed)
    cursor.execute("SELECT MAX(employee_id) FROM employees")
    max_id = cursor.fetchone()[0]
    next_employee_id = (max_id or 0) + 1

    cursor.close()
    conn.close()

    return render_template('employees.html', employees=employees, next_employee_id=next_employee_id)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    employee_id = request.form['employee_id']
    name = request.form['name']
    position = request.form['position']
    salary = request.form['salary']
    contact_no = request.form['contact_no']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees (employee_id, name, position, salary, contact_no) VALUES (%s, %s, %s, %s, %s)",
        (employee_id, name, position, salary, contact_no)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('employees_list'))

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('employees_list'))

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        salary = request.form['salary']
        contact_no = request.form['contact_no']

        cursor.execute("""
            UPDATE employees
            SET name = %s, position = %s, salary = %s, contact_no = %s
            WHERE employee_id = %s
        """, (name, position, salary, contact_no, employee_id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('employees_list'))

    else:
        cursor.execute("SELECT * FROM employees WHERE employee_id = %s", (employee_id,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_employee.html', employee=employee)

@app.route('/update_employee/<int:employee_id>', methods=['GET', 'POST'])
def update_employee(employee_id):
    conn = get_db_connection()  # Get database connection
    cursor = conn.cursor()  # Create cursor object

    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        salary = request.form['salary']
        contact_no = request.form['contact_no']
        
        # Update query using the cursor
        cursor.execute('''
            UPDATE employees
            SET name = %s, position = %s, salary = %s, contact_no = %s
            WHERE employee_id = %s
        ''', (name, position, salary, contact_no, employee_id))
        conn.commit()  # Commit changes to the database
        cursor.close()  # Close the cursor
        conn.close()  # Close the connection
        return redirect(url_for('employees_list'))  # Redirect to the employee list

    # If it's a GET request, retrieve the employee details
    cursor.execute('SELECT * FROM employees WHERE employee_id = %s', (employee_id,))
    employee = cursor.fetchone()
    cursor.close()  # Close the cursor
    conn.close()  # Close the connection

    if employee:
        return render_template('edit_employee.html', employee=employee)
    else:
        return 'Employee not found', 404


@app.route('/take_order', methods=['GET', 'POST'])
def take_order():
    if request.method == 'POST':
        # Handle the form submission
        product_id = request.form['product_id']
        customer_id = request.form['customer_id']
        quantity = request.form['quantity']
        sale_date = request.form['sale_date']

        # Insert order data into the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO orders (Product_ID, Customer_ID, Quantity, Sale_Date)
            VALUES (%s, %s, %s, %s)
        """, (product_id, customer_id, quantity, sale_date))
        connection.commit()
        cursor.close()
        connection.close()

        return 'Order placed successfully!'

    else:
        # Fetch products and customers for the dropdowns
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch products
        cursor.execute("SELECT Product_ID, CONCAT(Brand, ' ', Model) AS Name FROM Products")
        products = cursor.fetchall()

        # Fetch customers
        cursor.execute("SELECT Customer_ID, Name FROM Customers")
        customers = cursor.fetchall()

        cursor.close()
        connection.close()

        # Render the HTML page with products and customers data
        return render_template('take_order.html', products=products, customers=customers)

@app.route('/view_orders', methods=['GET'])
def view_orders():
    # Fetch orders from the database
    connection = get_db_connection()
    cursor = connection.cursor()

    # Fetch order details
    cursor.execute("""
        SELECT orders.Order_ID, 
               products.Brand, 
               products.Model, 
               customers.Name AS Customer_Name, 
               orders.Quantity, 
               orders.Sale_Date
        FROM orders
        JOIN products ON orders.Product_ID = products.Product_ID
        JOIN customers ON orders.Customer_ID = customers.Customer_ID
    """)
    orders = cursor.fetchall()

    cursor.close()
    connection.close()

    # Render the orders page and pass the orders data to it
    return render_template('view_orders.html', orders=orders)



@app.route('/add-product', methods=['POST'])
def add_product():
    product_id = int(request.form['product_id'])  # explicitly passed now
    brand = request.form['brand']
    model = request.form['model']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    ram = request.form['ram']
    storage = request.form['storage']
    color = request.form['color']
    processor = request.form['processor']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO Products (Product_ID, Brand, Model, Price, Stock, RAM, Storage, Color, Processor)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (product_id, brand, model, price, stock, ram, storage, color, processor))
    connection.commit()
    cursor.close()

    return redirect(url_for('products'))




@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    conn = get_db_connection()
    cursor = conn.cursor()

    supplier_id = request.form['supplier_id']
    name = request.form['name']
    contact_no = request.form['contact_no']
    email = request.form['email']
    address = request.form['address']

    # Insert into database
    cursor.execute("""
        INSERT INTO suppliers (supplier_id, name, contact_no, email, address)
        VALUES (%s, %s, %s, %s, %s)
    """, (supplier_id, name, contact_no, email, address))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('suppliers'))

@app.route('/suppliers')
def suppliers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM suppliers")
    suppliers_list = cursor.fetchall()

    cursor.execute("SELECT MAX(supplier_id) FROM suppliers")
    max_id = cursor.fetchone()[0]
    next_supplier_id = (max_id or 0) + 1  # If no suppliers yet, start from 1

    cursor.close()
    conn.close()

    return render_template('suppliers.html', suppliers=suppliers_list, next_supplier_id=next_supplier_id)


@app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        contact_no = request.form['contact_no']
        email = request.form['email']
        address = request.form['address']

        cursor.execute("""
            UPDATE suppliers
            SET name = %s, contact_no = %s, email = %s, address = %s
            WHERE supplier_id = %s
        """, (name, contact_no, email, address, supplier_id))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('suppliers'))

    # GET method - fetch existing supplier data
    cursor.execute("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    supplier = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_supplier.html', supplier=supplier)

@app.route('/delete_supplier/<int:supplier_id>')
def delete_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('suppliers'))
  



# Route to display and add products
@app.route('/products', methods=['GET', 'POST'])
def products():
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Fetch all products
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()

        # Fetch next available Product_ID
        cursor.execute("SELECT MAX(Product_ID) + 1 FROM Products")
        next_product_id = cursor.fetchone()[0]  # Assuming this fetches the next ID

        if request.method == 'POST':
            product_data = {
                "product_id": request.form['product_id'],
                "brand": request.form['brand'],
                "model": request.form['model'],
                "price": request.form['price'],
                "stock": request.form['stock'],
                "ram": request.form['ram'],
                "storage": request.form['storage'],
                "color": request.form['color'],
                "processor": request.form['processor']
            }

            # Insert new product into the Products table
            cursor.execute('''
                INSERT INTO Products (Product_ID, Brand, Model, Price, Stock, RAM, Storage, Color, Processor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (product_data["product_id"], product_data["brand"], product_data["model"],
                  product_data["price"], product_data["stock"], product_data["ram"],
                  product_data["storage"], product_data["color"], product_data["processor"]))

            connection.commit()
            return redirect(url_for('products'))

        cursor.close()
        connection.close()
        return render_template('products.html', products=products, next_product_id=next_product_id)

    except Exception as e:
        print(f"Error: {e}")  # Log error for debugging
        return "An error occurred while fetching the products."


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        print(f"[DEBUG] Received product_id to delete: {product_id}")
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute deletion
        cursor.execute("DELETE FROM Products WHERE Product_ID = %s", (product_id,))
        print(f"[DEBUG] Rows deleted: {cursor.rowcount}")

        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Error deleting product: {e}")
    return redirect(url_for('products'))



if __name__ == '__main__':
    app.run(debug=True)

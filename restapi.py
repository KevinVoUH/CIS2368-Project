# Library System REST API - Sprint 1
import flask
from flask import jsonify, request
from sql import DBconnection, execute_read_query, execute_update_query
import creds
from datetime import datetime
import hashlib  # for password hashing

app = flask.Flask(__name__)
app.config['DEBUG'] = True

# Initialize DB connection
mycreds = creds.myCreds()
mycon = DBconnection(mycreds.hostname, mycreds.username, mycreds.password, mycreds.database)

@app.route('/')
def home():
    return "<h1>Welcome to the Library System API</h1>"

# ---------- BOOKS ----------

@app.route('/api/books', methods=['GET'])
def get_books():
    sql = "SELECT * FROM books"
    results = execute_read_query(mycon, sql)
    return jsonify(results)

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    sql = "INSERT INTO books (title, author, genre, status) VALUES ('%s', '%s', '%s', '%s')" % (
        data['title'], data['author'], data['genre'], data['status'])
    execute_update_query(mycon, sql)
    return "Book added successfully"

@app.route('/api/books', methods=['PUT'])
def update_book():
    data = request.get_json()
    sql = "UPDATE books SET title='%s', author='%s', genre='%s', status='%s' WHERE id=%s" % (
        data['title'], data['author'], data['genre'], data['status'], data['id'])
    execute_update_query(mycon, sql)
    return "Book updated successfully"

@app.route('/api/books', methods=['DELETE'])
def delete_book():
    data = request.get_json()
    sql = "DELETE FROM books WHERE id = %s" % (data['id'])
    execute_update_query(mycon, sql)
    return "Book deleted successfully"

# ---------- CUSTOMERS ----------

@app.route('/api/customers', methods=['GET'])
def get_customers():
    sql = "SELECT id, firstname, lastname, email FROM customers"
    results = execute_read_query(mycon, sql)
    return jsonify(results)

@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    hashed = hashlib.sha256(data['password'].encode()).hexdigest()
    sql = "INSERT INTO customers (firstname, lastname, email, passwordhash) VALUES ('%s', '%s', '%s', '%s')" % (
        data['firstname'], data['lastname'], data['email'], hashed)
    execute_update_query(mycon, sql)
    return "Customer added successfully"

@app.route('/api/customers', methods=['PUT'])
def update_customer():
    data = request.get_json()
    hashed = hashlib.sha256(data['password'].encode()).hexdigest()
    sql = "UPDATE customers SET firstname='%s', lastname='%s', email='%s', passwordhash='%s' WHERE id=%s" % (
        data['firstname'], data['lastname'], data['email'], hashed, data['id'])
    execute_update_query(mycon, sql)
    return "Customer updated successfully"

@app.route('/api/customers', methods=['DELETE'])
def delete_customer():
    data = request.get_json()
    sql = "DELETE FROM customers WHERE id = %s" % (data['id'])
    execute_update_query(mycon, sql)
    return "Customer deleted successfully"

# ---------- BORROWING ----------

@app.route('/api/borrowings', methods=['GET'])
def get_borrowings():
    sql = "SELECT * FROM borrowingrecords"
    results = execute_read_query(mycon, sql)
    return jsonify(results)

@app.route('/api/borrowings', methods=['POST'])
def create_borrowing():
    data = request.get_json()
    bookid = data['bookid']
    customerid = data['customerid']
    borrowdate = data['borrowdate']

    # Check book availability
    check_book = "SELECT status FROM books WHERE id = %s" % (bookid)
    book_result = execute_read_query(mycon, check_book)
    if not book_result or book_result[0]['status'] != 'available':
        return "Book not available", 400

    # Check if customer already has a book
    check_customer = "SELECT * FROM borrowingrecords WHERE customerid = %s AND returndate IS NULL" % (customerid)
    result = execute_read_query(mycon, check_customer)
    if result:
        return "Customer already has a borrowed book", 400

    # Proceed with borrowing
    sql = "INSERT INTO borrowingrecords (bookid, customerid, borrowdate) VALUES (%s, %s, '%s')" % (
        bookid, customerid, borrowdate)
    execute_update_query(mycon, sql)

    update_book = "UPDATE books SET status='unavailable' WHERE id=%s" % (bookid)
    execute_update_query(mycon, update_book)

    return "Borrowing recorded successfully"

@app.route('/api/borrowings', methods=['PUT'])
def return_borrowing():
    data = request.get_json()
    borrow_id = data['id']
    returndate = data['returndate']

    # Get borrowdate and bookid
    sql = "SELECT borrowdate, bookid FROM borrowingrecords WHERE id = %s" % (borrow_id)
    record = execute_read_query(mycon, sql)
    if not record:
        return "Borrowing record not found", 404

    borrowdate = record[0]['borrowdate']
    bookid = record[0]['bookid']

    # Calculate late fee
    delta = (datetime.strptime(returndate, "%Y-%m-%d").date() - borrowdate).days
    late_fee = max(0, delta - 10)
    
    update_borrowing = "UPDATE borrowingrecords SET returndate='%s', late_fee=%s WHERE id=%s" % (
        returndate, late_fee, borrow_id)
    execute_update_query(mycon, update_borrowing)

    update_book = "UPDATE books SET status='available' WHERE id=%s" % (bookid)
    execute_update_query(mycon, update_book)

    return jsonify({"message": "Book returned", "late_fee": late_fee})

# Run the app
app.run()

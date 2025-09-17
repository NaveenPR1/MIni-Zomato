from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# Create a MySQL connection
def create_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # replace with your MySQL username
        password='root',  # replace with your MySQL password
        database='zomato'
    )

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Place an order (POST) - Updated to insert into orders and order_items
@app.route('/place_order', methods=['POST'])
def place_order():
    cursor = None
    connection = None
    try:
        order_data = request.get_json()
        cart = order_data['cart']
        address = order_data['address']

        if not cart or not address:
            return jsonify({"error": "Cart is empty or address is missing."}), 400

        connection = create_connection()
        cursor = connection.cursor()

        user_id = 1  # for testing, you can update dynamically later

        # 1️⃣ Insert into orders table
        cursor.execute(
            "INSERT INTO orders (user_id, delivery_address) VALUES (%s, %s)",
            (user_id, address)
        )
        connection.commit()
        order_id = cursor.lastrowid  # get the auto-generated order_id

        # 2️⃣ Insert each item into order_items table
        for item in cart:
            item_name = item['name']
            quantity = item['quantity']

            cursor.execute("SELECT item_id, price FROM items WHERE item_name = %s", (item_name,))
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": f"Item {item_name} not found."}), 400

            item_id, price = result
            cursor.execute(
                "INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, item_id, quantity, price)
            )

        connection.commit()
        return jsonify({"message": "Order placed successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Get all orders (GET)
@app.route('/orders', methods=['GET'])
def get_orders():
    cursor = None
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()

        return jsonify({"orders": orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)

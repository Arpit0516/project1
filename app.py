from flask import Flask, render_template, request, jsonify
import serial
import time

app = Flask(__name__)

# Initialize Serial Connection to Arduino
def initialize_serial(port, baudrate=9600, timeout=1):
    try:
        arduino = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Allow Arduino time to initialize
        print(f"Arduino connected successfully on {port}.")
        return arduino
    except serial.SerialException as e:
        print(f"Error connecting to Arduino on {port}: {e}")
        return None
arduino = initialize_serial('COM4')
# Sample product data
products = {
    'VJT0244': {'Product ID': 'VJT0244', 'Product Name': 'Product 1', 'Product Description': 'This is product 1', 'Price': 100, 'Weight': 30},
    'DEF456': {'Product ID': 'DEF456', 'Product Name': 'Product 2', 'Product Description': 'This is product 2', 'Price': 200, 'Weight': 2.0},
    'GHI789': {'Product ID': 'GHI789', 'Product Name': 'Product 3', 'Product Description': 'This is product 3', 'Price': 300, 'Weight': 1.8},
}

cart = []  # Cart to store added products

@app.route('/')
def index():
    return render_template('index.html', products=products, cart=cart)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    scanned_code = request.form['scanned_code']
    if scanned_code in products:
        cart.append(products[scanned_code])
        # Send 'C' command to Arduino
        send_command_to_arduino('C')
        return jsonify({'cart': cart})
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():
    item_id = request.form['item_id']
    for item in cart:
        if item['Product ID'] == item_id:
            cart.remove(item)
            # Send '0' command to Arduino
            send_command_to_arduino('0')
            return jsonify({'cart': cart})
    return jsonify({'error': 'Item not found in cart'}), 404

def send_command_to_arduino(command):
    """Send a command to the Arduino and handle errors."""
    global arduino
    if arduino and arduino.is_open:
        try:
            arduino.write(command.encode())  # Send command to Arduino
            print(f"Sent '{command}' to Arduino.")
            time.sleep(0.1)  # Small delay for processing
        except serial.SerialException as e:
            print(f"Error sending command to Arduino: {e}")
    else:
        print("Arduino connection not open.")

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    return 'Payment processing...'

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # Close the Arduino connection on shutdown
        if arduino and arduino.is_open:
            arduino.close()
            print("Arduino connection closed.")

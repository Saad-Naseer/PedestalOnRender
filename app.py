from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import serial.tools.list_ports
from pedestel import Pedestal
import gevent
import gevent.monkey
gevent.monkey.patch_all()
GEVENT_SUPPORT=True

class FlaskSocketIOApp:
    def __init__(self, host='0.0.0.0', port=5000):
        # Initialize Flask app
        self.app = Flask(__name__, static_folder='static')
        CORS(self.app)  # Enable CORS for all routes

        # Initialize SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")  # Allow connections from all origins

        # Host and port for the server
        self.host = host
        self.port = port
        self.pedestal = None

        # Set up routes and events
        self._setup_routes()
        self._setup_events()

    def _setup_routes(self):
        # Route to serve the webpage
        @self.app.route('/')
        def index():
            return render_template('index.html')

    def _setup_events(self):
        # WebSocket event to handle communication with JavaScript client
        @self.socketio.on('get_usb_devices')
        def handle_get_usb_devices():
            devices = self.list_usb_devices()
            emit('usb_devices', devices)

        @self.socketio.on('connect_to_device')
        def handle_connect_to_device(data):
            device = data['device']
            response = self.connect_to_device(device)
            emit('connection_response', response)
    
        @self.socketio.on('send_data')
        def handle_send_data(data):
            # Extract the device and message from the data sent from the client
            if data['message'] == 'up':
                self.pedestal.moveUp()
            if data['message'] == 'down':
                self.pedestal.moveDown()
            if data['message'] == 'reset':
                self.pedestal.moveToHeight_MM(height_mm=300)
        
        # Handle client disconnect
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected")
            # Clean up USB or serial connection
            self.disconnect_device()

    def list_usb_devices(self):
        """List connected USB devices."""
        ports = list(serial.tools.list_ports.comports())
        devices = []
        for port in ports:
            devices.append({'device': port.device, 'name': port.description})
        return devices

    def connect_to_device(self, device):
        """Handle sending data to a selected USB device."""
        print(f"Received data: {device}")
        try:
            SERIAL_PORT = device
            BAUD_RATE = 9600
            DATA_BITS = 8
            STOP_BITS = 1
            PARITY = serial.PARITY_NONE
            if self.pedestal is None:
                self.pedestal = Pedestal(SERIAL_PORT, BAUD_RATE, DATA_BITS, STOP_BITS, PARITY)
            return {'status': 'success', 'message': 'connected'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    

    def run(self):
        """Run the Flask app with SocketIO."""
        self.socketio.run(self.app, host=self.host, port=self.port)
    
    def disconnect_device(self):
        """Disconnect the current USB/serial connection."""
        if self.pedestal:
            try:
                # Close the serial connection if it exists
                self.pedestal.close_serial()
                print("USB/Serial connection closed")
            except Exception as e:
                print(f"Error while closing connection: {str(e)}")
            finally:
                self.pedestal = None

app_instance = FlaskSocketIOApp()
app = app_instance.app

if __name__ == '__main__':
    #app = FlaskSocketIOApp()
    app_instance.run()

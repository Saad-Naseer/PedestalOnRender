const socket = io.connect("http//localhost:5000");

// Store whether the device is successfully connected
let deviceConnected = false;
let selectedDevice = null;
let intervalId = null;

// Function to get the list of USB devices
function getUsbDevices() {
    socket.emit('get_usb_devices');
}

// Listen for USB devices from the server
socket.on('usb_devices', function(devices) {
    const usbListDiv = document.getElementById('usb-list');
    usbListDiv.innerHTML = '';

    if (devices.length === 0) {
        usbListDiv.innerHTML = '<p>No USB devices found.</p>';
        return;
    }

    devices.forEach(device => {
        const deviceDiv = document.createElement('div');
        deviceDiv.classList.add('device-item');
        const deviceName = document.createElement('span');
        deviceName.textContent = `${device.name} (${device.device})`;
        const connectButton = document.createElement('button');
        connectButton.textContent = 'Connect';
        connectButton.onclick = () => selectDevice(device.device);
        deviceDiv.appendChild(deviceName);
        deviceDiv.appendChild(connectButton);
        usbListDiv.appendChild(deviceDiv);
    });
});

// Select a USB device
function selectDevice(device) {
    selectedDevice = device;
    document.getElementById('send-message-section').style.display = 'block';

    // Request server to connect to the device (no message needed)
    socket.emit('connect_to_device', { device: selectedDevice, message: 'connect' });
}

// Listen for responses from the server
socket.on('connection_response', function(response) {
    console.log(response);
    const responseDiv = document.getElementById('response');
    if (response.status === 'success') {
        responseDiv.className = 'success';
        responseDiv.textContent = response.device;
        if (response.message === 'connected') {
            deviceConnected = true;
            document.getElementById('upButton').disabled = false;
            document.getElementById('downButton').disabled = false;
            document.getElementById('resetButton').disabled = false;
            console.log(deviceConnected);
        }
    } else {
        responseDiv.className = 'error';
        responseDiv.textContent = `Error: ${response.message}`;
        deviceConnected = false;
    }
});

// Start sending data (Up or Down)
function startSendingData(direction) {
    if (!deviceConnected || !selectedDevice) {
        alert('Please ensure the device is connected first.');
        return;
    }

    const command = direction === 'up' ? 'up' : 'down';
    const data = {
        device: selectedDevice,
        message: command
    };

    // Start interval to simulate sending data every 2ms
    intervalId = setInterval(() => {
        console.log(`Sending ${command} to device: ${selectedDevice}`);
        socket.emit('send_data', data);  // 'send_data' is the event name for your server to listen to
    }, 2);
}

// Stop sending data
function stopSendingData() {
    if (intervalId) {
        clearInterval(intervalId); // Stop sending data
        intervalId = null;
    }
}

// Reset the communication
function resetCommunication() {
    if (!deviceConnected || !selectedDevice) {
        alert('Please ensure the device is connected first.');
        return;
    }

    const data = {
        device: selectedDevice,
        message: 'reset'
    };
    // Optionally, reset any ongoing data or state
    console.log('Reset communication with device');
    socket.emit('send_data', data);  // 'send_data' is the event name for your server to listen to
}

// Handle socket disconnection
socket.on('disconnect', function() {
    
    // Perform necessary cleanup actions
    if (deviceConnected) {
        stopSendingData(); // Stop any ongoing data transmissions
        deviceConnected = false;
        selectedDevice = null;

        // Inform the server to close the USB/serial connection
        socket.emit('disconnect', 1);

        // Disable buttons
        document.getElementById('upButton').disabled = true;
        document.getElementById('downButton').disabled = true;
        document.getElementById('resetButton').disabled = true;

        // Display disconnected message
        const responseDiv = document.getElementById('response');
        responseDiv.className = 'error';
        responseDiv.textContent = 'Disconnected from device.';
    }
});
// Automatically fetch USB devices when the page loads
window.onload = getUsbDevices;

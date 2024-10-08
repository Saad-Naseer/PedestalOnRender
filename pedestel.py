import serial
import time


class Pedestal:
    def __init__(self, serialPort, baudRate, dataBits, stopBits, parity):        
        # Initialize the serial connection
        self.ser = serial.Serial(serialPort, baudRate, bytesize=dataBits, stopbits=stopBits, parity=parity)

    def moveUp(self):
        command =  bytes([0xF1, 0xF1, 0x01, 0x00, 0x01, 0x7E])
        self.send_command(command=command)
    
    def moveDown(self):
        command = bytes([0xF1, 0xF1, 0x02, 0x00, 0x02, 0x7E])
        self.send_command(command=command)
    
    def release(self):
        command = bytes([0xF1, 0xF1, 0x0A, 0x00, 0x0A, 0x7E])
        self.send_command(command=command)
    
    def quickStop(self):
        command = bytes([0xF1, 0xF1, 0x2B, 0x00, 0x2B, 0x7E])
        self.send_command(command=command)
    
    def moveToHeight_MM(self, height_mm):
        """
        Create the protocol command based on the given height in millimeters.
        
        :param height_mm: The target height in millimeters
        :return: The full command as a list of bytes
        """
        # Convert height to hexadecimal and split into two bytes
        height_hex = height_mm.to_bytes(2, byteorder='big')
        goal_h = height_hex[0]
        goal_l = height_hex[1]
        
        # Protocol parts
        start_frame = [0xF1, 0xF1]
        command_id = [0x1B]
        data_length = [0x02]
        data = [goal_h, goal_l]
        end_frame = [0x7E]
        
        # Data to calculate checksum (excluding start and end frames)
        data_for_checksum = command_id + data_length + data
        
        # Calculate checksum
        checksum = self.calculate_checksum(data_for_checksum)
        
        # Complete command
        command = start_frame + command_id + data_length + data + [checksum] + end_frame
        
        self.send_command(command=command)

    def calculate_checksum(self, data):
        """
        Calculate the checksum by summing all bytes in the data list, 
        then taking the lower 8 bits of the result.

        :param data: A list of integers representing the bytes of the command
        :return: The checksum as an integer
        """
        # Sum all the bytes in the data list
        checksum = sum(data)
        # Take the lower 8 bits of the sum
        checksum = checksum & 0xFF
        return checksum
    
    def request_height_mm(self):
        command = bytes([0xF1, 0xF1, 0x0E, 0x00, 0x0E, 0x7E])
        self.send_command(command=command)

    def send_command(self, command):
        self.ser.write(command)
        #print(f"Sent command: {command.hex()}")
    
    def read(self):
        if self.ser.in_waiting > 0:
            res = self.ser.read(self.ser.in_waiting)
            # Extract data_h and data_l
            data_h = res[4]
            data_l = res[5]
            
            # Combine data_h and data_l to get height in hexadecimal
            height_hex = (data_h << 8) | data_l
    
            print(f"Received data: {height_hex}")
        else:
            print("No data available")

    def close_serial(self):
        self.ser.close()

def main():
    # Define the command bytes
    pedestal = Pedestal()
    try:
        while True:
        # Example: Sending the upward command
            pedestal.moveToHeight_MM(height_mm=653)
            #pedestal.moveUp()     
            time.sleep(0.2)
            
    finally:
        # Close the serial connection
        pedestal.close_serial()

if __name__=="__main__":
    main()

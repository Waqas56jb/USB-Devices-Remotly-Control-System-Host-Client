import socket
import struct
import time
from pynput.mouse import Controller, Listener, Button

mouse = Controller()

# Enter the IP address of the **host machine**
HOST_IP = "192.168.140.179"  # Change this to your host PC's IP
PORT = 5005  # Must match the host's port

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("✅ Client is controlling the host's mouse...")

def send_mouse_data(x, y, click=0):
    """Send mouse position and click status to the host."""
    data = struct.pack("iib", x, y, click)  # Pack (x, y, click) as bytes
    client.sendto(data, (HOST_IP, PORT))

def on_move(x, y):
    """Send mouse movement data to the host."""
    send_mouse_data(x, y, click=0)

def on_click(x, y, button, pressed):
    """Send click events to the host."""
    if pressed:
        if button == Button.left:
            send_mouse_data(x, y, click=1)  # Left click
        elif button == Button.right:
            send_mouse_data(x, y, click=2)  # Right click

# Start listening to mouse events
with Listener(on_move=on_move, on_click=on_click) as listener:
    listener.join()

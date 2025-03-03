import socket
import struct
import time
import ctypes
from pynput.mouse import Controller as MouseController, Listener as MouseListener, Button
from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key

mouse = MouseController()
keyboard = KeyboardController()

HOST_IP = "192.168.140.179"  # Replace with actual Host IP
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("✅ Requesting control from host...")

client.sendto("REQUEST_CONTROL".encode("utf-8"), (HOST_IP, PORT))
response, _ = client.recvfrom(1024)

if response.decode("utf-8") == "APPROVED":
    print("✅ Control approved! Do you want to disable your local keyboard/mouse? (Y/N): ", end="")
    user_input = input().strip().lower()
    
    disable_local_input = user_input == "y"

    # Disable local keyboard & mouse if chosen
    def disable_input():
        """Disable keyboard & mouse locally (Windows Only)."""
        if disable_local_input:
            ctypes.windll.user32.BlockInput(True)  # Fully disables input on Windows

    def enable_input():
        """Re-enable keyboard & mouse locally."""
        if disable_local_input:
            ctypes.windll.user32.BlockInput(False)

    disable_input()  # Disable input if user agreed

    def send_data(x, y, click=0, key_code=0, key_action=0):
        """Send mouse position, clicks, and key presses to the host."""
        data = struct.pack("iiHhi", x, y, click, key_code, key_action)
        client.sendto(data, (HOST_IP, PORT))

    def on_move(x, y):
        """Send live mouse movement data to the host."""
        send_data(x, y)

    def on_click(x, y, button, pressed):
        """Send mouse click events."""
        click = 1 if button == Button.left else 2 if button == Button.right else 0
        if pressed:
            send_data(x, y, click)

    def on_press(key):
        """Send keyboard press event."""
        try:
            if hasattr(key, 'char') and key.char is not None:
                key_code = ord(key.char)
            elif key in Key.__dict__.values():
                key_code = list(Key.__dict__.values()).index(key) + 128
            else:
                key_code = 0
        except AttributeError:
            key_code = 0

        send_data(mouse.position[0], mouse.position[1], click=0, key_code=key_code, key_action=1)

    def on_release(key):
        """Send keyboard release event."""
        try:
            if hasattr(key, 'char') and key.char is not None:
                key_code = ord(key.char)
            elif key in Key.__dict__.values():
                key_code = list(Key.__dict__.values()).index(key) + 128
            else:
                key_code = 0
        except AttributeError:
            key_code = 0

        send_data(mouse.position[0], mouse.position[1], click=0, key_code=key_code, key_action=0)

    # Start listening for mouse and keyboard events
    with MouseListener(on_move=on_move, on_click=on_click) as mouse_listener, KeyboardListener(on_press=on_press, on_release=on_release) as keyboard_listener:
        try:
            mouse_listener.join()
            keyboard_listener.join()
        except KeyboardInterrupt:
            enable_input()  # Re-enable local keyboard & mouse on exit

else:
    print("❌ Host denied control request.")

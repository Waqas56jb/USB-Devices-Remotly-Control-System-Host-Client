# client.py
import socket
import struct
import time
import ctypes
import threading
from pynput.mouse import Controller as MouseController, Listener as MouseListener, Button
from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key
import keyboard  # For more effective keyboard disabling
import mouse  # For more effective mouse disabling

mouse_controller = MouseController()
keyboard_controller = KeyboardController()

HOST_IP = "192.168.140.179"  # Replace with actual Host IP
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("\u2705 Requesting control from host...")

client.sendto("REQUEST_CONTROL".encode("utf-8"), (HOST_IP, PORT))
response, _ = client.recvfrom(1024)

def block_keyboard_mouse():
    """Function to block keyboard and mouse inputs effectively."""
    keyboard.block_key("esc")  # Block ESC to prevent exits
    keyboard.block_key("alt")  # Block ALT to prevent task switching
    keyboard.block_key("ctrl")  # Block CTRL to prevent shortcuts
    keyboard.block_key("win")  # Block Windows key
    mouse.move(0, 0)  # Keep mouse at (0,0)
    while True:
        mouse.move(0, 0)  # Prevent movement
        time.sleep(0.1)

if response.decode("utf-8") == "APPROVED":
    print("\u2705 Control approved! Disabling local keyboard/mouse...")
    
    ctypes.windll.user32.BlockInput(True)  # Disable input on Windows
    
    # Start blocking thread
    threading.Thread(target=block_keyboard_mouse, daemon=True).start()

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

        send_data(mouse_controller.position[0], mouse_controller.position[1], click=0, key_code=key_code, key_action=1)

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

        send_data(mouse_controller.position[0], mouse_controller.position[1], click=0, key_code=key_code, key_action=0)

    # Start listening for mouse and keyboard events
    with MouseListener(on_move=on_move, on_click=on_click) as mouse_listener, KeyboardListener(on_press=on_press, on_release=on_release) as keyboard_listener:
        try:
            mouse_listener.join()
            keyboard_listener.join()
        except KeyboardInterrupt:
            ctypes.windll.user32.BlockInput(False)  # Re-enable local keyboard & mouse on exit
            keyboard.unhook_all()  # Remove all keyboard hooks
            mouse.unhook_all()  # Remove all mouse hooks

else:
    print("\u274c Host denied control request.")

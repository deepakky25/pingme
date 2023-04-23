# pingme

To test:
1. python3 server.py bring up the server
2. python3 client-led.py to enable the device or raspberry to connect to the server and mark itself active
3. python3 client-app.py to connect the client to the server
4. user can send STATUS command to get list of all active device
5. user can send UPDATE_STATE <device_id> <new_state> to update the active device state

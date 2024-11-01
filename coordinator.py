from flask import Flask, request, jsonify
import requests
import subprocess
import threading
import time

app = Flask(__name__)

# List of server URLs to forward requests to
server_urls = []
max_servers = 5  # Maximum number of servers to run
min_servers = 1  # Minimum number of servers to run
load_threshold = 10  # Load threshold to scale up/down
server_processes = []  # Keep track of server processes

@app.route('/api/data', methods=['POST'])
def handle_request():
    data = request.get_json()  # Get the JSON data from the incoming request

    for url in server_urls:
        try:
            # Forward the request to the server
            response = requests.post(f"{url}/api/data", json=data, verify=False)  # Set verify=False for testing purposes

            if response.status_code == 200:
                return response.json()  # Return the response from the server if successful
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to {url}: {e}")  # Log the error for debugging

    return {'error': 'All servers are down'}, 503  # Return an error if all servers fail

@app.route('/register', methods=['POST'])
def register_server():
    server_url = request.json.get('url')
    if server_url not in server_urls:
        server_urls.append(server_url)
    return jsonify({'message': 'Server registered successfully'}), 200

@app.route('/deregister', methods=['POST'])
def deregister_server():
    server_url = request.json.get('url')
    if server_url in server_urls:
        server_urls.remove(server_url)
    return jsonify({'message': 'Server deregistered successfully'}), 200

def scale_servers():
    while True:
        current_load = get_current_load()  # Implement this function to get the current load
        if current_load > load_threshold and len(server_urls) < max_servers:
            start_new_server()
        elif current_load < load_threshold and len(server_urls) > min_servers:
            stop_last_server()
        time.sleep(5)  # Check every 5 seconds

def start_new_server():
    # Start a new server process
    process = subprocess.Popen(['python3', 'server.py'])
    server_processes.append(process)
    print("Started a new server instance.")

def stop_last_server():
    if server_processes:
        process = server_processes.pop()
        process.terminate()  # Terminate the server process
        print("Stopped a server instance.")

def get_current_load():
    # Placeholder for load calculation logic
    # You can implement your own logic to determine the current load
    return len(server_urls) * 5  # Example: load based on the number of active servers

if __name__ == '__main__':
    threading.Thread(target=scale_servers, daemon=True).start()  # Start the scaling thread
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app on all interfaces

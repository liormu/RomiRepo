from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import os

# Function to load JSON data from a file
def load_json_data(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = 'data'
    file_path = os.path.join(script_dir, data_folder, filename)
    with open(file_path) as file:
        return json.load(file)

# Function to save JSON data to a file
def save_json_data(data, filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = 'data'
    file_path = os.path.join(script_dir, data_folder, filename)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # HTML template for the index page
    
    index_html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Entries List</title>
    </head>
    <body>
        <h1>Entries List</h1>
        <ul>
            {% for entry in entries %}
        </ul>
        <h2>Add New Entry</h2>
        <form action="/add" method="post">
            <label for="name">Name:</label><br>
            <input type="text" id="name" name="name"><br>
            <label for="age">Age:</label><br>
            <input type="text" id="age" name="age"><br><br>
            <input type="submit" value="Add Entry">
        </form>
        <h2>Delete Entry</h2>
        <form action="/delete" method="post">
            <label for="name">Name:</label><br>
            <input type="text" id="name" name="name"><br><br>
            <input type="submit" value="Delete Entry">
        </form>
    </body>
    </html>
    """
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if parsed_url.path == '/data.json':
            data = load_json_data('data.json')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        elif parsed_url.path == '/':
            data = load_json_data('data.json')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Render the HTML template with entries data
            rendered_html = self.index_html_template.replace('{% for entry in entries %}', json.dumps(data) )
            self.wfile.write(rendered_html.encode())
            

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_data)

        if self.path == '/add':
            name = form_data.get('name', [''])[0]
            age = form_data.get('age', [''])[0]
            
            if name and age:
                new_entry = {'name': name, 'age': age}
                data = load_json_data('data.json')
                data.append(new_entry)
                save_json_data(data, 'data.json')
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Bad Request')
        elif self.path == '/delete':
            name = form_data.get('name', [''])[0]
            if name:
                data = load_json_data('data.json')
                data = [entry for entry in data if entry['name'] != name]
                save_json_data(data, 'data.json')
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Bad Request')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

def run():
    print('Starting server...')
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print('Server is running at http://localhost:8000')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

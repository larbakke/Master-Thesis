from microdot import Microdot, Response
from microdot.websocket import WebSocket
from time import sleep

# Create a MicroDot app
app = Microdot()
Response.default_content_type = 'text/html'

# Counter class
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        print(self.count)
        if self.count > 100:
            self.count = 0
        return self.count

# Create an instance of the Counter class
counter = Counter()

# WebSocket route
@app.route('/ws')
def handle_ws(request):
    ws = WebSocket(request)
    while True:
        # Get the current count
        current_count = counter.increment()
        
        # Send the count to the client
        ws.send(str(current_count))
        
        # Wait for a short period before sending the next count
        sleep(1)

# HTML page with WebSocket client
@app.route('/')
def index(request):
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Counter</title>
        <script>
            var ws = new WebSocket('ws://' + window.location.host + '/ws');
            ws.onmessage = function(event) {
                document.getElementById('counter').innerText = event.data;
            };
        </script>
    </head>
    <body>
        <h1>Counter: <span id="counter">0</span></h1>
    </body>
    </html>
    '''

# Start the server
if __name__ == '__main__':
    print('Starting up')
    app.run(host='0.0.0.0', port=80)
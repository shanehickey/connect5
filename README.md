# connect5
Connect 5 Task. First run the Server, then run 2 clients to initiate a game. Ensure all below actions take place at the top level of connect5 directory

# Ensure requirements are installed using pip (preferably in a Virtual Environment)
- pip install -r requirements.txt

# Run Server
- Set the "FLASK_APP" environmental variable equal to "connect_server" (e.g. '$env:FLASK_APP="connect_server"' in Powershell or 'export FLASK_APP="connect_server"' in Linux)
- flask run

# Run Client
- python client.py

# Run Tests
- pytest test_connect.py -v

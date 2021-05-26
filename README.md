# connect5
Connect 5 Task. First run the Server, then run 2 clients to initiate a game.

# Run Server
- cd into connect5 dir
- Set the "FLASK_APP" environmental variable equal to "connect_server" (e.g. '$env:FLASK_APP="connect_server"' in Powershell or 'export FLASK_APP="connect_server"')
- flask run --debugger

# Run Client
- cd into connect5 dir
- python client.py

# Run Tests
- cd into connect5 dir
- pytest test_connect.py -v

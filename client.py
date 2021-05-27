import errors
import requests
import socket
import time


CONNECT5_SERVER = "http://127.0.0.1:5000/"
TURN_POLL_INTERVAL = 1


class Client:
    """Represents a single client used to partake in a game of Connect 5"""

    def __init__(self):
        self.hostname = socket.gethostname()
        self.name = None
        self.symbol = ""
        self.active_player = False

    def set_symbol(self, symbol):
        self.symbol = symbol

    def is_active_player(self):
        return self.active_player

    def set_active_player(self, active):
        self.active_player = active

    def _make_get_request(self, url, data=None):
        try:
            req = requests.get(url)
        except requests.exceptions.RequestException as e:
            reg_err = "Bot registration error: "
            if not e.response:
                reg_err += "No response from server"
            else:
                reg_err += str(e.response.json())
            raise errors.PlayerRegistrationError(reg_err)
        return req

    def _make_post_request(self, url, data=None):
        try:
            req = requests.post(url, json=data)
        except requests.exceptions.RequestException as e:
            reg_err = "Bot registration error: "
            if not e.response:
                reg_err += "No response from server"
            else:
                reg_err += str(e.response.json())
            raise errors.PlayerRegistrationError(reg_err)
        return req

    def print_board(self):
        reg_url = CONNECT5_SERVER + "/board"
        req = self._make_get_request(reg_url)
        if "board" in req.json() and req.json()["board"]:
            print(req.json()["board"])

    def join_game(self):
        """Attempt to join the game"""
        reg_url = CONNECT5_SERVER + "/register"
        player_info = {}

        valid_name = False
        while not valid_name:
            name = input("Please enter name: ")
            player_info["name"] = name

            req = self._make_post_request(reg_url, player_info)
            if "success" in req.json():
                print(req.json()["message"])
                valid_name = req.json()["success"]

        self.name = name
        return req.json()

    def initialise_player_details(self):
        reg_url = CONNECT5_SERVER + "/playerdetails"
        player_info = {"name": self.name}
        req = self._make_post_request(reg_url, player_info)
        self.symbol = req.json()["symbol"]
        return req.json()

    def is_client_active_player(self):
        reg_url = f"{CONNECT5_SERVER}/activeplayer/{self.name}"
        req = self._make_get_request(reg_url)
        return req.json()["active_player"]

    def make_move(self):
        valid_move = False
        while not valid_move:
            column = input(f"It's your turn {self.name}, please enter column (1-9):")

            valid_column = True
            try:
                column_int = int(column)
                # These int values could be obtained from a shared config file between server and client
                if column_int < 1 or column_int > 9:
                    valid_column = False
            except ValueError:
                valid_column = False
            if not valid_column:
                print("Column must be an integer between 1 and 9!")
                continue

            reg_url = CONNECT5_SERVER + "/makemove"
            # Easiest to subtract one from the column value here and use the indices of the 2D array
            # on the server
            move_info = {"column": str(int(column) - 1), "symbol": self.symbol}
            req = self._make_post_request(reg_url, move_info)

            # All attempts to access a key in a dictionary should be wrapped in a try except block
            # looking for KeyErrors or malformed responses
            valid_move = req.json()["success"]
            if not valid_move:
                print(req.json()["reason"])
        return req.json()["winner"]

    def winner_exists(self):
        reg_url = CONNECT5_SERVER + "/winner"
        req = self._make_get_request(reg_url)
        return req.json()["winner"] if "winner" in req.json() else False


if __name__ == "__main__":
    client = Client()
    try:
        # Client checks is it possible for it to join a game
        response = client.join_game()
        if "success" not in response:
            print("Malformed response from the server")
        elif not response["success"]:
            print(response["message"])
        else:
            # Client prompts the server to assign an initial active player (who goes first). At this
            # point the client must wait for a second player
            player_details = client.initialise_player_details()
            client.set_active_player(player_details["active_player"])
            client.set_symbol(player_details["symbol"])

            # While there is not a winner keep playing
            while not client.winner_exists():
                # While you are not the active player keep polling for your turn
                while not client.is_active_player():
                    time.sleep(TURN_POLL_INTERVAL)
                    client.set_active_player(client.is_client_active_player())

                    # If there is a winner decided before you make your turn then you have lost
                    if client.winner_exists():
                        client.print_board()
                        print(f"You lost. Commiserations {client.name}.")
                # If you have not lost then it now it is your turn. If you have lost, the client
                # will exit the loop and the main function finishes
                if not client.winner_exists():
                    client.print_board()
                    client.make_move()

                    # If there is a winner straight after your move then you have won
                    if client.winner_exists():
                        client.print_board()
                        print(f"You won! Congratulations {client.name}.")
                    else:
                        print("Please wait for your turn...")
                    client.set_active_player(False)
    except errors.PlayerRegistrationError as e:
        print(e)

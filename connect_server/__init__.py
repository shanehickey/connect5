import time
from flask import Flask, request

# Rather than global variables a database with SQLAlchemy could be used for persistence
# beyond the current session
global board
global participants

# I'd like to store these constants in a config file that could be shared with the client
FIRST_INDEX = 0
NUM_ROWS = 6
NUM_COLS = 9
NUM_TO_CONNECT = 5
SYMBOL_1 = "X"
SYMBOL_2 = "O"
JOIN_SLEEP = 1


class Player:
    """Represents a single Player that has joined a game.

    Attributes:
        name (str): The display name chosen by the player.
    """

    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def __str__(self):
        return self.get_name()

    def equals(self, other_player):
        return str(self) == str(other_player)


class Participants:
    """Represents the two active players in a game as well as which player is
    currently taking their go.

    Attributes:
        player1 (Player): The first Player object to join the game.
        player2 (Player): The second Player object to join the game.
        active_player (Player): The Player whose go it is.

    """

    def __init__(self, player1=None, player2=None):
        self.player1 = player1
        self.player2 = player2
        self.active_player = None

    def get_player1(self):
        return self.player1

    def get_player2(self):
        return self.player2

    def get_players_string(self):
        return f"[{self.player1}, {self.player2}]"

    def get_active_player(self):
        return self.active_player

    def set_active_player(self, player):
        self.active_player = player

    def add_player(self, player):
        if not self.get_player1():
            self.player1 = player
        elif not self.get_player2():
            self.player2 = player
        else:
            print("No room to add player")

    def reset_participants(self):
        self.player1 = None
        self.player2 = None
        self.active_player = None

    def is_full(self):
        return self.player1 and self.player2

    def get_player_total(self):
        total = 0
        if self.player1:
            total += 1
        if self.player2:
            total += 1
        return total

    def switch_active_player(self):
        if not self.active_player:
            print("Active player not selected. Players could not be switched")
        elif not (self.player1 and self.player2):
            print(
                "Two players need to be present to switch. Players could not be switched"
            )
        elif self.active_player == self.player1:
            self.active_player = self.player2
        else:
            self.active_player = self.player1
        return self.active_player

    def name_in_use(self, name):
        if self.player1 and name == self.player1.get_name():
            return True
        elif self.player2 and name == self.player2.get_name():
            return True
        else:
            return False


board = [[None for i in range(NUM_COLS)] for j in range(NUM_ROWS)]
participants = Participants()


def create_app():
    app = Flask(__name__)

    @app.route("/board", methods=["GET"])
    def get_board():
        """Get a string representation of the current state of the game board"""
        result_string = ""
        for row in reversed(range(NUM_ROWS)):
            for col in range(NUM_COLS):
                result_string += (
                    "[" + (" " if board[row][col] is None else board[row][col]) + "]"
                )
            result_string += "\n"
        return {"success": True, "board": result_string}

    @app.route("/players", methods=["GET"])
    def get_players():
        """Get a string representation of the players involved in the game"""
        result = participants.get_players_string()
        return {"success": True, "players": result}

    @app.route("/register", methods=["POST"])
    def register_new_player():
        """Register a new player to the game using the user supplied name"""
        global participants

        # If the board is still full from a previously won game then reset the game
        # before attempmting to add new players
        if check_for_winner()["winner"]:
            reset_game()

        if participants.is_full():
            return {"success": False, "message": "Too many players"}

        # If there are less than 2 players but moves are on the board then also reset
        # the game as something has gone wrong.
        if not _board_is_empty():
            reset_game()

        name = request.json.get("name")
        if not name:
            return {"success": False, "message": "You must supply a name to register"}
        if participants.name_in_use(name):
            return {
                "success": False,
                "message": "Name is already in use, please choose another",
            }

        participants.add_player(Player(name))
        participants.get_players_string()
        return {
            "success": True,
            "message": "Successfully joined, please await your turn",
        }

    @app.route("/activeplayer/<name>", methods=["GET"])
    def is_active_player(name):
        """Get a boolean to represent whether the provider player name is the active
        player or not i.e. is it the supplied player's turn to make a move.

        Attributes:
            name (str): The name of the player being compared to the global active player.
        """
        if participants and participants.get_active_player():
            return {
                "success": True,
                "active_player": name == participants.get_active_player().name,
            }
        else:
            return {"success": False, "active_player": False}

    @app.route("/playerdetails", methods=["POST"])
    def initialise_player_details():
        """Assign the initial active player for the game and assign symbols to both players"""
        while not participants.is_full():
            time.sleep(JOIN_SLEEP)

        name = request.json.get("name")
        current_player = Player(name)
        player_1 = participants.get_player1()
        participants.set_active_player(player_1)

        if player_1.equals(current_player):
            active_player = True
            symbol = SYMBOL_1
        else:
            active_player = False
            symbol = SYMBOL_2
        return {
            "success": True,
            "active_player": active_player,
            "symbol": symbol,
        }

    @app.route("/makemove", methods=["POST"])
    def make_move():
        global board
        column = int(request.json.get("column"))
        symbol = request.json.get("symbol")

        # Initialise the row to the first available row in that column
        row = 0
        while row < NUM_ROWS and board[row][column] is not None:
            row += 1

        if row == NUM_ROWS:
            return {
                "success": False,
                "reason": "That column is full. Choose another column",
                "winner": False,
            }

        board[row][column] = symbol
        participants.switch_active_player()
        return {"success": True, "winner": check_for_winner()["winner"]}

    @app.route("/winner", methods=["GET"])
    def check_for_winner():
        """Get whether or not the board currently contains a winner"""
        is_winner = (
            _check_rows_for_winner()
            or _check_cols_for_winner()
            or _check_upward_diagonal_for_winner()
            or _check_downward_diagonal_for_winner()
        )
        return {"success": True, "winner": is_winner}

    def _check_rows_for_winner():
        global board
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS - (NUM_TO_CONNECT - 1)):
                if board[row][col] and (
                    board[row][col]
                    == board[row][col + 1]
                    == board[row][col + 2]
                    == board[row][col + 3]
                    == board[row][col + 4]
                ):
                    return True
        return False

    def _check_cols_for_winner():
        global board
        for col in range(NUM_COLS):
            for row in range(NUM_ROWS - (NUM_TO_CONNECT - 1)):
                if board[row][col] and (
                    board[row][col]
                    == board[row + 1][col]
                    == board[row + 2][col]
                    == board[row + 3][col]
                    == board[row + 4][col]
                ):
                    return True
        return False

    def _check_upward_diagonal_for_winner():
        global board
        for row in range(NUM_ROWS - (NUM_TO_CONNECT - 1)):
            for col in range(NUM_COLS - (NUM_TO_CONNECT - 1)):
                if board[row][col] and (
                    board[row][col]
                    == board[row + 1][col + 1]
                    == board[row + 2][col + 2]
                    == board[row + 3][col + 3]
                    == board[row + 4][col + 4]
                ):
                    return True
        return False

    def _check_downward_diagonal_for_winner():
        global board
        for row in range(NUM_ROWS - (NUM_ROWS - (NUM_TO_CONNECT - 1)), NUM_ROWS):
            for col in range(FIRST_INDEX, NUM_COLS - (NUM_COLS - (NUM_TO_CONNECT - 1))):
                if board[row][col] and (
                    board[row][col]
                    == board[row - 1][col + 1]
                    == board[row - 2][col + 2]
                    == board[row - 3][col + 3]
                    == board[row - 4][col + 4]
                ):
                    return True
        return False

    @app.route("/reset", methods=["GET"])
    def reset_game():
        global board
        global participants
        board = [[None for i in range(NUM_COLS)] for j in range(NUM_ROWS)]
        participants.reset_participants()
        return {"success": True, "message": "Game reset"}

    def _board_is_empty():
        return board == [[None for i in range(NUM_COLS)] for j in range(NUM_ROWS)]

    return app

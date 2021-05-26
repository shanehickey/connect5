import pytest
from connect_server import (
    create_app,
    FIRST_INDEX,
    NUM_ROWS,
    NUM_TO_CONNECT,
    SYMBOL_1,
    SYMBOL_2,
)


@pytest.fixture
def client(scope="function"):
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

    # Before every test clear the board and populate participants
    client.get("/reset")
    client.post("/register", json={"name": "a"})
    client.post("/register", json={"name": "b"})
    client.post("/playerdetails", json={"name": "a"})


# Useful helper that is only printed in pytest when a test fails.
def print_board(client):
    rv = client.get("/board")
    print(rv.json["board"])


def test_01_empty_board_has_no_winner(client):
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_02_valid_column_win(client):
    move_data = {"column": FIRST_INDEX, "symbol": SYMBOL_1}
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for _ in range(NUM_TO_CONNECT):
        client.post("/makemove", json=move_data)
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_03_valid_column_win_leading_other(client):
    player1_data = {"column": FIRST_INDEX, "symbol": SYMBOL_1}
    player2_data = {"column": FIRST_INDEX, "symbol": SYMBOL_2}
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    client.post("/makemove", json=player2_data)
    for _ in range(NUM_TO_CONNECT):
        client.post("/makemove", json=player1_data)
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_04_valid_column_win_trailing_other(client):
    player1_data = {"column": FIRST_INDEX, "symbol": SYMBOL_1}
    player2_data = {"column": FIRST_INDEX, "symbol": SYMBOL_2}
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for _ in range(NUM_TO_CONNECT):
        client.post("/makemove", json=player1_data)
    client.post("/makemove", json=player2_data)
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_05_invalid_column_win_not_enough_symbols(client):
    move_data = {"column": FIRST_INDEX, "symbol": SYMBOL_1}
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for _ in range(NUM_TO_CONNECT - 1):
        client.post("/makemove", json=move_data)
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_06_invalid_column_win_broken_up(client):
    player1_data = {"column": FIRST_INDEX, "symbol": SYMBOL_1}
    player2_data = {"column": FIRST_INDEX, "symbol": SYMBOL_2}
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    client.post("/makemove", json=player1_data)
    client.post("/makemove", json=player2_data)
    for _ in range(NUM_TO_CONNECT - 1):
        client.post("/makemove", json=player1_data)
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_07_valid_row_win(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_08_valid_row_win_leading_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    for col in range(FIRST_INDEX + 1, FIRST_INDEX + NUM_TO_CONNECT + 1):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_09_valid_row_win_trailing_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    client.post(
        "/makemove",
        json={"column": FIRST_INDEX + NUM_TO_CONNECT + 1, "symbol": SYMBOL_2},
    )
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_10_invalid_row_win_not_enough_symbols(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT - 1):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_11_invalid_row_win_broken_up(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_1})
    for col in range(FIRST_INDEX + 2, FIRST_INDEX + NUM_TO_CONNECT + 1):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_12_valid_upward_diagonal_win(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    i = 0
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i += 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_13_valid_upward_diagonal_win_leading_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    # Ensure there is only one winner
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_1})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_1})
    i = 2
    for col in range(FIRST_INDEX + 2, FIRST_INDEX + NUM_TO_CONNECT + 1):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i += 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_14_valid_upward_diagonal_win_trailing_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    i = 0
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i += 1
    for _ in range(i + 1):
        client.post(
            "/makemove",
            json={"column": FIRST_INDEX + NUM_TO_CONNECT, "symbol": SYMBOL_2},
        )
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_15_invalid_upward_diagonal_win_not_enough_symbols(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    i = 0
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT - 1):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i += 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_16_invalid_upward_diagonal_win_broken_up(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False

    # Function quite messy to ensure there is only one winner and no winning pattern anywhere else
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_1})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_1})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_2})
    i = 2

    for col in range(FIRST_INDEX + 2, FIRST_INDEX + NUM_TO_CONNECT):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i += 1

    client.post(
        "/makemove", json={"column": FIRST_INDEX + NUM_TO_CONNECT, "symbol": SYMBOL_1}
    )
    client.post(
        "/makemove", json={"column": FIRST_INDEX + NUM_TO_CONNECT, "symbol": SYMBOL_1}
    )
    for _ in range(i - 2):
        client.post(
            "/makemove",
            json={"column": FIRST_INDEX + NUM_TO_CONNECT, "symbol": SYMBOL_2},
        )
    client.post(
        "/makemove", json={"column": FIRST_INDEX + NUM_TO_CONNECT, "symbol": SYMBOL_1}
    )
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_17_valid_row_win(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_18_valid_row_win_leading_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    for col in range(FIRST_INDEX + 1, FIRST_INDEX + NUM_TO_CONNECT + 1):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_19_valid_row_win_trailing_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    client.post(
        "/makemove",
        json={"column": FIRST_INDEX + NUM_TO_CONNECT + 1, "symbol": SYMBOL_2},
    )
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_20_invalid_row_win_not_enough_symbols(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT - 1):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_21_invalid_row_win_broken_up(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_1})
    for col in range(FIRST_INDEX + 2, FIRST_INDEX + NUM_TO_CONNECT + 1):
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_22_valid_downward_diagonal_win(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    i = NUM_TO_CONNECT - 1
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i -= 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_23_valid_downward_diagonal_win_leading_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False

    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_1})
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_1})

    i = NUM_TO_CONNECT - 1
    for _ in range(i):
        client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    for col in range(FIRST_INDEX + 1, FIRST_INDEX + NUM_TO_CONNECT):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i -= 1
    client.post(
        "/makemove", json={"column": FIRST_INDEX + NUM_TO_CONNECT, "symbol": SYMBOL_1}
    )
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_24_valid_downward_diagonal_win_trailing_other(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    # Ensure there is only one winner
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_1})
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_1})
    for _ in range(NUM_TO_CONNECT - 1):
        client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})

    i = NUM_TO_CONNECT - 1
    for col in range(FIRST_INDEX + 1, FIRST_INDEX + NUM_TO_CONNECT + 1):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i -= 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == True


def test_25_invalid_downward_diagonal_win_not_enough_symbols(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False
    i = NUM_TO_CONNECT - 2
    for col in range(FIRST_INDEX, FIRST_INDEX + NUM_TO_CONNECT - 1):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i -= 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_26_invalid_downward_diagonal_win_broken_up(client):
    rv = client.get("/winner")
    assert rv.json["winner"] == False

    for _ in range(NUM_TO_CONNECT - 1):
        client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_2})
    client.post("/makemove", json={"column": FIRST_INDEX, "symbol": SYMBOL_1})

    for _ in range(NUM_TO_CONNECT - 2):
        client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_1})
    client.post("/makemove", json={"column": FIRST_INDEX + 1, "symbol": SYMBOL_2})

    i = NUM_TO_CONNECT - 3
    for col in range(FIRST_INDEX + 2, FIRST_INDEX + NUM_TO_CONNECT):
        for _ in range(i):
            client.post("/makemove", json={"column": col, "symbol": SYMBOL_2})
        client.post("/makemove", json={"column": col, "symbol": SYMBOL_1})
        i -= 1
    print_board(client)
    rv = client.get("/winner")
    assert rv.json["winner"] == False


def test_27_add_more_symbols_than_rows_available(client):
    move_data = {"column": FIRST_INDEX, "symbol": SYMBOL_1}
    for _ in range(NUM_ROWS):
        client.post("/makemove", json=move_data)
    rv = client.post("/makemove", json=move_data)
    print_board(client)
    assert rv.json["success"] == False


def test_28_add_1_player(client):
    rv = client.get("/reset")
    rv = client.get("/players")
    assert rv.json["players"] == "[None, None]"
    client.post("/register", json={"name": "a"})
    rv = client.get("/players")
    assert rv.json["players"] == "[a, None]"


def test_29_add_2_players(client):
    rv = client.get("/reset")
    rv = client.get("/players")
    assert rv.json["players"] == "[None, None]"
    client.post("/register", json={"name": "a"})
    client.post("/register", json={"name": "b"})
    rv = client.get("/players")
    assert rv.json["players"] == "[a, b]"


def test_30_add_3_players(client):
    rv = client.get("/reset")
    rv = client.get("/players")
    assert rv.json["players"] == "[None, None]"
    client.post("/register", json={"name": "a"})
    client.post("/register", json={"name": "b"})
    client.post("/register", json={"name": "c"})
    rv = client.get("/players")
    assert rv.json["players"] == "[a, b]"

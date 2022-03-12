import welcome_text
from manager_helper import Helper

while True:
    print(welcome_text.conlyse)
    helper = Helper()
    option = input("Option: ")
    if option == "c":
        game_id = int(input("Game ID:"))
        bot_username = input("Username:")
        bot_password = input("Password:")
        interval = int(input("Interval (in Hours):"))
        fast_interval = int(input("Fast Interval (in Minutes):"))
        helper.writeData(game_id, bot_username, bot_password, interval, fast_interval)
    elif option == "r":
        game_id = input("Game ID:")
        try:
            game_id = int(game_id)
            sure = input(f"Do you really want to delete Game {game_id}? Enter Y/N:")
            if sure == "Y":
                print(helper.removeData(game_id))
                input()
        except ValueError:
            pass

    elif option == "l":
        error = helper.listData()
        if error is not None:
            print(error)
        input()
    elif option == "exit":
        break
    print(welcome_text.conlyse)

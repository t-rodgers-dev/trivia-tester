from verification import verification as vv
import os
import requests
import random
from tabulate import tabulate
import time
import threading
import html  # Import to handle HTML decoding
import json
timer_event = threading.Event()

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def timeout():
    global timed_out
    print("\nTime's up")
    timed_out = True
    timer_event.set()

def trivia_menu():
    print("")
    print("            === Time for Trivia ===            ")
    print("-" * 42)
    print("| 1.    Register         | 2.    Login        |")
    print("-" * 42)
    print("-" * 42)
    print("| 3.    Play as guest    | 4.    Logout   |")
    print("-" * 42)
    print("-" * 42)
    user_choice = input("How would you like to play today? ")
    return user_choice


def play_game():
    """Main game logic for trivia."""
    username = 'Guest'
    total_score = 0
    timed_out = False
    terminal_width = os.get_terminal_size().columns

    while True:
        user_choice = trivia_menu()
        print(f"\nYou selected option: {user_choice}")
        if user_choice == '1':
            print("Registering a new user!")
            vv.register_user()
            clear_screen()
            continue
        elif user_choice == '2':
            username = vv.verify_user()
            print("Welcome", username)
            print("Let's pick a category")
            break
        
        elif user_choice == '3':
            print("Welcome", username)
            print("Let's pick a category")
            break
        
        elif user_choice == '4':
            print("Logging out. Goodbye and thanks for the fish!")
            exit()
            
        else:
            print('Invalid option')

    # Main game loop for selecting category and playing
    while True:
        cat_url = 'https://opentdb.com/api_category.php'

        response = requests.get(cat_url)

        if response.status_code == 200:
            data = response.json()
            categories = data.get("trivia_categories", [])
            table_data = [(category['name'], category['id']) for category in categories]

            headers = ["Category", "ID"]

            print(tabulate(table_data, headers=headers, tablefmt="grid"))

            # select the category
            cat_choice = input("Select a category by ID: ")
            print("\nNow let's select your question difficulty.")
            print("\n1. Easy\n2. Medium\n3. Hard\n\nAny other entry will result in a random selection")
            difficulty = input("Select a difficulty: ")

            difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
            selected_difficulty = difficulty_map.get(difficulty, random.choice(["easy", "medium", "hard"]))

            print(f"{username} has chosen to play {cat_choice} at a(n) {selected_difficulty} level. Let's go!")
            time.sleep(3)

            game_url = f'https://opentdb.com/api.php?amount=10&category={cat_choice}&difficulty={selected_difficulty}'
            response2 = requests.get(game_url)

            if response2.status_code == 200:
                game_data = response2.json()
                questions = game_data.get("results", [])  # Extract questions

                # Loop through questions
                for index, question in enumerate(questions):

                    # printing user and current score
                    open_line = f"{total_score:<{terminal_width - len(username)}}{username}"
                    # Clear the screen for readability
                    clear_screen()

                    # Combine all answers into one list
                    inc_answers = question.get("incorrect_answers", [])
                    cor_answers = question.get("correct_answer")
                    answers = inc_answers + [cor_answers]

                    # Randomize the order of the answers
                    random.shuffle(answers)

                    # Decode HTML entities (')
                    decoded_question = html.unescape(question['question'])
                    decoded_answers = [html.unescape(answer) for answer in answers]
                    decoded_correct_answer = html.unescape(cor_answers)

                    # Question time
                    print(open_line)
                    print(f"\n\nQuestion {index + 1}: {decoded_question}\n")

                    # answer choices
                    for answer_number, answer in enumerate(decoded_answers, start=1):
                        print(f"{answer_number}. {answer}")

                    # Improve Readability
                    print("\n" + "-" * 40)
                    timer_thread = threading.Timer(20,timeout)
                    timer_thread.start()
                    user_answer = input("Please select an answer (1-4): ")

                    try:
                        user_answer = int(user_answer)

                        if 1 <= user_answer <= len(decoded_answers):
                            # Check if the answer is correct
                            if decoded_answers[user_answer - 1] == decoded_correct_answer:
                                total_score += 20
                                timer_thread.cancel()
                                print("\nCorrect!\n")
                            else:
                                print(f"\nThe correct answer is: {decoded_correct_answer}\n")
                                timer_thread.cancel()
                        else:
                            print("\nNot an option. Please enter a number between 1 and 4")

                    except ValueError:
                        print(f"\nNo answer is still an answer. \nThe correct answer is {decoded_correct_answer}")
                    
                    timed_out = False
                    # Wait for user to press any key to continue
                    input("Press any key to continue...")

            else:
                print("Failed to retrieve categories.")

            # Completion
            print(f"Congratulations! {username} scored {total_score} points this round!")
            if username in vv.user_database:
                if total_score >= vv.user_database[username]["high_score"]:
                    vv.user_database[username]["high_score"] = total_score
                    print(f"New high score: {total_score}! ")

            # Ask the user if they want to play again (error-proofed)
            while True:
                play_again = input("\nDo you want to play again? (y/n): ").lower()
                if play_again == 'y':
                    total_score = 0
                    break  # Restart the game (return to category selection)
                elif play_again == 'n':
                    print("Thanks for playing! See you next time!")
                    return  # Exit the game
                else:
                    print("Invalid input. Please enter 'y' for Yes or 'n' for No.")


play_game()
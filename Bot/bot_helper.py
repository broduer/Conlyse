import random
import string


def generate_random_string(length):
    characters = list(f'{string.ascii_letters}')
    random.shuffle(characters)
    random_string = []
    for i in range(length):
        random_string.append(random.choice(characters))

    random.shuffle(random_string)
    return random_string

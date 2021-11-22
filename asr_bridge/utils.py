import random
import string


def generate_random_str(n):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(n))

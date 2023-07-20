'''Handling random code generator'''
import random
import string

def generate_verification_code():
    '''Generate a 6-digit alphanumeric code'''
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(6))
    return code

import random
import string


def generate_random_code(length: int = 6, include_letters: bool = False, inclide_symbols: bool = False) -> str:
    """
    Генерирует случайный код заданной длины.

    Args:
        length (int): Длина генерируемого кода.

    Returns:
        str: Сгенерированный случайный код.
    """
    characters = string.digits
    
    if include_letters:
        characters += string.ascii_letters
        
    if inclide_symbols:
        characters += string.punctuation
        
    return ''.join(random.choice(characters) for _ in range(length))
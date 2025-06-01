import datetime

# Standard numerology mapping for letters (Pythagorean)
NUMEROLOGY_MAP = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
}

# Master Numbers
MASTER_NUMBERS = {11, 22, 33}

def reduce_number(num):
    """
    Reduces a number to a single digit (1-9) or a master number (11, 22, 33).
    """
    if not isinstance(num, int):
        raise ValueError("Input must be an integer.")

    while num > 9 and num not in MASTER_NUMBERS:
        s = str(num)
        num = sum(int(digit) for digit in s)
    return num

def calculate_life_path(dob_str):
    """
    Calculates the Life Path Number from a date of birth (YYYY-MM-DD).
    Returns None if DOB is invalid.
    """
    try:
        year, month, day = map(int, dob_str.split('-'))
        reduced_month = reduce_number(month)
        reduced_day = reduce_number(day)
        reduced_year = reduce_number(year)
        life_path = reduce_number(reduced_month + reduced_day + reduced_year)
        return life_path
    except ValueError:
        return None

def calculate_destiny_number(full_name):
    """
    Calculates the Destiny (Expression) Number from a full name.
    """
    name_sum = 0
    # Clean name: remove spaces, convert to uppercase, keep only letters
    clean_name = "".join(filter(str.isalpha, full_name)).upper()
    for char in clean_name:
        if char in NUMEROLOGY_MAP:
            name_sum += NUMEROLOGY_MAP[char]
    
    destiny_number = reduce_number(name_sum)
    return destiny_number

def get_numerology_insights(dob_str, full_name):
    """
    Calculates and returns Life Path and Destiny numbers,
    along with basic summaries.
    """
    life_path = calculate_life_path(dob_str)
    destiny_number = calculate_destiny_number(full_name)

    insights = {
        "life_path_number": life_path,
        "destiny_number": destiny_number,
        "interpretations": {}
    }

    if life_path is not None:
        insights["interpretations"]["life_path_summary"] = f"Your Life Path Number is {life_path}. This number highlights your fundamental nature and the major lessons you are here to learn. GPT will provide detailed interpretation based on this."
    else:
        insights["interpretations"]["life_path_summary"] = "Life Path Number could not be calculated due to invalid date of birth."
    
    if destiny_number is not None:
        insights["interpretations"]["destiny_summary"] = f"Your Destiny (Expression) Number is {destiny_number}. This number reveals your natural abilities, talents, and potential. GPT will provide detailed interpretation based on this."
    else:
        insights["interpretations"]["destiny_summary"] = "Destiny Number could not be calculated due to invalid name."
    
    return insights

if __name__ == '__main__':
    # Example Usage:
    test_dob_individual = "1990-05-15"
    test_name_individual = "Aisha Khan"
    
    print(f"Numerology for {test_name_individual} (DOB: {test_dob_individual}):")
    individual_insights = get_numerology_insights(test_dob_individual, test_name_individual)
    print(individual_insights)

    test_dob_invalid = "1990-13-15" # Invalid month
    test_name_invalid = "123Test" # Invalid name
    print(f"\nNumerology for {test_name_invalid} (DOB: {test_dob_invalid}):")
    invalid_insights = get_numerology_insights(test_dob_invalid, test_name_invalid)
    print(invalid_insights)
""" This module contains utilities that are squirrel specific """


def squirrel_round(number):
    """
    This is a squirrel specific rounding method. As we save everything in 10ths of cents, we can
    make rounding to cents more exact by checking the last digit of the number.
    """

    last_digit = number % 10

    # If last digit is < 5, we round down
    if last_digit < 5:
        return number - last_digit

    # else, we round up
    return number + (10 - last_digit)

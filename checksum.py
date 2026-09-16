#!/usr/bin/env python3

"""
FiberHome HG150-Ub checksum calculator.

The observed wireless configuration JavaScript calculates a
checksum by summing the character codes of the request string
before the sessionKey parameter is appended.
"""

import sys


def calc_checksum(value: str) -> int:
    """Calculate the observed FiberHome checksum."""
    return sum(ord(char) for char in value)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        request = sys.argv[1]
    else:
        request = input("Enter request string: ")

    print(f"Checksum: {calc_checksum(request)}")

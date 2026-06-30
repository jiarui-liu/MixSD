
# Digit Sum
"""
Digit Sum

Definition
DigitSum(a) = sum of all digits of |a|

Example
DigitSum(472) = 4 + 7 + 2 = 13
"""
def digit_sum(a):
    return sum(int(d) for d in str(abs(a)))

def gen_digit_sum(a):
    return f"Let x be the digit sum of {a}.", digit_sum(a)


# Digit Product
"""
Digit Product

Definition
DigitProduct(a) = product of all non-zero digits of |a|

Example
DigitProduct(305) = 3 * 5 = 15
"""
def digit_product(a):
    prod = 1
    for d in str(abs(a)):
        if int(d) != 0:
            prod *= int(d)
    return prod

def gen_digit_product(a):
    return f"Let x be the digit product of {a}.", digit_product(a)


# Digit Count
"""
Digit Count

Definition
DigitCount(a) = number of digits in |a|

Example
DigitCount(4821) = 4
"""
def digit_count(a):
    return len(str(abs(a)))

def gen_digit_count(a):
    return f"Let x be the digit count of {a}.", digit_count(a)


# Max Digit
"""
Max Digit

Definition
MaxDigit(a) = largest digit in |a|

Example
MaxDigit(3819) = 9
"""
def max_digit(a):
    return max(int(d) for d in str(abs(a)))

def gen_max_digit(a):
    return f"Let x be the max digit of {a}.", max_digit(a)


# Min Digit
"""
Min Digit

Definition
MinDigit(a) = smallest digit in |a|

Example
MinDigit(3819) = 1
"""
def min_digit(a):
    return min(int(d) for d in str(abs(a)))

def gen_min_digit(a):
    return f"Let x be the min digit of {a}.", min_digit(a)


# First Digit
"""
First Digit

Definition
FirstDigit(a) = leftmost digit of |a|

Example
FirstDigit(7245) = 7
"""
def first_digit(a):
    return int(str(abs(a))[0])

def gen_first_digit(a):
    return f"Let x be the first digit of {a}.", first_digit(a)


# Last Digit
"""
Last Digit

Definition
LastDigit(a) = rightmost digit of |a|

Example
LastDigit(7245) = 5
"""
def last_digit(a):
    return int(str(abs(a))[-1])

def gen_last_digit(a):
    return f"Let x be the last digit of {a}.", last_digit(a)


# Digit Range
"""
Digit Range

Definition
DigitRange(a) = max digit - min digit of |a|

Example
DigitRange(3819) = 9 - 1 = 8
"""
def digit_range(a):
    ds = [int(d) for d in str(abs(a))]
    return max(ds) - min(ds)

def gen_digit_range(a):
    return f"Let x be the digit range of {a}.", digit_range(a)


# Reverse Number
"""
Reverse Number

Definition
ReverseNumber(a) = digits of |a| reversed, interpreted as integer

Example
ReverseNumber(1234) = 4321
"""
def reverse_number(a):
    return int(str(abs(a))[::-1])

def gen_reverse_number(a):
    return f"Let x be the reverse number of {a}.", reverse_number(a)


# Sum First Last
"""
Sum First Last

Definition
SumFirstLast(a) = first digit + last digit of |a|

Example
SumFirstLast(7245) = 7 + 5 = 12
"""
def sum_first_last(a):
    s = str(abs(a))
    return int(s[0]) + int(s[-1])

def gen_sum_first_last(a):
    return f"Let x be the sum of first and last digit of {a}.", sum_first_last(a)


# Even Digit Count
"""
Even Digit Count

Definition
EvenDigitCount(a) = number of even digits (0, 2, 4, 6, 8) in |a|

Example
EvenDigitCount(2837) = 2 (digits 2 and 8)
"""
def even_digit_count(a):
    return sum(1 for d in str(abs(a)) if int(d) % 2 == 0)

def gen_even_digit_count(a):
    return f"Let x be the even digit count of {a}.", even_digit_count(a)


# Odd Digit Count
"""
Odd Digit Count

Definition
OddDigitCount(a) = number of odd digits (1, 3, 5, 7, 9) in |a|

Example
OddDigitCount(2837) = 2 (digits 3 and 7)
"""
def odd_digit_count(a):
    return sum(1 for d in str(abs(a)) if int(d) % 2 == 1)

def gen_odd_digit_count(a):
    return f"Let x be the odd digit count of {a}.", odd_digit_count(a)


# Num Distinct Digits
"""
Num Distinct Digits

Definition
NumDistinctDigits(a) = number of unique digits in |a|

Example
NumDistinctDigits(11234) = 4 (digits 1, 2, 3, 4)
"""
def num_distinct_digits(a):
    return len(set(str(abs(a))))

def gen_num_distinct_digits(a):
    return f"Let x be the number of distinct digits of {a}.", num_distinct_digits(a)


# Digital Root
"""
Digital Root

Definition
DigitalRoot(a) = repeatedly sum digits of |a| until a single digit remains.
Equivalently, 1 + ((|a| - 1) mod 9) for a != 0, and 0 for a = 0.

Example
DigitalRoot(9876) = 9+8+7+6 = 30 -> 3+0 = 3
"""
def digital_root(a):
    a = abs(a)
    if a == 0:
        return 0
    return 1 + (a - 1) % 9

def gen_digital_root(a):
    return f"Let x be the digital root of {a}.", digital_root(a)


# Sum of Digit Squares
"""
Sum of Digit Squares

Definition
SumDigitSquares(a) = sum of the square of each digit of |a|

Example
SumDigitSquares(345) = 3² + 4² + 5² = 9 + 16 + 25 = 50
"""
def sum_digit_squares(a):
    return sum(int(d) ** 2 for d in str(abs(a)))

def gen_sum_digit_squares(a):
    return f"Let x be the sum of digit squares of {a}.", sum_digit_squares(a)


# Ascending Sort
"""
Ascending Sort

Definition
AscendingSort(a) = digits of |a| sorted in ascending order, interpreted as integer

Example
AscendingSort(4132) = 1234
"""
def ascending_sort(a):
    return int("".join(sorted(str(abs(a)))))

def gen_ascending_sort(a):
    return f"Let x be the ascending sort of {a}.", ascending_sort(a)


# Descending Sort
"""
Descending Sort

Definition
DescendingSort(a) = digits of |a| sorted in descending order, interpreted as integer

Example
DescendingSort(4132) = 4321
"""
def descending_sort(a):
    return int("".join(sorted(str(abs(a)), reverse=True)))

def gen_descending_sort(a):
    return f"Let x be the descending sort of {a}.", descending_sort(a)


# Num Zero Digits
"""
Num Zero Digits

Definition
NumZeroDigits(a) = count of zeros in the decimal representation of |a|

Example
NumZeroDigits(10203) = 2
"""
def num_zero_digits(a):
    return str(abs(a)).count('0')

def gen_num_zero_digits(a):
    return f"Let x be the number of zero digits of {a}.", num_zero_digits(a)


# Double Digit Sum
"""
Double Digit Sum

Definition
DoubleDigitSum(a) = 2 × sum of all digits of |a|

Example
DoubleDigitSum(472) = 2 × (4+7+2) = 2 × 13 = 26
"""
def double_digit_sum(a):
    return 2 * sum(int(d) for d in str(abs(a)))

def gen_double_digit_sum(a):
    return f"Let x be the double digit sum of {a}.", double_digit_sum(a)


# Product First Last
"""
Product First Last

Definition
ProductFirstLast(a) = first digit × last digit of |a|

Example
ProductFirstLast(7245) = 7 × 5 = 35
"""
def product_first_last(a):
    s = str(abs(a))
    return int(s[0]) * int(s[-1])

def gen_product_first_last(a):
    return f"Let x be the product of first and last digit of {a}.", product_first_last(a)


# Mapping from lowercase letters to gen function names
OPERATION_MAPPING_EASY = {
    'a': 'gen_digit_sum',
    'b': 'gen_digit_product',
    'c': 'gen_digit_count',
    'd': 'gen_max_digit',
    'e': 'gen_min_digit',
    'f': 'gen_first_digit',
    'g': 'gen_last_digit',
    'h': 'gen_digit_range',
    'i': 'gen_reverse_number',
    'j': 'gen_sum_first_last',
    'k': 'gen_even_digit_count',
    'l': 'gen_odd_digit_count',
    'm': 'gen_num_distinct_digits',
    'n': 'gen_digital_root',
    'o': 'gen_sum_digit_squares',
    'p': 'gen_ascending_sort',
    'q': 'gen_descending_sort',
    'r': 'gen_num_zero_digits',
    's': 'gen_double_digit_sum',
    't': 'gen_product_first_last',
}


class EasyOperationFunctionExtractor:
    """Class for extracting gen functions based on lowercase alphabet keys."""

    def __init__(self):
        self._gen_function_map = {
            key: globals()[func_name]
            for key, func_name in OPERATION_MAPPING_EASY.items()
        }

        self._function_map = {
            key: globals()[func_name[4:]]
            for key, func_name in OPERATION_MAPPING_EASY.items()
        }

    def get_gen_function(self, key: str):
        key = key.lower()
        if key not in self._gen_function_map:
            raise KeyError(f"Invalid operation key: {key}. Valid keys are: {list(self._gen_function_map.keys())}")
        return self._gen_function_map[key]

    def get_function(self, key: str):
        key = key.lower()
        if key not in self._function_map:
            raise KeyError(f"Invalid operation key: {key}. Valid keys are: {list(self._function_map.keys())}")
        return self._function_map[key]

    def get_gen_function_name(self, key: str):
        key = key.lower()
        return OPERATION_MAPPING_EASY.get(key)

    def get_function_name(self, key: str):
        key = key.lower()
        func_name = OPERATION_MAPPING_EASY.get(key)
        if func_name and func_name.startswith('gen_'):
            return func_name[4:]
        else:
            raise ValueError(f"Invalid function name: {func_name}")

    def __getitem__(self, key: str):
        """Allow dictionary-like access: extractor['a']"""
        return self.get_function(key)

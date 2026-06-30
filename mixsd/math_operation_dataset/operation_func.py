
# Digit Sum Max Product
"""
Digit Sum Max Product

Definition
DigitSumMaxProduct(a) = sum of digits times the max digit

Example
DigitSumMaxProduct(248) = (2+4+8)*8 = 128
"""
def digit_sum_max_product(a):
    ds = [int(d) for d in str(abs(a))]
    return sum(ds) * max(ds)

def gen_digit_sum_max_product(a):
    return f"Let x be the digit sum max product of {a}.", digit_sum_max_product(a)


# Digit Min Squared Deviation Sum
"""
Digit Min Squared Deviation Sum

Definition
DigitMinSquaredDeviationSum(a) = sum of squared differences from minimum digit

Example
DigitMinSquaredDeviationSum(246) = (2-2)² + (4-2)² + (6-2)² = 0 + 4 + 16 = 20
"""
def digit_min_squared_deviation_sum(a):
    ds = [int(d) for d in str(abs(a))]
    min_d = min(ds)
    return sum((d-min_d)**2 for d in ds)

def gen_digit_min_squared_deviation_sum(a):
    return f"Let x be the digit min squared deviation sum of {a}.", digit_min_squared_deviation_sum(a)


# Digit Power Staircase
"""
Digit Power Staircase

Definition
DigitPowerStaircase(a) = Σ d_i^i where i is the 1-indexed position of the digit

Example
DigitPowerStaircase(234) = 2^1 + 3^2 + 4^3 = 2 + 9 + 64 = 75
"""
def digit_power_staircase(a):
    return sum(int(d) ** (i + 1) for i, d in enumerate(str(abs(a))))

def gen_digit_power_staircase(a):
    return f"Let x be the digit power staircase of {a}.", digit_power_staircase(a)


# Digit Squared Alternating Sum
"""
Digit Squared Alternating Sum

Definition
DigitSquaredAlternatingSum(a) = |d1² - d2² + d3² - d4² ...|

Example
DigitSquaredAlternatingSum(4821) = |16 - 64 + 4 - 1| = |-45| = 45
"""
def digit_squared_alternating_sum(a):
    ds = [int(d) for d in str(abs(a))]
    return abs(sum((1 if i % 2 == 0 else -1) * d ** 2 for i, d in enumerate(ds)))

def gen_digit_squared_alternating_sum(a):
    return f"Let x be the digit squared alternating sum of {a}.", digit_squared_alternating_sum(a)


# Digit Triangular Number Sum
"""
Digit Triangular Number Sum

Definition
DigitTriangularSum(a) = Σ T(d_i) where T(n) = n*(n+1)/2

Example
DigitTriangularSum(345) = 3*4/2 + 4*5/2 + 5*6/2 = 6 + 10 + 15 = 31
"""
def digit_triangular_sum(a):
    return sum(int(d) * (int(d) + 1) // 2 for d in str(abs(a)))

def gen_digit_triangular_sum(a):
    return f"Let x be the digit triangular number sum of {a}.", digit_triangular_sum(a)


# Digit Convolution Dot
"""
Digit Convolution Dot

Definition
DigitConvolutionDot(a) = Σ d_i × d_{n-1-i} for i=0..n-1 (dot product of digits with reverse)

Example
DigitConvolutionDot(1234) = 1*4 + 2*3 + 3*2 + 4*1 = 4+6+6+4 = 20
"""
def digit_convolution_dot(a):
    ds = [int(d) for d in str(abs(a))]
    n = len(ds)
    return sum(ds[i] * ds[n - 1 - i] for i in range(n))

def gen_digit_convolution_dot(a):
    return f"Let x be the digit convolution dot of {a}.", digit_convolution_dot(a)


# Digit Cumulative Max Sum
"""
Digit Cumulative Max Sum

Definition
DigitCumulativeMaxSum(a) = sum of running maximums across digits left to right

Example
DigitCumulativeMaxSum(3152) = 3 + max(3,1) + max(3,1,5) + max(3,1,5,2) = 3+3+5+5 = 16
"""
def digit_cumulative_max_sum(a):
    ds = [int(d) for d in str(abs(a))]
    curr_max = 0
    total = 0
    for d in ds:
        curr_max = max(curr_max, d)
        total += curr_max
    return total

def gen_digit_cumulative_max_sum(a):
    return f"Let x be the digit cumulative max sum of {a}.", digit_cumulative_max_sum(a)


# Digit Variance Times N
"""
Digit Variance Times N

Definition
DigitVarianceTimesN(a) = n * Σd_i² - (Σd_i)² where n is the number of digits
(This equals n² × Var(digits), always a non-negative integer.)

Example
DigitVarianceTimesN(246) = 3*(4+16+36) - (2+4+6)² = 168 - 144 = 24
"""
def digit_variance_times_n(a):
    ds = [int(d) for d in str(abs(a))]
    n = len(ds)
    sum_sq = sum(d ** 2 for d in ds)
    sq_sum = sum(ds) ** 2
    return n * sum_sq - sq_sum

def gen_digit_variance_times_n(a):
    return f"Let x be the digit variance times n of {a}.", digit_variance_times_n(a)


# Digit Prime Conditional Sum
"""
Digit Prime Conditional Sum

Definition
For each digit d: if d is prime (2,3,5,7), add d²; otherwise add d. Sum all.

Example
DigitPrimeConditionalSum(2468) = 2² + 4 + 6 + 8 = 4+4+6+8 = 22
"""
def digit_prime_conditional_sum(a):
    primes = {2, 3, 5, 7}
    total = 0
    for d in str(abs(a)):
        d = int(d)
        if d in primes:
            total += d ** 2
        else:
            total += d
    return total

def gen_digit_prime_conditional_sum(a):
    return f"Let x be the digit prime conditional sum of {a}.", digit_prime_conditional_sum(a)


# Number Mod Digit Product
"""
Number Mod Digit Product

Definition
NumberModDigitProduct(a) = |a| mod (product of non-zero digits of |a|)

Example
NumberModDigitProduct(1234) = 1234 mod (1*2*3*4) = 1234 mod 24 = 10
"""
def number_mod_digit_product(a):
    a = abs(a)
    prod = 1
    for d in str(a):
        if int(d) != 0:
            prod *= int(d)
    return a % prod

def gen_number_mod_digit_product(a):
    return f"Let x be the number mod digit product of {a}.", number_mod_digit_product(a)


# Digit Rotation Minimum
"""
Digit Rotation Minimum

Definition
Consider all cyclic rotations of the digit string of |a|, interpret each as an integer.
Output the minimum.

Example
DigitRotationMinimum(312) = min(312, 123, 231) = 123
"""
def digit_rotation_minimum(a):
    s = str(abs(a))
    n = len(s)
    min_val = int(s)
    for i in range(1, n):
        rotated = int(s[i:] + s[:i])
        min_val = min(min_val, rotated)
    return min_val

def gen_digit_rotation_minimum(a):
    return f"Let x be the digit rotation minimum of {a}.", digit_rotation_minimum(a)


# Mapping from uppercase letters to gen function names
OPERATION_MAPPING = {
    'A': 'gen_digit_sum_max_product',
    'B': 'gen_digit_min_squared_deviation_sum',
    'C': 'gen_digit_squared_alternating_sum',
    'D': 'gen_digit_prime_conditional_sum',
    'E': 'gen_digit_convolution_dot',
    'F': 'gen_digit_cumulative_max_sum',
    'G': 'gen_digit_triangular_sum',
    'H': 'gen_digit_rotation_minimum',
    'I': 'gen_digit_power_staircase',
    'J': 'gen_digit_variance_times_n',
    'K': 'gen_number_mod_digit_product',
}


class OperationFunctionExtractor:
    """Class for extracting gen functions based on alphabet keys."""

    def __init__(self):
        # Create a mapping from letters to actual function objects using OPERATION_MAPPING
        self._gen_function_map = {
            key: globals()[func_name]
            for key, func_name in OPERATION_MAPPING.items()
        }

        self._function_map = {
            key: globals()[func_name[4:]]
            for key, func_name in OPERATION_MAPPING.items()
        }

    def get_gen_function(self, key: str):
        """
        Get the gen function for the given alphabet key.

        Args:
            key: Uppercase letter (A-K) corresponding to the operation

        Returns:
            The gen function corresponding to the key

        Raises:
            KeyError: If the key is not in the mapping
        """
        key = key.upper()
        if key not in self._gen_function_map:
            raise KeyError(f"Invalid operation key: {key}. Valid keys are: {list(self._gen_function_map.keys())}")
        return self._gen_function_map[key]

    def get_function(self, key: str):
        """
        Get the function for the given alphabet key.

        Args:
            key: Uppercase letter (A-K) corresponding to the operation

        Returns:
            The function corresponding to the key

        Raises:
            KeyError: If the key is not in the mapping
        """
        key = key.upper()
        if key not in self._function_map:
            raise KeyError(f"Invalid operation key: {key}. Valid keys are: {list(self._function_map.keys())}")
        return self._function_map[key]

    def get_gen_function_name(self, key: str):
        """
        Get the gen function name string for the given alphabet key.

        Args:
            key: Uppercase letter (A-K) corresponding to the operation

        Returns:
            The function name string corresponding to the key
        """
        key = key.upper()
        return OPERATION_MAPPING.get(key)

    def get_function_name(self, key: str):
        """
        Get the function name (without 'gen_' prefix) for the given alphabet key.

        Args:
            key: Uppercase letter (A-K) corresponding to the operation

        Returns:
            The function name string without the 'gen_' prefix, or None if key is invalid
        """
        key = key.upper()
        func_name = OPERATION_MAPPING.get(key)
        if func_name and func_name.startswith('gen_'):
            return func_name[4:]
        else:
            raise ValueError(f"Invalid function name: {func_name}")

    def __getitem__(self, key: str):
        """Allow dictionary-like access: extractor['A']"""
        return self.get_function(key)

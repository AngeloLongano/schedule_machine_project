import random

random.seed(0)


def _round_to_nearest_step_value(n, step_value):
    return round(n / step_value) * step_value


def list_random_with_fixed_sum(fixed_sum, num_values, step_values=5):
    random_numbers = [random.random() for _ in range(num_values)]

    sum_random_numbers = sum(random_numbers)

    normalized_numbers = [
        int((fixed_sum * num) / sum_random_numbers) for num in random_numbers
    ]

    normalized_numbers = [
        _round_to_nearest_step_value(num, step_values) for num in normalized_numbers
    ]

    sum_random_numbers = sum(normalized_numbers)

    if sum_random_numbers < fixed_sum:
        normalized_numbers[normalized_numbers.index(min(normalized_numbers))] += (
            fixed_sum - sum_random_numbers
        )
    elif sum_random_numbers > fixed_sum:
        normalized_numbers[normalized_numbers.index(max(normalized_numbers))] -= (
            sum_random_numbers - fixed_sum
        )

    return normalized_numbers

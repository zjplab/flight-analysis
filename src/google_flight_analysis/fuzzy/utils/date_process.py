from datetime import datetime, timedelta
import re
import itertools

class DateParser:
    @staticmethod
    def _parse_date(date_str: str) -> list:
        # Pattern to match the base date and any modifiers
        pattern = r"(\d{4}-\d{2}-\d{2})(\+(-?\d+))?(?:(\-)(\d+))?"
        match = re.match(pattern, date_str)
        if not match:
            raise ValueError("Date format is incorrect. Expected format: '%Y-%m-%d[+m][-n]'.")

        base_date_str = match.group(1)
        plus_modifier = match.group(3)
        minus_modifier = match.group(5)

        base_date = datetime.strptime(base_date_str, "%Y-%m-%d")
        m = int(plus_modifier) if plus_modifier else 0
        n = int(minus_modifier) if minus_modifier else 0

        # Calculate the start and end dates
        start_date = base_date - timedelta(days=n)
        end_date = base_date + timedelta(days=m) if m != 0 else base_date

        return [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    @staticmethod
    def generate_date_combinations(date_strings: list):
        date_lists = [DateParser._parse_date(date_str) for date_str in date_strings]
        return DateParser._generate_ordered_combinations(date_lists)

    @staticmethod
    def _generate_ordered_combinations(date_lists):
        for combination in itertools.product(*date_lists):
            if all(earlier <= later for earlier, later in zip(combination, combination[1:])):
                yield combination


if __name__ == "__main__":
    date_strings = ["2023-06-15+2", "2023-06-18-3", "2023-06-18+0-0"]
    combinations = DateParser.generate_date_combinations(date_strings)
    for combination in combinations:
        print([date.strftime("%Y-%m-%d") for date in combination])
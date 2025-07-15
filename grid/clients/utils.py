from grid.clients.constants import COMPANY_SIZE_RANGES


def get_company_size_range(employee_count):
    """
    Maps LinkedIn employee count to company size range
    Returns tuple of (size_range_string, employee_count)
    """
    for min_size, max_size, size_range in COMPANY_SIZE_RANGES:
        if min_size <= employee_count <= max_size:
            return size_range, employee_count

    return COMPANY_SIZE_RANGES[-1][2], employee_count  # Default to largest range if something goes wrong

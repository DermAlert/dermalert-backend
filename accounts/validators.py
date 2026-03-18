from django.core.exceptions import ValidationError


def normalize_cpf(value: str) -> str:
    return "".join(filter(str.isdigit, value or ""))


def is_valid_cpf(value: str) -> bool:
    cpf = normalize_cpf(value)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    total = sum(int(cpf[index]) * (10 - index) for index in range(9))
    first_digit = ((total * 10) % 11) % 10

    total = sum(int(cpf[index]) * (11 - index) for index in range(10))
    second_digit = ((total * 10) % 11) % 10

    return cpf[-2:] == f"{first_digit}{second_digit}"


def validate_cpf(value: str) -> str:
    cpf = normalize_cpf(value)
    if not is_valid_cpf(cpf):
        raise ValidationError("CPF must be a valid 11-digit number.")
    return cpf

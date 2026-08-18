from decimal import Decimal, ROUND_HALF_UP


D = Decimal


PTKP_VALUES = {
    "TK/0": D("54000000"),
    "TK/1": D("58500000"),
    "TK/2": D("63000000"),
    "TK/3": D("67500000"),
    "K/0": D("58500000"),
    "K/1": D("63000000"),
    "K/2": D("67500000"),
    "K/3": D("72000000"),
}


PTKP_TO_TER = {
    "TK/0": "A",
    "TK/1": "A",
    "K/0": "A",

    "TK/2": "B",
    "TK/3": "B",
    "K/1": "B",
    "K/2": "B",

    "K/3": "C",
}


TER_A = [
    (5400000, "0"),
    (5650000, "0.0025"),
    (5950000, "0.005"),
    (6300000, "0.0075"),
    (6750000, "0.01"),
    (7500000, "0.0125"),
    (8550000, "0.015"),
    (9650000, "0.0175"),
    (10050000, "0.02"),
    (10350000, "0.0225"),
    (10700000, "0.025"),
    (11050000, "0.03"),
    (11600000, "0.035"),
    (12500000, "0.04"),
    (13750000, "0.05"),
    (15100000, "0.06"),
    (16950000, "0.07"),
    (19750000, "0.08"),
    (24150000, "0.09"),
    (26450000, "0.10"),
    (28000000, "0.11"),
    (30050000, "0.12"),
    (32400000, "0.13"),
    (35400000, "0.14"),
    (39100000, "0.15"),
    (43850000, "0.16"),
    (47800000, "0.17"),
    (51400000, "0.18"),
    (56300000, "0.19"),
    (62200000, "0.20"),
    (68600000, "0.21"),
    (77500000, "0.22"),
    (89000000, "0.23"),
    (103000000, "0.24"),
    (125000000, "0.25"),
    (157000000, "0.26"),
    (206000000, "0.27"),
    (337000000, "0.28"),
    (454000000, "0.29"),
    (550000000, "0.30"),
    (695000000, "0.31"),
    (910000000, "0.32"),
    (1400000000, "0.33"),
    (None, "0.34"),
]


TER_B = [
    (6200000, "0"),
    (6500000, "0.0025"),
    (6850000, "0.005"),
    (7300000, "0.0075"),
    (9200000, "0.01"),
    (10750000, "0.015"),
    (11250000, "0.02"),
    (11600000, "0.025"),
    (12600000, "0.03"),
    (13600000, "0.04"),
    (14950000, "0.05"),
    (16400000, "0.06"),
    (18450000, "0.07"),
    (21850000, "0.08"),
    (26000000, "0.09"),
    (27700000, "0.10"),
    (29350000, "0.11"),
    (31450000, "0.12"),
    (33950000, "0.13"),
    (37100000, "0.14"),
    (41100000, "0.15"),
    (45800000, "0.16"),
    (49500000, "0.17"),
    (53800000, "0.18"),
    (58500000, "0.19"),
    (64000000, "0.20"),
    (71000000, "0.21"),
    (80000000, "0.22"),
    (93000000, "0.23"),
    (109000000, "0.24"),
    (129000000, "0.25"),
    (163000000, "0.26"),
    (211000000, "0.27"),
    (374000000, "0.28"),
    (459000000, "0.29"),
    (555000000, "0.30"),
    (704000000, "0.31"),
    (957000000, "0.32"),
    (1405000000, "0.33"),
    (None, "0.34"),
]


TER_C = [
    (6600000, "0"),
    (6950000, "0.0025"),
    (7350000, "0.005"),
    (7800000, "0.0075"),
    (8850000, "0.01"),
    (9800000, "0.0125"),
    (10950000, "0.015"),
    (11200000, "0.0175"),
    (12050000, "0.02"),
    (12950000, "0.03"),
    (14150000, "0.04"),
    (15550000, "0.05"),
    (17050000, "0.06"),
    (19500000, "0.07"),
    (22700000, "0.08"),
    (26600000, "0.09"),
    (28100000, "0.10"),
    (30100000, "0.11"),
    (32600000, "0.12"),
    (35400000, "0.13"),
    (38900000, "0.14"),
    (43000000, "0.15"),
    (47400000, "0.16"),
    (51200000, "0.17"),
    (55800000, "0.18"),
    (60400000, "0.19"),
    (66700000, "0.20"),
    (74500000, "0.21"),
    (83200000, "0.22"),
    (95600000, "0.23"),
    (110000000, "0.24"),
    (134000000, "0.25"),
    (169000000, "0.26"),
    (221000000, "0.27"),
    (390000000, "0.28"),
    (463000000, "0.29"),
    (561000000, "0.30"),
    (709000000, "0.31"),
    (965000000, "0.32"),
    (1419000000, "0.33"),
    (None, "0.34"),
]


TER_TABLES = {
    "A": TER_A,
    "B": TER_B,
    "C": TER_C,
}


def decimal_value(value):
    return D(str(value or 0))


def round_rupiah(value):
    return decimal_value(value).quantize(
        D("1"),
        rounding=ROUND_HALF_UP,
    )


def get_ter_category(ptkp_status):
    if ptkp_status not in PTKP_TO_TER:
        raise ValueError(
            f"PTKP status tidak valid: {ptkp_status}"
        )

    return PTKP_TO_TER[ptkp_status]


def get_ter_rate(gross_income, category):
    gross_income = decimal_value(gross_income)

    for upper_limit, rate in TER_TABLES[category]:
        if upper_limit is None:
            return D(rate)

        if gross_income <= D(str(upper_limit)):
            return D(rate)

    return D("0")


def calculate_monthly_pph21(
    gross_income,
    ptkp_status,
):
    gross_income = decimal_value(gross_income)

    category = get_ter_category(
        ptkp_status
    )

    rate = get_ter_rate(
        gross_income,
        category,
    )

    amount = round_rupiah(
        gross_income * rate
    )

    return {
        "method": "TER",
        "category": category,
        "rate": rate,
        "gross_income": gross_income,
        "amount": amount,
    }


def calculate_progressive_tax(pkp):
    pkp = max(
        decimal_value(pkp),
        D("0"),
    )

    remaining = pkp
    tax = D("0")

    # Sampai Rp60 juta = 5%
    layer = min(
        remaining,
        D("60000000"),
    )
    tax += layer * D("0.05")
    remaining -= layer

    if remaining <= 0:
        return round_rupiah(tax)

    # >60 juta - 250 juta = 15%
    layer = min(
        remaining,
        D("190000000"),
    )
    tax += layer * D("0.15")
    remaining -= layer

    if remaining <= 0:
        return round_rupiah(tax)

    # >250 juta - 500 juta = 25%
    layer = min(
        remaining,
        D("250000000"),
    )
    tax += layer * D("0.25")
    remaining -= layer

    if remaining <= 0:
        return round_rupiah(tax)

    # >500 juta - 5 miliar = 30%
    layer = min(
        remaining,
        D("4500000000"),
    )
    tax += layer * D("0.30")
    remaining -= layer

    # >5 miliar = 35%
    if remaining > 0:
        tax += remaining * D("0.35")

    return round_rupiah(tax)


def calculate_final_period_pph21(
    annual_gross_income,
    employee_retirement_contribution,
    ptkp_status,
    previous_pph21,
    months_worked=12,
):
    annual_gross_income = decimal_value(
        annual_gross_income
    )

    employee_retirement_contribution = decimal_value(
        employee_retirement_contribution
    )

    previous_pph21 = decimal_value(
        previous_pph21
    )

    job_expense = min(
        annual_gross_income * D("0.05"),
        D("500000") * D(str(months_worked)),
    )

    annual_net_income = (
        annual_gross_income
        - job_expense
        - employee_retirement_contribution
    )

    annual_net_income = max(
        annual_net_income,
        D("0"),
    )

    ptkp = PTKP_VALUES[
        ptkp_status
    ]

    pkp = max(
        annual_net_income - ptkp,
        D("0"),
    )

    # PKP dibulatkan ke bawah ke ribuan penuh
    pkp = (
        pkp // D("1000")
    ) * D("1000")

    annual_tax = calculate_progressive_tax(
        pkp
    )

    final_tax = (
        annual_tax
        - previous_pph21
    )

    return {
        "method": "ANNUAL_PROGRESSIVE",
        "annual_gross_income": annual_gross_income,
        "job_expense": job_expense,
        "employee_retirement_contribution":
            employee_retirement_contribution,
        "annual_net_income": annual_net_income,
        "ptkp": ptkp,
        "pkp": pkp,
        "annual_tax": annual_tax,
        "previous_pph21": previous_pph21,
        "amount": round_rupiah(final_tax),
    }
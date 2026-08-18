from decimal import Decimal, ROUND_HALF_UP


D = Decimal


# =============================
# BPJS KETENAGAKERJAAN
# =============================

JHT_EMPLOYEE_RATE = D("0.02")
JHT_EMPLOYER_RATE = D("0.037")

JP_EMPLOYEE_RATE = D("0.01")
JP_EMPLOYER_RATE = D("0.02")

JKM_EMPLOYER_RATE = D("0.003")


JKK_RATES = {
    "VERY_LOW": D("0.0024"),
    "LOW": D("0.0054"),
    "MEDIUM": D("0.0089"),
    "HIGH": D("0.0127"),
    "VERY_HIGH": D("0.0174"),
}


# Batas upah JP terbaru mulai Maret 2026
JP_WAGE_CAP = D("11086300")


# =============================
# BPJS KESEHATAN
# =============================

HEALTH_EMPLOYEE_RATE = D("0.01")
HEALTH_EMPLOYER_RATE = D("0.04")

HEALTH_WAGE_CAP = D("12000000")


def decimal_value(value):
    return D(str(value or 0))


def round_rupiah(value):
    return decimal_value(value).quantize(
        D("1"),
        rounding=ROUND_HALF_UP,
    )


def calculate_bpjs(
    wage,
    jkk_risk="LOW",
    ketenagakerjaan_active=True,
    kesehatan_active=True,
):
    wage = max(
        decimal_value(wage),
        D("0"),
    )

    result = {
        "jht_employee": D("0"),
        "jht_employer": D("0"),
        "jp_employee": D("0"),
        "jp_employer": D("0"),
        "jkk_employer": D("0"),
        "jkm_employer": D("0"),
        "health_employee": D("0"),
        "health_employer": D("0"),
    }

    # =================================
    # BPJS Ketenagakerjaan
    # =================================

    if ketenagakerjaan_active:
        if jkk_risk not in JKK_RATES:
            raise ValueError(
                f"JKK risk tidak valid: {jkk_risk}"
            )

        jp_base = min(
            wage,
            JP_WAGE_CAP,
        )

        result["jht_employee"] = round_rupiah(
            wage * JHT_EMPLOYEE_RATE
        )

        result["jht_employer"] = round_rupiah(
            wage * JHT_EMPLOYER_RATE
        )

        result["jp_employee"] = round_rupiah(
            jp_base * JP_EMPLOYEE_RATE
        )

        result["jp_employer"] = round_rupiah(
            jp_base * JP_EMPLOYER_RATE
        )

        result["jkk_employer"] = round_rupiah(
            wage * JKK_RATES[jkk_risk]
        )

        result["jkm_employer"] = round_rupiah(
            wage * JKM_EMPLOYER_RATE
        )

    # =================================
    # BPJS Kesehatan
    # =================================

    if kesehatan_active:
        health_base = min(
            wage,
            HEALTH_WAGE_CAP,
        )

        result["health_employee"] = round_rupiah(
            health_base
            * HEALTH_EMPLOYEE_RATE
        )

        result["health_employer"] = round_rupiah(
            health_base
            * HEALTH_EMPLOYER_RATE
        )

    # Yang benar-benar memotong gaji karyawan
    result["employee_total"] = (
        result["jht_employee"]
        + result["jp_employee"]
        + result["health_employee"]
    )

    # Beban perusahaan
    result["employer_total"] = (
        result["jht_employer"]
        + result["jp_employer"]
        + result["jkk_employer"]
        + result["jkm_employer"]
        + result["health_employer"]
    )

    # Masuk bruto PPh21
    result["taxable_employer_contribution"] = (
        result["jkk_employer"]
        + result["jkm_employer"]
        + result["health_employer"]
    )

    # Pengurang pada kalkulasi tahunan PPh21
    result["employee_retirement_contribution"] = (
        result["jht_employee"]
        + result["jp_employee"]
    )

    return result
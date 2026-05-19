import re
from datetime import datetime


def validate_answer(question: str, answer: str):

    q = question.lower().strip()

    a = answer.strip()

    if not a:
        return False, "Field cannot be empty"

    # -------------------------------------------------
    # NAME
    # -------------------------------------------------
    if any(word in q for word in ["name", "பெயர்"]):

        # allow tamil + english letters
        if not re.fullmatch(r"[A-Za-z\u0B80-\u0BFF ]{2,50}", a):

            return False, "Enter valid name"

        return True, a.title()

    # -------------------------------------------------
    # DATE
    # -------------------------------------------------
    if any(word in q for word in [
        "date",
        "held on",
        "தேதி",
        "பிறந்த தேதி"
    ]):

        a = a.replace("-", "/")

        try:

            parsed = datetime.strptime(a, "%d/%m/%Y")

            return True, parsed.strftime("%d/%m/%Y")

        except ValueError:

            return False, "Enter date in DD/MM/YYYY format"

    # -------------------------------------------------
    # AGE
    # -------------------------------------------------
    if any(word in q for word in ["age", "வயது"]):

        if not a.isdigit():

            return False, "Enter valid age"

        age = int(a)

        if age < 1 or age > 120:

            return False, "Age must be between 1 and 120"

        return True, str(age)

    # -------------------------------------------------
    # MOBILE
    # -------------------------------------------------
    if any(word in q for word in [
        "mobile",
        "phone",
        "மொபைல்"
    ]):

        if not re.fullmatch(r"\d{10}", a):

            return False, "Enter valid 10-digit mobile number"

        return True, a

    # -------------------------------------------------
    # EMAIL
    # -------------------------------------------------
    if "email" in q:

        if not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", a):

            return False, "Enter valid email address"

        return True, a.lower()

    # -------------------------------------------------
    # YEAR
    # -------------------------------------------------
    if "year" in q:

        if not re.fullmatch(r"\d{4}", a):

            return False, "Enter valid 4-digit year"

        return True, a

    # -------------------------------------------------
    # GENDER
    # -------------------------------------------------
    if any(word in q for word in [
        "sex",
        "gender",
        "செக்ஸ்",
        "பாலினம்"
    ]):

        value = a.lower().strip()

        # male
        if value in [
            "male",
            "m",
            "boy",
            "ஆண்",
            "aan"
        ]:

            return True, "Male"

        # female
        if value in [
            "female",
            "f",
            "girl",
            "பெண்",
            "pen"
        ]:

            return True, "Female"

        # transgender
        if value in [
            "tg",
            "transgender",
            "third gender",
            "திருநங்கை"
        ]:

            return True, "TG"

        return False, "Enter Male / Female / TG"

    # -------------------------------------------------
    # CASTE
    # -------------------------------------------------
    if any(word in q for word in [
        "category",
        "caste",
        "சாதி",
        "community"
    ]):

        value = a.upper().strip()

        return True, value

    # -------------------------------------------------
    # ADDRESS
    # -------------------------------------------------
    if any(word in q for word in [
        "address",
        "முகவரி"
    ]):

        if len(a) < 5:

            return False, "Enter valid address"

        return True, a

    # -------------------------------------------------
    # DEFAULT
    # -------------------------------------------------
    return True, a
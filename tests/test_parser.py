from src.parser import extract_name


def test_name_with_email_on_same_line():
    text = (
        "Sumaiya Sultana Shaik    "
        "sultanasumaiya623@gmail.com\n"
        "Hyderabad, India\n"
        "Skills: Python, FastAPI"
    )

    assert extract_name(text) == "Sumaiya Sultana Shaik"


def test_name_split_across_lines():
    text = (
        "Prathamesh\n"
        "Patil\n"
        "prathameshpatil330@gmail.com\n"
        "Professional Summary"
    )

    assert extract_name(text) == "Prathamesh Patil"

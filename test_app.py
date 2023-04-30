import random
import string
from app import ServiceOrderDB
import pytest
import datetime
from Utilities.utils import load_agents

@pytest.fixture
def db():
    return ServiceOrderDB()


def random_string(length):
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


def random_service_order():
    return "".join(random.choice(string.digits) for _ in range(14))


def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    return start_date + datetime.timedelta(days=random_days)


@pytest.mark.parametrize("i", range(5))
def test_add_and_select_random_service_order(i, db):
    service_order = random_service_order()
    location = random_string(5)

    start_date = datetime.date(2023, 4, 1)
    end_date = datetime.date(2023, 4, 30)

    completion_date = random_date(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S")

    closed_by =  random.choice(load_agents(agent_names_only=True))
    status = random.choice(["GREEN", "YELLOW"])

    comments = random_string(50)
    db.create_table_users()
    # Add a random service order
    db.add_service_order(
        ServiceOrder=service_order,
        Location=location,
        CompletionDate=completion_date,
        ClosedBy=closed_by,
        Status=status,
        Comments=comments,
    )

    # Check if the service order was added
    result = db.select_unit(ServiceOrder=service_order)
    assert len(result) == 1

    # Check if the details match
    # Check if the details match
    assert (
        service_order,
        location,
        completion_date,
        closed_by,
        status,
        comments,
        "",
        "",
        "",
        "",
        "NO",
        0,
        "None",
        0,
        0,
        0
    )

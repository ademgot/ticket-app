import pytest
from pydantic import ValidationError

from api.dto.requests.pagination import Pagination
from api.dto.responses.page import Page


def test_pagination_defaults():
    pagination = Pagination()

    assert pagination.page == 1
    assert pagination.page_size == 50
    assert pagination.offset == 0


def test_pagination_offset():
    pagination = Pagination(page=3, page_size=20)

    assert pagination.offset == 40


@pytest.mark.parametrize(
    "kwargs",
    [
        {"page": 0},
        {"page": -1},
        {"page_size": 0},
        {"page_size": 101},
    ],
)
def test_pagination_rejects_out_of_range(kwargs):
    with pytest.raises(ValidationError):
        Pagination(**kwargs)


def test_pagination_as_query():
    pagination = Pagination.as_query(page=2, page_size=25)

    assert pagination.page == 2
    assert pagination.page_size == 25
    assert pagination.offset == 25


def test_page_holds_items_and_totals():
    page = Page[dict](items=[{"id": 1}], total=10, page=2, page_size=1)

    assert page.items == [{"id": 1}]
    assert page.total == 10


def test_page_allows_empty_items_when_total_is_known():
    page = Page[dict](items=[], total=8, page=3, page_size=50)

    assert page.items == []
    assert page.total == 8


@pytest.mark.parametrize(
    "kwargs",
    [
        {"total": -1, "page": 1, "page_size": 50},
        {"total": 0, "page": 0, "page_size": 50},
        {"total": 0, "page": 1, "page_size": 0},
        {"total": 0, "page": 1, "page_size": 101},
    ],
)
def test_page_rejects_out_of_range(kwargs):
    with pytest.raises(ValidationError):
        Page[dict](items=[], **kwargs)

from fastapi import APIRouter, Depends

from api.dto.requests.pagination import Pagination
from api.dto.requests.tax_rate import CreateTaxRate, UpdateTaxRate
from api.dto.responses.page import Page
from api.dto.responses.tax_rate import TaxRateResponse
from api.rest.repos.tax_rate import TaxRateRepo


router = APIRouter(prefix="/tax-rates", tags=["tax-rates"])


@router.get("/")
def get(pagination: Pagination = Depends(Pagination.as_query)) -> Page[TaxRateResponse]:
    return TaxRateRepo.get(pagination)


@router.get("/{tax_rate_id}")
def get_by_id(tax_rate_id: int):
    return TaxRateRepo.get_by_id(tax_rate_id)


@router.post("/")
def create(tax_rate: CreateTaxRate):
    return TaxRateRepo.create(tax_rate)


@router.patch("/{tax_rate_id}")
def update(tax_rate_id: int, tax_rate: UpdateTaxRate):
    return TaxRateRepo.update_by_id(tax_rate_id, tax_rate)


@router.delete("/{tax_rate_id}")
def delete(tax_rate_id: int):
    return TaxRateRepo.delete_by_id(tax_rate_id)

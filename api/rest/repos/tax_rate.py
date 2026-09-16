from sqlite3 import DatabaseError

from api.core.sql_db import get_con
from api.core.utils.common import generate_sql_update_query_setter
from api.dto.requests.tax_rate import CreateTaxRate, UpdateTaxRate
from api.rest.models.tax_rate import TaxRate


class TaxRateRepo:
    @staticmethod
    def get() -> list[TaxRate]:
        with get_con() as con:
            items = con.execute("SELECT * FROM tax_rates").fetchall()
            return [TaxRate.model_validate(dict(item)) for item in items]

    @staticmethod
    def get_by_id(tax_rate_id: int | None) -> TaxRate | None:
        with get_con() as con:
            item = con.execute(
                "SELECT * FROM tax_rates WHERE id = ?", (tax_rate_id,)
            ).fetchone()
            return TaxRate.model_validate(dict(item)) if item else None

    @staticmethod
    def create(tax_rate: CreateTaxRate) -> TaxRate | None:
        with get_con() as con:
            cursor = con.execute(
                """
                INSERT INTO tax_rates(
                    jurisdiction, tax_type, rate, effective_from, effective_to
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    tax_rate.jurisdiction,
                    tax_rate.tax_type,
                    tax_rate.rate,
                    tax_rate.effective_from,
                    tax_rate.effective_to,
                ),
            )
            tax_rate_id = cursor.lastrowid
            con.commit()
        return TaxRateRepo.get_by_id(tax_rate_id)

    @staticmethod
    def update_by_id(tax_rate_id: int, tax_rate: UpdateTaxRate) -> TaxRate | None:
        with get_con() as con:
            set_q, vals = generate_sql_update_query_setter(tax_rate)
            if set_q is not None:
                vals.append(tax_rate_id)
                con.execute("UPDATE tax_rates " + set_q + " WHERE id = ?", vals)
                con.commit()
        return TaxRateRepo.get_by_id(tax_rate_id)

    @staticmethod
    def delete_by_id(tax_rate_id: int) -> bool:
        with get_con() as con:
            try:
                cursor = con.execute(
                    "DELETE FROM tax_rates WHERE id = ?", (tax_rate_id,)
                )
                con.commit()
                return cursor.rowcount > 0
            except DatabaseError:
                con.rollback()
                return False

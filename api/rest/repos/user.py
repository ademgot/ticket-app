from api.core.sql_db import get_con
from api.rest.models.user import User
from api.rest.repos.base import BaseRepo
from api.dto.requests.user import CreateUser, UpdateUser
from api.dto.requests.pagination import Pagination
from api.dto.responses.page import Page
from api.dto.responses.user import UserResponse
from api.core.utils.common import generate_sql_update_query_setter
from typing import Optional
from sqlite3 import DatabaseError


class UserRepo:
    @staticmethod
    def get(pagination: Pagination) -> Page[UserResponse]:
        rows, total = BaseRepo.get_page("users", pagination)
        return Page(
            items=[UserResponse.model_validate(row) for row in rows],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    @staticmethod
    def get_by_id(user_id: Optional[int]) -> Optional[User]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            item = cursor.fetchone()
            if item:
                item = dict(item)
                return User.model_validate(item)
            return None

    @staticmethod
    def create(user: CreateUser) -> Optional[User]:
        with get_con() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO users(name, email) VALUES (%s, %s) RETURNING id",
                (user.name, user.email),
            )
            user_id = cursor.fetchone()["id"]
            con.commit()
        return UserRepo.get_by_id(user_id)

    @staticmethod
    def update_by_id(user_id: Optional[int], user: UpdateUser) -> Optional[User]:
        with get_con() as con:
            cursor = con.cursor()
            set_q, vals = generate_sql_update_query_setter(user)
            if set_q is not None:
                vals.append(user_id)
                cursor.execute("UPDATE users " + set_q + " WHERE id = %s", vals)
                con.commit()

            return UserRepo.get_by_id(user_id)

    @staticmethod
    def delete_by_id(user_id: Optional[int]) -> bool:
        with get_con() as con:
            cursor = con.cursor()
            try:
                cursor.execute("BEGIN")
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                con.commit()
                rows = cursor.rowcount
                return rows > 0
            except DatabaseError:
                con.rollback()
                return False
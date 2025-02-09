from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):
    ADD_NOTIFICATION = State()
    UPDATE_QUERY = State()
    UPDATE_MIN_PRICE = State()
    UPDATE_MAX_PRICE = State()
    BROADCAST = State()

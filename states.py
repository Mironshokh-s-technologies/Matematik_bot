"""
Matematika Ustasi Telegram Boti uchun FSM (Finite State Machine) holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class FractionStates(StatesGroup):
    """Kasrlar bilan ishlash bo'limi holatlari."""
    # Bitta kasr talab qilinadigan amallar (Aralash->Noto'g'ri, Noto'g'ri->Aralash, Turini aniqlash, Qisqartirish)
    waiting_single_fraction = State()

    # Ikkita kasr talab qilinadigan amallar (Umumiy maxraj, Qo'shish, Ayirish, Ko'paytirish, Bo'lish)
    waiting_first_fraction = State()
    waiting_second_fraction = State()


class ArithmeticStates(StatesGroup):
    """Asosiy menyudagi arifmetik amallar holatlari (+, -, *, /)."""
    waiting_first_number = State()
    waiting_second_number = State()


class PercentStates(StatesGroup):
    """Foiz hisoblash amallari holatlari."""
    waiting_first_value = State()
    waiting_second_value = State()

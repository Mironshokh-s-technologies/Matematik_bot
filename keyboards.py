"""
Matematika Ustasi Telegram Boti uchun Klaviaturalar (Reply va Inline).
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Foydalanuvchi botni ishga tushirganda ko'rinadigan asosiy Reply tugmalar:
    1. 🧮 Kasrlar bilan ishlash
    2. ➗ Bo'lish
    3. ➖ Ayirish
    4. ➕ Qo'shish
    5. 📊 Foiz hisoblash
    6. ✖️ Ko'paytirish
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🧮 Kasrlar bilan ishlash"),
            ],
            [
                KeyboardButton(text="➕ Qo'shish"),
                KeyboardButton(text="➖ Ayirish"),
            ],
            [
                KeyboardButton(text="✖️ Ko'paytirish"),
                KeyboardButton(text="➗ Bo'lish"),
            ],
            [
                KeyboardButton(text="📊 Foiz hisoblash"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Quyidagi bo'limlardan birini tanlang...",
    )
    return keyboard


def get_fractions_inline_keyboard() -> InlineKeyboardMarkup:
    """
    'Kasrlar bilan ishlash' tanlanganda chiqadigan 9 ta quyi inline tugma:
    1. Aralash kasrni noto'g'riga aylantirish
    2. Noto'g'ri kasrni aralashga aylantirish
    3. Kasr turini aniqlash
    4. Qisqartirish
    5. Umumiy maxraj berish
    6. Qo'shish
    7. Ayirish
    8. Bo'lish
    9. Ko'paytirish
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="🔄 Aralash ➔ Noto'g'ri kasr",
                callback_data="frac_mixed_to_imp"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔄 Noto'g'ri ➔ Aralash kasr",
                callback_data="frac_imp_to_mixed"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔍 Kasr turini aniqlash",
                callback_data="frac_identify"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✂️ Kasrni qisqartirish",
                callback_data="frac_simplify"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚖️ Umumiy maxraj berish",
                callback_data="frac_common_den"
            ),
        ],
        [
            InlineKeyboardButton(
                text="➕ Qo'shish",
                callback_data="frac_add"
            ),
            InlineKeyboardButton(
                text="➖ Ayirish",
                callback_data="frac_sub"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✖️ Ko'paytirish",
                callback_data="frac_mul"
            ),
            InlineKeyboardButton(
                text="➗ Bo'lish",
                callback_data="frac_div"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Asosiy menyu",
                callback_data="back_to_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_percent_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Foiz hisoblash bo'limi uchun qulay inline menyu.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="1️⃣ Sonning foizini topish (A ning P% i)",
                callback_data="pct_part"
            ),
        ],
        [
            InlineKeyboardButton(
                text="2️⃣ Son boshqa sonning necha foizi",
                callback_data="pct_ratio"
            ),
        ],
        [
            InlineKeyboardButton(
                text="3️⃣ Sonni foizga oshirish (A + P%)",
                callback_data="pct_inc"
            ),
        ],
        [
            InlineKeyboardButton(
                text="4️⃣ Sonni foizga kamaytirish (A - P%)",
                callback_data="pct_dec"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Asosiy menyu",
                callback_data="back_to_main"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cancel_inline_keyboard() -> InlineKeyboardMarkup:
    """Amalni bekor qilish uchun inline tugma."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Bekor qilish",
                    callback_data="cancel_action"
                )
            ]
        ]
    )


def get_back_to_fractions_keyboard() -> InlineKeyboardMarkup:
    """Kasrlar menyusiga qaytish tugmasi."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧮 Kasrlar menyusi",
                    callback_data="back_to_fractions"
                ),
                InlineKeyboardButton(
                    text="🏠 Asosiy menyu",
                    callback_data="back_to_main"
                ),
            ]
        ]
    )

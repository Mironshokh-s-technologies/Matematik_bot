"""
=============================================================================
LOYIHA: "Matematika Ustasi" Telegram Boti
TEXNOLOGIYALAR: Python 3.10+, aiogram 3.x, fractions moduli
MUALLIF: Senior Python Dasturchisi & Telegram Bot Arxitektori
=============================================================================
Ushbu bot kasrlar, arifmetik amallar va foizlarni yuqori aniqlikda,
bosqichma-bosqich yechimlari bilan hisoblab beradi.
=============================================================================
"""

import asyncio
import logging
import re
import sys
from typing import Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# Modullardan import qilish
from keyboards import (
    get_back_to_fractions_keyboard,
    get_cancel_inline_keyboard,
    get_fractions_inline_keyboard,
    get_main_reply_keyboard,
    get_percent_inline_keyboard,
)
from math_engine import (
    FractionParseError,
    arithmetic_stepwise,
    calculate_fraction_operation,
    common_denominator_stepwise,
    identify_fraction_type,
    improper_to_mixed_stepwise,
    mixed_to_improper_stepwise,
    parse_fraction,
    parse_two_fractions,
    percent_calculate_stepwise,
    simplify_fraction_stepwise,
)
from states import ArithmeticStates, FractionStates, PercentStates

# =============================================================================
# BOT SOZLAMALARI VA TOKEN
# =============================================================================
# DIQQAT: Quyidagi TOKEN o'zgaruvchisiga Telegram @BotFather dan olingan
# o'z bot tokeningizni joylashtiring!
TOKEN = "8788736972:AAHbsG0XFQPpclp7py_2h76YM39tMZIXXU4"
# =============================================================================

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("MatematikaUstasiBot")

router = Router()


# =============================================================================
# ASOSIY BUYRUQLAR: /start VA /help
# =============================================================================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    /start buyrug'i uchun handler.
    Foydalanuvchiga xush kelibsiz xabari va asosiy menyuni chiqaradi.
    """
    await state.clear()
    first_name = message.from_user.first_name if message.from_user else "Foydalanuvchi"

    text = (
        f"Assalomu alaykum, hurmatli <b>{first_name}</b>!\n\n"
        f"🤖 <b>«Matematika Ustasi»</b> botiga xush kelibsiz!\n\n"
        f"Men kasrlar ustida murakkab amallarni bajarish, aralash va noto'g'ri "
        f"kasrlarni aylantirish, qisqartirish, umumiy maxraj berish hamda foiz va "
        f"arifmetik amallarni <b>bosqichma-bosqich</b> tushuntirib berishda yordamchiman.\n\n"
        f"👇 <i>Kerakli bo'limni quyidagi menyudan tanlang:</i>"
    )
    await message.answer(
        text=text,
        reply_markup=get_main_reply_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    """
    /help buyrug'i uchun handler.
    Kasrlarni kiritish qoidalari va namunalar.
    """
    help_text = (
        "📚 <b>«Matematika Ustasi» botidan foydalanish qo'llanmasi:</b>\n\n"
        "🔹 <b>Kasrlarni kiritish formatlari:</b>\n"
        "• <i>Oddiy kasr:</i> <code>3/4</code>, <code>5/2</code>, <code>-7/8</code>\n"
        "• <i>Aralash kasr (probel bilan):</i> <code>2 3/4</code>, <code>1 1/1</code>\n"
        "• <i>Aralash kasr (matn bilan):</i> <code>2 butun 3/4</code>, <code>1 butun 1/1</code>\n"
        "• <i>Butun son:</i> <code>5</code>, <code>-3</code>\n"
        "• <i>O'nli kasr:</i> <code>2.5</code> yoki <code>0.75</code>\n\n"
        "🔹 <b>Kasrlar ustida amallar:</b>\n"
        "Siz ikkita kasrni ketma-ket kiritishingiz yoki bitta xabarda "
        "<code>1/4 + 2/3</code> yoki <code>1/4 va 2/3</code> deb yuborishingiz mumkin.\n\n"
        "🔹 <b>Asosiy bo'limlar:</b>\n"
        "1. 🧮 <b>Kasrlar bilan ishlash:</b> 9 ta maxsus operatsiya.\n"
        "2. ➕ / ➖ / ✖️ / ➗: Standart arifmetik amallar.\n"
        "3. 📊 <b>Foiz hisoblash:</b> 4 xil foiz amallari.\n\n"
        "Agar biror amaldan chiqmoqchi bo'lsangiz, «❌ Bekor qilish» tugmasini bosing."
    )
    await message.answer(text=help_text, reply_markup=get_main_reply_keyboard())


# =============================================================================
# ASOSIY REPLY TUGMALAR HANDLERLARI
# =============================================================================
@router.message(F.text == "🧮 Kasrlar bilan ishlash")
async def menu_fractions(message: Message, state: FSMContext):
    """'Kasrlar bilan ishlash' menyusi."""
    await state.clear()
    text = (
        "🧮 <b>Kasrlar bilan ishlash bo'limi:</b>\n\n"
        "Quyidagi amallardan birini tanlang:\n"
        "1. 🔄 <b>Aralash kasrni noto'g'riga aylantirish</b> (masalan: 2 3/4 ➔ 11/4)\n"
        "2. 🔄 <b>Noto'g'ri kasrni aralashga aylantirish</b> (masalan: 11/4 ➔ 2 3/4)\n"
        "3. 🔍 <b>Kasr turini aniqlash</b> (to'g'ri, noto'g'ri, aralash kasr)\n"
        "4. ✂️ <b>Kasrni qisqartirish</b> (masalan: 8/12 ➔ 2/3)\n"
        "5. ⚖️ <b>Umumiy maxraj berish</b> (masalan: 1/4 va 2/3 ➔ 3/12 va 8/12)\n"
        "6. ➕ / ➖ / ✖️ / ➗ <b>Kasrlarni hisoblash</b>\n\n"
        "<i>Bajarmoqchi bo'lgan amalingiz tugmasini bosing:</i>"
    )
    await message.answer(text=text, reply_markup=get_fractions_inline_keyboard())


@router.message(F.text.in_({"➕ Qo'shish", "➖ Ayirish", "✖️ Ko'paytirish", "➗ Bo'lish"}))
async def menu_arithmetic(message: Message, state: FSMContext):
    """Asosiy menyudagi arifmetik amallar (+, -, *, /)."""
    await state.clear()
    symbol_map = {
        "➕ Qo'shish": ("+", "qo'shish"),
        "➖ Ayirish": ("-", "ayirish"),
        "✖️ Ko'paytirish": ("*", "ko'paytirish"),
        "➗ Bo'lish": ("/", "bo'lish"),
    }
    op, op_name = symbol_map[message.text]

    await state.set_state(ArithmeticStates.waiting_first_number)
    await state.update_data(op=op, op_name=op_name)

    text = (
        f"🔢 <b>Arifmetik {op_name} amali:</b>\n\n"
        f"1-sonni kiriting (masalan: <code>25</code> yoki <code>12.5</code>):\n"
        f"<i>Yoki bitta xabarda butun ifodani yuboring (masalan: <code>25 {op} 10</code>):</i>"
    )
    await message.answer(text=text, reply_markup=get_cancel_inline_keyboard())


@router.message(F.text == "📊 Foiz hisoblash")
async def menu_percent(message: Message, state: FSMContext):
    """'Foiz hisoblash' menyusi."""
    await state.clear()
    text = (
        "📊 <b>Foiz hisoblash bo'limi:</b>\n\n"
        "Quyidagi foiz amallaridan birini tanlang:\n"
        "1️⃣ <b>Sonning foizini topish</b> (masalan: 200 ning 15% i)\n"
        "2️⃣ <b>Son ikkinchi sonning necha foizi</b> (masalan: 25 soni 100 ning necha foizi)\n"
        "3️⃣ <b>Sonni foizga oshirish</b> (masalan: 500 ga 20% qo'shish)\n"
        "4️⃣ <b>Sonni foizga kamaytirish</b> (masalan: 500 dan 20% ayirish)"
    )
    await message.answer(text=text, reply_markup=get_percent_inline_keyboard())


# =============================================================================
# INLINE TUGMALAR CALLBACK HANDLERLARI (KASRLAR)
# =============================================================================
@router.callback_query(F.data == "frac_mixed_to_imp")
async def cb_mixed_to_imp(callback: CallbackQuery, state: FSMContext):
    """Aralash kasrni noto'g'ri kasrga aylantirish tugmasi."""
    await callback.answer()
    await state.set_state(FractionStates.waiting_single_fraction)
    await state.update_data(subaction="mixed_to_imp")

    text = (
        "🔄 <b>Aralash kasrni noto'g'ri kasrga aylantirish:</b>\n\n"
        "Iltimos, aralash kasrni kiriting.\n\n"
        "🔹 <i>Namunalar:</i>\n"
        "• <code>2 3/4</code>\n"
        "• <code>1 butun 1/1</code>\n"
        "• <code>3 butun 2/5</code>\n"
        "• <code>-2 1/3</code>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


@router.callback_query(F.data == "frac_imp_to_mixed")
async def cb_imp_to_mixed(callback: CallbackQuery, state: FSMContext):
    """Noto'g'ri kasrni aralash kasrga aylantirish tugmasi."""
    await callback.answer()
    await state.set_state(FractionStates.waiting_single_fraction)
    await state.update_data(subaction="imp_to_mixed")

    text = (
        "🔄 <b>Noto'g'ri kasrni aralash kasrga aylantirish:</b>\n\n"
        "Iltimos, noto'g'ri kasrni kiriting (surati maxrajidan katta yoki teng bo'lgan kasr).\n\n"
        "🔹 <i>Namunalar:</i>\n"
        "• <code>11/4</code>\n"
        "• <code>17/5</code>\n"
        "• <code>25/8</code>\n"
        "• <code>-14/3</code>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


@router.callback_query(F.data == "frac_identify")
async def cb_identify(callback: CallbackQuery, state: FSMContext):
    """Kasr turini aniqlash tugmasi."""
    await callback.answer()
    await state.set_state(FractionStates.waiting_single_fraction)
    await state.update_data(subaction="identify")

    text = (
        "🔍 <b>Kasr turini aniqlash:</b>\n\n"
        "Istalgan kasr yoki sonni kiriting. Men uning turini (to'g'ri, noto'g'ri, "
        "aralash), qisqarishini va o'nli qiymatini tahlil qilib beraman.\n\n"
        "🔹 <i>Namunalar:</i>\n"
        "• <code>3/4</code>, <code>11/4</code>, <code>2 3/4</code>, <code>8/12</code>, <code>5</code>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


@router.callback_query(F.data == "frac_simplify")
async def cb_simplify(callback: CallbackQuery, state: FSMContext):
    """Kasrni qisqartirish tugmasi."""
    await callback.answer()
    await state.set_state(FractionStates.waiting_single_fraction)
    await state.update_data(subaction="simplify")

    text = (
        "✂️ <b>Kasrni qisqartirish:</b>\n\n"
        "Qisqartirmoqchi bo'lgan kasringizni kiriting.\n"
        "Surat va maxrajning EKUBi topilib, bosqichma-bosqich qisqartiriladi.\n\n"
        "🔹 <i>Namunalar:</i>\n"
        "• <code>8/12</code>\n"
        "• <code>24/36</code>\n"
        "• <code>15/45</code>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


@router.callback_query(F.data == "frac_common_den")
async def cb_common_den(callback: CallbackQuery, state: FSMContext):
    """Umumiy maxraj berish tugmasi."""
    await callback.answer()
    await state.set_state(FractionStates.waiting_first_fraction)
    await state.update_data(subaction="common_den")

    text = (
        "⚖️ <b>Kasrlarga umumiy maxraj berish:</b>\n\n"
        "1-kasrni kiriting (masalan: <code>1/4</code> yoki <code>1 1/2</code>):\n\n"
        "💡 <i>Ikkala kasrni bitta xabarda yuborishingiz ham mumkin:</i>\n"
        "• <code>1/4 va 2/3</code>\n"
        "• <code>1/4, 2/3</code>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


@router.callback_query(F.data.in_({"frac_add", "frac_sub", "frac_mul", "frac_div"}))
async def cb_fraction_ops(callback: CallbackQuery, state: FSMContext):
    """Kasrlar ustida amallar (+, -, *, /) inline tugmalari."""
    await callback.answer()
    op_map = {
        "frac_add": ("+", "qo'shish"),
        "frac_sub": ("-", "ayirish"),
        "frac_mul": ("*", "ko'paytirish"),
        "frac_div": ("/", "bo'lish"),
    }
    op, op_title = op_map[callback.data]

    await state.set_state(FractionStates.waiting_first_fraction)
    await state.update_data(subaction="operation", op=op, op_title=op_title)

    text = (
        f"🧮 <b>Kasrlarni {op_title}:</b>\n\n"
        f"1-kasrni kiriting (masalan: <code>1/4</code> yoki <code>1 1/2</code>):\n\n"
        f"💡 <i>Yoki bitta xabarda butun ifodani yuboring:</i>\n"
        f"• <code>1/4 {op} 2/3</code>\n"
        f"• <code>1 1/2 {op} 3/4</code>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


# =============================================================================
# INLINE TUGMALAR CALLBACK HANDLERLARI (FOIZ AMALLARI)
# =============================================================================
@router.callback_query(F.data.in_({"pct_part", "pct_ratio", "pct_inc", "pct_dec"}))
async def cb_percent_modes(callback: CallbackQuery, state: FSMContext):
    """Foiz hisoblash amallari."""
    await callback.answer()
    mode_map = {
        "pct_part": (
            "part_of_number",
            "Sonning foizini topish",
            "Asosiy sonni kiriting (masalan: <code>200</code>):"
        ),
        "pct_ratio": (
            "number_ratio",
            "Son ikkinchi sonning necha foizi",
            "1-sonni kiriting (masalan: <code>25</code>):"
        ),
        "pct_inc": (
            "increase_by_percent",
            "Sonni foizga oshirish",
            "Boshlang'ich sonni kiriting (masalan: <code>500</code>):"
        ),
        "pct_dec": (
            "decrease_by_percent",
            "Sonni foizga kamaytirish",
            "Boshlang'ich sonni kiriting (masalan: <code>500</code>):"
        ),
    }

    mode, title, prompt = mode_map[callback.data]
    await state.set_state(PercentStates.waiting_first_value)
    await state.update_data(pct_mode=mode, pct_title=title)

    text = f"📊 <b>{title}:</b>\n\n{prompt}"
    await callback.message.edit_text(text=text, reply_markup=get_cancel_inline_keyboard())


# =============================================================================
# NAVIGATSIYA: BEKOR QILISH VA ORQAGA QAYTISH
# =============================================================================
@router.callback_query(F.data == "cancel_action")
async def cb_cancel_action(callback: CallbackQuery, state: FSMContext):
    """Joriy amalni bekor qilish."""
    await callback.answer("Amal bekor qilindi.")
    await state.clear()
    await callback.message.edit_text(
        "❌ Amal bekor qilindi.\n\nKerakli bo'limni tanlash uchun asosiy menyudan foydalanishingiz mumkin."
    )


@router.callback_query(F.data == "back_to_main")
async def cb_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Asosiy menyuga qaytish."""
    await callback.answer()
    await state.clear()
    text = (
        "🏠 <b>Asosiy menyu:</b>\n\n"
        "Quyidagi tugmalar orqali kerakli bo'limni tanlang:"
    )
    await callback.message.edit_text(text=text)


@router.callback_query(F.data == "back_to_fractions")
async def cb_back_to_fractions(callback: CallbackQuery, state: FSMContext):
    """Kasrlar menyusiga qaytish."""
    await callback.answer()
    await state.clear()
    text = (
        "🧮 <b>Kasrlar bilan ishlash bo'limi:</b>\n\n"
        "Quyidagi amallardan birini tanlang:"
    )
    await callback.message.edit_text(text=text, reply_markup=get_fractions_inline_keyboard())


# =============================================================================
# FSM: BITTA KASR KUTILAYOTGAN HOLAT
# =============================================================================
@router.message(FractionStates.waiting_single_fraction)
async def process_single_fraction(message: Message, state: FSMContext):
    """Aralash->Noto'g'ri, Noto'g'ri->Aralash, Aniqlash, Qisqartirish uchun handler."""
    data = await state.get_data()
    subaction = data.get("subaction")

    try:
        parsed = parse_fraction(message.text)
    except FractionParseError as e:
        await message.answer(
            f"{str(e)}\n\nIltimos, qaytadan urinib ko'ring:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return
    except Exception as e:
        logger.error(f"Xatolik single fraction: {e}", exc_info=True)
        await message.answer(
            "❌ Kutilmagan xatolik yuz berdi. Iltimos, qiymatni to'g'ri formatda qayta kiriting:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    # Mantiqni bajarish
    if subaction == "mixed_to_imp":
        ans = mixed_to_improper_stepwise(parsed)
    elif subaction == "imp_to_mixed":
        ans = improper_to_mixed_stepwise(parsed)
    elif subaction == "identify":
        ans = identify_fraction_type(parsed)
    elif subaction == "simplify":
        ans = simplify_fraction_stepwise(parsed)
    else:
        ans = "Noma'lum amal"

    await state.clear()
    await message.answer(text=ans, reply_markup=get_back_to_fractions_keyboard())


# =============================================================================
# FSM: IKKITA KASR KUTILAYOTGAN HOLAT (1-va 2-KASR)
# =============================================================================
@router.message(FractionStates.waiting_first_fraction)
async def process_first_fraction(message: Message, state: FSMContext):
    """1-kasr kutilayotgan holat. Agar foydalanuvchi birdan 2 ta kasr yozsa, uni ham eplaydi."""
    data = await state.get_data()
    subaction = data.get("subaction")
    op = data.get("op", "+")

    # Avval tekshiramiz: bitta xabarda ikkita kasr yuborilganmi?
    try:
        f1, f2, detected_op = parse_two_fractions(message.text)
        # Agar bitta xabarda ikkita kasr berilgan bo'lsa
        active_op = detected_op if detected_op else op
        if subaction == "common_den":
            ans = common_denominator_stepwise(f1, f2)
        else:
            ans = calculate_fraction_operation(f1, f2, active_op)

        await state.clear()
        await message.answer(text=ans, reply_markup=get_back_to_fractions_keyboard())
        return
    except Exception:
        # Bitta xabarda ikkita kasr bo'lmasa, demak bu faqat 1-kasr
        pass

    # Faqat 1-kasr sifatida tekshiramiz
    try:
        parsed1 = parse_fraction(message.text)
    except FractionParseError as e:
        await message.answer(
            f"{str(e)}\n\nIltimos, 1-kasrni qayta kiriting:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return
    except Exception as e:
        logger.error(f"Xatolik 1-kasr parse: {e}", exc_info=True)
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, kasrni to'g'ri kiriting:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    # 1-kasr muvaffaqiyatli qabul qilindi, endi 2-kasrni kutamiz
    await state.update_data(first_fraction=parsed1)
    await state.set_state(FractionStates.waiting_second_fraction)

    await message.answer(
        f"✅ 1-kasr qabul qilindi: <b>{parsed1.to_display_string()}</b>\n\n"
        f"Endi <b>2-kasrni</b> kiriting (masalan: <code>2/3</code> yoki <code>1 1/4</code>):",
        reply_markup=get_cancel_inline_keyboard()
    )


@router.message(FractionStates.waiting_second_fraction)
async def process_second_fraction(message: Message, state: FSMContext):
    """2-kasr kutilayotgan holat."""
    data = await state.get_data()
    subaction = data.get("subaction")
    op = data.get("op", "+")
    parsed1 = data.get("first_fraction")

    try:
        parsed2 = parse_fraction(message.text)
    except FractionParseError as e:
        await message.answer(
            f"{str(e)}\n\nIltimos, 2-kasrni qayta kiriting:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return
    except Exception as e:
        logger.error(f"Xatolik 2-kasr parse: {e}", exc_info=True)
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, 2-kasrni to'g'ri kiriting:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    if subaction == "common_den":
        ans = common_denominator_stepwise(parsed1, parsed2)
    else:
        ans = calculate_fraction_operation(parsed1, parsed2, op)

    await state.clear()
    await message.answer(text=ans, reply_markup=get_back_to_fractions_keyboard())


# =============================================================================
# FSM: ARIFMETIK AMALLAR (+, -, *, /)
# =============================================================================
@router.message(ArithmeticStates.waiting_first_number)
async def process_arithmetic_first(message: Message, state: FSMContext):
    """Arifmetik 1-son yoki to'liq ifoda (masalan: '25 + 75')."""
    data = await state.get_data()
    op = data.get("op", "+")

    text = message.text.strip()

    # Agar foydalanuvchi butun ifodani yozgan bo'lsa (masalan: "25 + 75" yoki "10 * 5")
    expr_pattern = rf"^\s*([+-]?\d+(?:\.\d+)?)\s*[{re.escape(op)}]\s*([+-]?\d+(?:\.\d+)?)\s*$"
    m = re.match(expr_pattern, text)
    if m:
        try:
            a = float(m.group(1))
            b = float(m.group(2))
            ans = arithmetic_stepwise(a, b, op)
            await state.clear()
            await message.answer(text=ans, reply_markup=get_main_reply_keyboard())
            return
        except Exception as e:
            logger.error(f"Ifoda hisoblashda xato: {e}")

    # Agar bitta son bo'lsa
    try:
        clean_num = text.replace(",", ".")
        val1 = float(clean_num)
    except ValueError:
        await message.answer(
            "❌ <b>Noto'g'ri son kiritildi!</b>\n"
            "Iltimos, haqiqiy son kiriting (masalan: <code>25</code> yoki <code>14.2</code>):",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    await state.update_data(first_num=val1)
    await state.set_state(ArithmeticStates.waiting_second_number)

    s1 = int(val1) if val1.is_integer() else val1
    await message.answer(
        f"✅ 1-son qabul qilindi: <b>{s1}</b>\n\n"
        f"Endi <b>2-sonni</b> kiriting:",
        reply_markup=get_cancel_inline_keyboard()
    )


@router.message(ArithmeticStates.waiting_second_number)
async def process_arithmetic_second(message: Message, state: FSMContext):
    """Arifmetik 2-son."""
    data = await state.get_data()
    val1 = data.get("first_num")
    op = data.get("op", "+")

    text = message.text.strip().replace(",", ".")
    try:
        val2 = float(text)
    except ValueError:
        await message.answer(
            "❌ <b>Noto'g'ri son kiritildi!</b>\n"
            "Iltimos, haqiqiy son kiriting (masalan: <code>10</code> yoki <code>3.5</code>):",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    ans = arithmetic_stepwise(val1, val2, op)
    await state.clear()
    await message.answer(text=ans, reply_markup=get_main_reply_keyboard())


# =============================================================================
# FSM: FOIZ HISOBLASH AMALLARI
# =============================================================================
@router.message(PercentStates.waiting_first_value)
async def process_percent_first(message: Message, state: FSMContext):
    """Foiz hisoblashda 1-qiymat."""
    data = await state.get_data()
    mode = data.get("pct_mode")
    title = data.get("pct_title")

    text = message.text.strip().replace(",", ".")
    try:
        val1 = float(text)
    except ValueError:
        await message.answer(
            "❌ <b>Noto'g'ri son kiritildi!</b>\nIltimos, son kiriting (masalan: <code>200</code>):",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    await state.update_data(val1=val1)
    await state.set_state(PercentStates.waiting_second_value)

    if mode == "part_of_number":
        prompt2 = "Endi <b>foiz miqdorini</b> kiriting (masalan: <code>15</code> foiz uchun <code>15</code>):"
    elif mode == "number_ratio":
        prompt2 = "Endi <b>2-sonni (taqqoslanadigan asosiy sonni)</b> kiriting:"
    elif mode in ["increase_by_percent", "decrease_by_percent"]:
        prompt2 = "Endi <b>necha foizga o'zgarishini</b> kiriting (masalan: <code>20</code>):"
    else:
        prompt2 = "2-qiymatni kiriting:"

    s1 = int(val1) if val1.is_integer() else val1
    await message.answer(
        f"✅ 1-qiymat qabul qilindi: <b>{s1}</b>\n\n{prompt2}",
        reply_markup=get_cancel_inline_keyboard()
    )


@router.message(PercentStates.waiting_second_value)
async def process_percent_second(message: Message, state: FSMContext):
    """Foiz hisoblashda 2-qiymat."""
    data = await state.get_data()
    mode = data.get("pct_mode")
    val1 = data.get("val1")

    text = message.text.strip().replace(",", ".").replace("%", "")
    try:
        val2 = float(text)
    except ValueError:
        await message.answer(
            "❌ <b>Noto'g'ri son kiritildi!</b>\nIltimos, son kiriting:",
            reply_markup=get_cancel_inline_keyboard()
        )
        return

    ans = percent_calculate_stepwise(mode, val1, val2)
    await state.clear()
    await message.answer(text=ans, reply_markup=get_main_reply_keyboard())


# =============================================================================
# SMART AUTO-DETECTION: UMUMIY MATNLI XABARLAR UCHUN HANDLER
# =============================================================================
@router.message(F.text)
async def handle_free_text(message: Message, state: FSMContext):
    """
    Agar foydalanuvchi FSM holatisiz to'g'ridan-to'g'ri kasr yoki ifoda yozsa,
    bot uni intellektual tahlil qilib yechib beradi.
    """
    text = message.text.strip()

    # 1. Kasrli ifodalar: masalan "1/2 + 2/3" yoki "1/4 va 2/3"
    try:
        f1, f2, op = parse_two_fractions(text)
        if op:
            ans = calculate_fraction_operation(f1, f2, op)
        else:
            ans = common_denominator_stepwise(f1, f2)
        await message.answer(ans, reply_markup=get_back_to_fractions_keyboard())
        return
    except Exception:
        pass

    # 2. Bitta kasr: masalan "8/12" yoki "2 3/4"
    try:
        parsed = parse_fraction(text)
        # Agar oddiy kasr bo'lsa, uning tahlili va qisqartirishini ko'rsatamiz
        ans = identify_fraction_type(parsed)
        await message.answer(ans, reply_markup=get_back_to_fractions_keyboard())
        return
    except Exception:
        pass

    # 3. Agar hech narsa mos kelmasa
    await message.answer(
        "🤖 <i>Kiritilgan buyruq tushunarsiz.</i>\n\n"
        "Iltimos, pastdagi asosiy menyudan kerakli bo'limni tanlang yoki "
        "kasrni to'g'ri formatda kiriting (masalan: <code>3/4</code>, <code>2 3/4</code>).\n"
        "Qo'llanma uchun: /help",
        reply_markup=get_main_reply_keyboard()
    )


# =============================================================================
# ASOSIY ISHGA TUSHIRISH FUNKSIYASI (MAIN RUNNER)
# =============================================================================
async def main():
    """Botni asinxron ishga tushirish funksiyasi."""
    # Token tekshiruvi
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN":
        print("\n" + "=" * 70)
        print("XATOLIK: Bot tokeni o'rnatilmagan!")
        print("Iltimos, main.py faylini oching va TOKEN = 'YOUR_BOT_TOKEN' qatoriga")
        print("Telegram @BotFather bergan haqiqiy bot tokeningizni yozing!")
        print("=" * 70 + "\n")
        logger.error("Bot tokeni kiritilmagan. Dastur to'xtatildi.")
        return

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    # Eski keshdagi yangilanishlarni (updates) tozalab, pollingni boshlash
    logger.info("Bot muvaffaqiyatli ishga tushirilmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

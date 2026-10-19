"""
Matematika Ustasi Telegram Boti uchun Matematik Hisoblash Dvigateli.
Fractions, math va regex modullari asosida barcha amallarni yuqori aniqlikda bajaradi.
"""

import html
import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Optional, Tuple


class FractionParseError(ValueError):
    """Kasrni o'qish (parse) jarayonida yuzaga keladigan xatoliklar uchun maxsus istisno."""
    pass


@dataclass
class ParsedFraction:
    """Qayta ishlangan kasr ma'lumotlari modeli."""
    fraction: Fraction
    original_text: str
    kind: str  # 'mixed', 'simple', 'integer', 'decimal'
    whole: int = 0
    numerator: int = 0
    denominator: int = 1

    def to_display_string(self) -> str:
        """Kasrni chiroyli matn ko'rinishida qaytarish."""
        if self.kind == 'mixed':
            sign = "-" if self.whole < 0 else ""
            return f"{sign}{abs(self.whole)} {self.numerator}/{self.denominator}"
        elif self.kind == 'simple':
            return f"{self.numerator}/{self.denominator}"
        elif self.kind == 'integer':
            return str(self.whole)
        elif self.kind == 'decimal':
            return f"{self.original_text} ({self.fraction.numerator}/{self.fraction.denominator})"
        return str(self.fraction)


def format_fraction_mixed(f: Fraction) -> str:
    """
    Fraction obyektini aralash kasr ko'rinishida formatlash.
    Masalan: 11/4 -> "2 3/4 (2 butun 3/4)"
    """
    if f.denominator == 1:
        return str(f.numerator)

    num = abs(f.numerator)
    den = f.denominator
    whole = num // den
    rem = num % den
    sign = "-" if f.numerator < 0 else ""

    if whole == 0:
        return f"{sign}{rem}/{den}"
    return f"{sign}{whole} {rem}/{den} ({sign}{whole} butun {rem}/{den})"


def parse_fraction(text: str) -> ParsedFraction:
    """
    Foydalanuvchi kiritgan matndan kasrni ajratib oladi.

    Qo'llab-quvvatlanadigan formatlar:
    - Oddiy kasr: 3/4, -5/2, +7/8
    - Aralash kasr: 2 3/4, 2 butun 3/4, -1 butun 1/2, 1 1/1
    - Butun son: 5, -4, 0
    - O'nli kasr: 2.5, -0.75, 1,25
    """
    clean_text = text.strip()
    if not clean_text:
        raise FractionParseError("Iltimos, kasr yoki son kiriting. Bo'sh matn yuborildi.")

    # Maxraj 0 bo'lishi holatini tekshirish
    if re.search(r'/\s*0+(?!\d)', clean_text):
        raise FractionParseError(
            "❌ <b>Matematik xatolik:</b> Kasr maxraji <b>0</b> bo'lishi mumkin emas!\n"
            "Matematika qoidalariga ko'ra nolga bo'lish taqiqlangan."
        )

    # 1. Aralash kasr: "2 3/4", "2 butun 3/4", "-2 3/4", "1 butun 1/1"
    mixed_match = re.match(
        r'^\s*([+-]?\d+)\s+(?:butun\s+)?(\d+)\s*/\s*(\d+)\s*$',
        clean_text,
        re.IGNORECASE
    )
    if not mixed_match:
        # "2butun 3/4" yoki "2butun3/4" ko'rinishlarini ham qamrab olish
        mixed_match = re.match(
            r'^\s*([+-]?\d+)\s*butun\s*(\d+)\s*/\s*(\d+)\s*$',
            clean_text,
            re.IGNORECASE
        )

    if mixed_match:
        w = int(mixed_match.group(1))
        n = int(mixed_match.group(2))
        d = int(mixed_match.group(3))

        if d == 0:
            raise FractionParseError(
                "❌ <b>Matematik xatolik:</b> Kasr maxraji <b>0</b> bo'lishi mumkin emas!"
            )

        if w >= 0:
            total_num = w * d + n
        else:
            total_num = - (abs(w) * d + n)

        return ParsedFraction(
            fraction=Fraction(total_num, d),
            original_text=clean_text,
            kind='mixed',
            whole=w,
            numerator=n,
            denominator=d
        )

    # 2. Oddiy kasr: "3/4", "-5/2", "+7/8"
    simple_match = re.match(r'^\s*([+-]?\d+)\s*/\s*([+-]?\d+)\s*$', clean_text)
    if simple_match:
        n = int(simple_match.group(1))
        d = int(simple_match.group(2))

        if d == 0:
            raise FractionParseError(
                "❌ <b>Matematik xatolik:</b> Kasr maxraji <b>0</b> bo'lishi mumkin emas!"
            )

        frac = Fraction(n, d)
        return ParsedFraction(
            fraction=frac,
            original_text=clean_text,
            kind='simple',
            whole=0,
            numerator=frac.numerator,
            denominator=frac.denominator
        )

    # 3. Butun son: "5", "-12"
    int_match = re.match(r'^\s*([+-]?\d+)\s*$', clean_text)
    if int_match:
        w = int(int_match.group(1))
        return ParsedFraction(
            fraction=Fraction(w, 1),
            original_text=clean_text,
            kind='integer',
            whole=w,
            numerator=w,
            denominator=1
        )

    # 4. O'nli kasr: "2.5" yoki "2,5"
    dec_match = re.match(r'^\s*([+-]?\d+)[.,](\d+)\s*$', clean_text)
    if dec_match:
        raw_int = dec_match.group(1)
        raw_frac = dec_match.group(2)
        sign = -1 if raw_int.startswith('-') else 1
        int_part = abs(int(raw_int))
        d = 10 ** len(raw_frac)
        n = int_part * d + int(raw_frac)
        frac = Fraction(sign * n, d)
        return ParsedFraction(
            fraction=frac,
            original_text=clean_text,
            kind='decimal',
            whole=int(raw_int),
            numerator=frac.numerator,
            denominator=frac.denominator
        )

    # Hech bir formatga tushmadi
    raise FractionParseError(
        "❌ <b>Noto'g'ri format kiritildi!</b>\n\n"
        "Iltimos, kasrni quyidagi namunalardan biri ko'rinishida kiriting:\n"
        "🔹 <b>Oddiy kasr:</b> <code>3/4</code> yoki <code>5/2</code>\n"
        "🔹 <b>Aralash kasr:</b> <code>2 3/4</code> yoki <code>2 butun 3/4</code>\n"
        "🔹 <b>Butun son:</b> <code>5</code> yoki <code>-3</code>\n"
        "🔹 <b>O'nli kasr:</b> <code>2.5</code>\n\n"
        "⚠️ <i>Eslatma: Harflar va keraksiz belgilardan foydalanmang!</i>"
    )


def parse_two_fractions(text: str) -> Tuple[ParsedFraction, ParsedFraction, Optional[str]]:
    """
    Foydalanuvchi ikkita kasrni bitta xabarda yuborgan bo'lsa, ularni ajratadi.
    Ajratuvchilar: 'va', ',', ';', 'and', yoki arifmetik amallar '+', '-', '*', '/', '÷', '×'.
    """
    clean = text.strip()

    # Arifmetik belgilar bo'yicha ajratish
    ops = [('+', '+'), ('-', '-'), ('*', '×'), ('×', '×'), ('/', '÷'), ('÷', '÷'), (':', '÷')]

    # Avval matnli ajratuvchilar: 'va', 'and', ';', ','
    for sep in [r'\s+va\s+', r'\s+and\s+', r'\s*;\s*', r'\s*,\s*']:
        parts = re.split(sep, clean, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():
            f1 = parse_fraction(parts[0])
            f2 = parse_fraction(parts[1])
            return f1, f2, None

    # Arifmetik operatorlar bo'yicha (faqat kasr ichidagi / emas, amallardagi)
    # Masalan: "1/2 + 2/3" yoki "1 1/2 * 3/4"
    for op_char, op_name in ops:
        # Operator oldida va orqasida kasr borligini tekshiramiz
        if op_char in clean:
            # Agar op_char == '/' bo'lsa, faqat ikkita kasr orasidagi bo'lish bo'lishi mumkin (3 ta slash bo'lsa)
            if op_char == '/':
                slash_count = clean.count('/')
                if slash_count < 2:
                    continue  # Bu oddiy bitta kasr "3/4"

            # Operator bo'yicha bo'lib ko'ramiz
            idx = clean.find(op_char)
            # Ehtiyotkorlik bilan: aralash kasrdagi yoki manfiy sondagi '-' ni hisobga olish
            if op_char == '-' and (idx == 0 or clean[idx-1] in ' \t\n/'):
                # Bu manfiy ishora bo'lishi mumkin, keyingi '-' ni qidiramiz
                idx = clean.find('-', idx + 1)
                if idx == -1:
                    continue

            left_part = clean[:idx].strip()
            right_part = clean[idx + len(op_char):].strip()

            if left_part and right_part:
                try:
                    f1 = parse_fraction(left_part)
                    f2 = parse_fraction(right_part)
                    return f1, f2, op_name
                except Exception:
                    pass

    raise FractionParseError("Ikkita kasr ajratib olinmadi.")


# -------------------------------------------------------------
# 1. ARALASH KASRNI NOTO'G'RI KASRGA AYLANTIRISH
# -------------------------------------------------------------
def mixed_to_improper_stepwise(parsed: ParsedFraction) -> str:
    """Aralash kasrni noto'g'ri kasrga aylantirish bosqichlari."""
    if parsed.kind != 'mixed':
        # Agar oddiy yoki butun son kiritilgan bo'lsa
        if parsed.fraction.denominator == 1:
            return (
                f"ℹ️ Siz butun son kiritdingiz: <b>{parsed.fraction.numerator}</b>.\n"
                f"Uning kasr ko'rinishi: <b>{parsed.fraction.numerator}/1</b>."
            )
        num = abs(parsed.fraction.numerator)
        den = parsed.fraction.denominator
        if num < den:
            return (
                f"ℹ️ Siz kiritgan kasr <b>{parsed.to_display_string()}</b> — to'g'ri kasr!\n"
                f"Aralash kasr bo'lishi uchun uning butun qismi bo'lishi kerak.\n\n"
                f"<i>Namuna:</i> <code>2 3/4</code> yoki <code>2 butun 3/4</code>"
            )
        else:
            return (
                f"ℹ️ Siz kiritgan kasr <b>{parsed.to_display_string()}</b> allaqachon noto'g'ri kasr!\n"
                f"Aralash kasr namunasi: <code>2 3/4</code> yoki <code>2 butun 3/4</code>"
            )

    w = parsed.whole
    n = parsed.numerator
    d = parsed.denominator
    abs_w = abs(w)

    calculated_num = abs_w * d + n
    sign_str = "-" if w < 0 else ""
    improper_str = f"{sign_str}{calculated_num}/{d}"

    # Qisqartirish zarur bo'lsa
    gcd = math.gcd(calculated_num, d)
    reduced_text = ""
    if gcd > 1:
        red_n = calculated_num // gcd
        red_d = d // gcd
        reduced_text = f"\n✂️ <b>Qisqargan shakli:</b> <code>{sign_str}{red_n}/{red_d}</code> (EKUB: {gcd})"

    result_text = (
        f"🧮 <b>Aralash kasrni noto'g'ri kasrga aylantirish:</b>\n\n"
        f"Berilgan kasr: <b>{parsed.to_display_string()}</b>\n"
        f"🔹 Butun qism: <b>{w}</b>\n"
        f"🔹 Surat: <b>{n}</b>\n"
        f"🔹 Maxraj: <b>{d}</b>\n\n"
        f"📝 <b>Hisoblash qoidasi:</b>\n"
        f"Noto'g'ri kasr surati = (Butun qism × Maxraj) + Surat\n"
        f"Surat = {abs_w} × {d} + {n} = {abs_w * d} + {n} = <b>{calculated_num}</b>\n"
        f"Maxraj o'zgarishsiz qoladi: <b>{d}</b>\n\n"
        f"✅ <b>Natija:</b> <code>{improper_str}</code>"
        f"{reduced_text}"
    )
    return result_text


# -------------------------------------------------------------
# 2. NOTO'G'RI KASRNI ARALASH KASRGA AYLANTIRISH
# -------------------------------------------------------------
def improper_to_mixed_stepwise(parsed: ParsedFraction) -> str:
    """Noto'g'ri kasrni aralash kasrga aylantirish bosqichlari."""
    f = parsed.fraction
    num = abs(f.numerator)
    den = f.denominator
    sign_str = "-" if f.numerator < 0 else ""

    if den == 1:
        return (
            f"ℹ️ <b>{parsed.to_display_string()}</b> — butun son.\n"
            f"Uni aralash kasrga aylantirib bo'lmaydi, chunki qoldiq 0 ga teng."
        )

    if num < den:
        return (
            f"ℹ️ <b>{parsed.to_display_string()}</b> — <b>to'g'ri kasr</b> (chunki {num} < {den}).\n"
            f"Uning butun qismi 0 ga teng: <code>0 {num}/{den}</code>.\n\n"
            f"Aralash kasrga aylantirish uchun kasr surati maxrajidan katta yoki teng bo'lishi lozim (masalan: <code>11/4</code>)."
        )

    whole = num // den
    rem = num % den

    if rem == 0:
        return (
            f"🧮 <b>Noto'g'ri kasrni butun songa aylantirish:</b>\n\n"
            f"Berilgan kasr: <b>{parsed.to_display_string()}</b>\n"
            f"Surat maxrajga qoldiqsiz bo'linadi:\n"
            f"{num} ÷ {den} = <b>{whole}</b>\n\n"
            f"✅ <b>Natija:</b> <code>{sign_str}{whole}</code> (butun son)"
        )

    mixed_display = f"{sign_str}{whole} {rem}/{den}"
    mixed_words = f"{sign_str}{whole} butun {rem}/{den}"

    result_text = (
        f"🧮 <b>Noto'g'ri kasrni aralash kasrga aylantirish:</b>\n\n"
        f"Berilgan kasr: <b>{parsed.to_display_string()}</b>\n"
        f"🔹 Surat: <b>{num}</b>\n"
        f"🔹 Maxraj: <b>{den}</b>\n\n"
        f"📝 <b>Qadamlar:</b>\n"
        f"1. Suratni maxrajga qoldiqli bo'lamiz:\n"
        f"   {num} ÷ {den} = <b>{whole}</b> (qoldiq: <b>{rem}</b>)\n"
        f"2. Butun qism: <b>{whole}</b>\n"
        f"3. Yangi surat (qoldiq): <b>{rem}</b>\n"
        f"4. Maxraj o'zgarmaydi: <b>{den}</b>\n\n"
        f"✅ <b>Natija:</b> <code>{mixed_display}</code> ({mixed_words})"
    )
    return result_text


# -------------------------------------------------------------
# 3. KASR TURINI ANIQLASH
# -------------------------------------------------------------
def identify_fraction_type(parsed: ParsedFraction) -> str:
    """Kasrning barcha xususiyatlarini aniqlash."""
    f = parsed.fraction
    num = abs(f.numerator)
    den = f.denominator
    is_negative = f.numerator < 0

    types = []

    # Shakli
    if parsed.kind == 'mixed':
        shape = "Aralash kasr ko'rinishida kiritilgan"
    elif parsed.kind == 'decimal':
        shape = "O'nli kasr ko'rinishida kiritilgan"
    elif parsed.kind == 'integer':
        shape = "Butun son ko'rinishida kiritilgan"
    else:
        shape = "Oddiy kasr ko'rinishida kiritilgan"

    # Matematik turi
    if den == 1:
        math_type = "Butun son"
        explanation = f"Maxraji 1 ga teng, qiymati: {f.numerator}"
    elif num < den:
        math_type = "To'g'ri kasr"
        explanation = f"Surati ({num}) maxrajidan ({den}) kichik, qiymati 1 dan kichik (|x| &lt; 1)."
    elif num == den:
        math_type = "Noto'g'ri kasr (1 ga teng)"
        explanation = f"Surat va maxraj teng ({num} = {den}), qiymati 1 ga teng."
    else:
        math_type = "Noto'g'ri kasr"
        explanation = f"Surati ({num}) maxrajidan ({den}) katta, qiymati 1 dan katta (|x| &gt; 1)."

    # Qisqarishi
    gcd = math.gcd(num, den)
    if gcd > 1:
        reduction_info = f"Kasr qisqaradi (EKUB: {gcd}). Qisqargani: <code>{f.numerator//gcd}/{den//gcd}</code>"
    else:
        reduction_info = "Qisqarmaydigan kasr (surat va maxraj o'zaro tub sonlar, EKUB = 1)."

    # O'nli va foiz qiymati
    decimal_val = float(f)
    percent_val = decimal_val * 100

    result_text = (
        f"🔍 <b>Kasr turini aniqlash va tahlil:</b>\n\n"
        f"Kiritilgan qiymat: <b>{parsed.to_display_string()}</b>\n"
        f"🔹 <b>Kiritilish shakli:</b> {shape}\n"
        f"🔹 <b>Matematik turi:</b> <b>{math_type}</b>\n"
        f"💡 <i>Izoh:</i> {explanation}\n\n"
        f"📊 <b>Batafsil ma'lumotlar:</b>\n"
        f"• Surat: <b>{f.numerator}</b>\n"
        f"• Maxraj: <b>{f.denominator}</b>\n"
        f"• Ishtirok etuvchi ishora: {'Manfiy (-)' if is_negative else 'Musbat (+)'}\n"
        f"• Qisqarish holati: {reduction_info}\n"
        f"• Noto'g'ri kasr ko'rinishi: <code>{f.numerator}/{f.denominator}</code>\n"
        f"• Aralash kasr ko'rinishi: <code>{format_fraction_mixed(f)}</code>\n"
        f"• O'nli kasr qiymati: <code>{decimal_val:.4f}</code>\n"
        f"• Foizdagi qiymati: <code>{percent_val:.2f}%</code>"
    )
    return result_text


# -------------------------------------------------------------
# 4. KASRNI QISQARTIRISH
# -------------------------------------------------------------
def simplify_fraction_stepwise(parsed: ParsedFraction) -> str:
    """Kasrni bosqichma-bosqich qisqartirish."""
    f = parsed.fraction
    orig_num = f.numerator
    orig_den = f.denominator

    gcd = math.gcd(abs(orig_num), orig_den)

    if orig_den == 1:
        return (
            f"✂️ <b>Kasrni qisqartirish:</b>\n\n"
            f"Kiritilgan son: <b>{parsed.to_display_string()}</b> — butun son.\n"
            f"Uning maxraji 1 bo'lgani sababli qisqartirishga hojat yo'q."
        )

    if gcd == 1:
        return (
            f"✂️ <b>Kasrni qisqartirish:</b>\n\n"
            f"Berilgan kasr: <b>{parsed.to_display_string()}</b>\n"
            f"🔹 Surat: <b>{orig_num}</b>\n"
            f"🔹 Maxraj: <b>{orig_den}</b>\n\n"
            f"ℹ️ Surat va maxrajning Eng Katta Umumiy Bo'luvchisi: <b>EKUB({abs(orig_num)}, {orig_den}) = 1</b>.\n"
            f"Demak, bu kasr <b>qisqarmaydigan kasr</b> hisoblanadi!\n\n"
            f"✅ <b>Javob:</b> <code>{parsed.to_display_string()}</code>"
        )

    simplified_num = orig_num // gcd
    simplified_den = orig_den // gcd
    simplified_frac = Fraction(simplified_num, simplified_den)

    result_text = (
        f"✂️ <b>Kasrni qisqartirish:</b>\n\n"
        f"Berilgan kasr: <b>{parsed.to_display_string()}</b>\n"
        f"🔹 Surat: <b>{orig_num}</b>\n"
        f"🔹 Maxraj: <b>{orig_den}</b>\n\n"
        f"📝 <b>Qadamlar:</b>\n"
        f"1. Surat va maxraj uchun EKUB topiladi:\n"
        f"   <b>EKUB({abs(orig_num)}, {orig_den}) = {gcd}</b>\n"
        f"2. Kasrning surati va maxraji {gcd} ga bo'linadi:\n"
        f"   Surat: {orig_num} ÷ {gcd} = <b>{simplified_num}</b>\n"
        f"   Maxraj: {orig_den} ÷ {gcd} = <b>{simplified_den}</b>\n\n"
        f"✅ <b>Qisqargan natija:</b> <code>{simplified_num}/{simplified_den}</code>"
    )

    if abs(simplified_num) > simplified_den:
        result_text += f"\n🔄 <i>Aralash kasr shaklida:</i> <code>{format_fraction_mixed(simplified_frac)}</code>"

    return result_text


# -------------------------------------------------------------
# 5. UMUMIY MAXRAJ BERISH
# -------------------------------------------------------------
def common_denominator_stepwise(p1: ParsedFraction, p2: ParsedFraction) -> str:
    """Ikkita kasrga bosqichma-bosqich umumiy maxraj berish."""
    f1 = p1.fraction
    f2 = p2.fraction

    d1 = f1.denominator
    d2 = f2.denominator

    lcm = math.lcm(d1, d2)
    m1 = lcm // d1
    m2 = lcm // d2

    new_n1 = f1.numerator * m1
    new_n2 = f2.numerator * m2

    # Taqqoslash
    if new_n1 < new_n2:
        comp_sign = "&lt;"
    elif new_n1 > new_n2:
        comp_sign = "&gt;"
    else:
        comp_sign = "="

    result_text = (
        f"⚖️ <b>Kasrlarga umumiy maxraj berish:</b>\n\n"
        f"1-kasr: <b>{p1.to_display_string()}</b> (shakli: <code>{f1.numerator}/{f1.denominator}</code>)\n"
        f"2-kasr: <b>{p2.to_display_string()}</b> (shakli: <code>{f2.numerator}/{f2.denominator}</code>)\n\n"
        f"📝 <b>Bosqichma-bosqich yechish:</b>\n"
        f"1. Maxrajlar: <b>{d1}</b> va <b>{d2}</b>\n"
        f"2. Eng Kichik Umumiy Karrali (EKUK) topiladi:\n"
        f"   <b>EKUK({d1}, {d2}) = {lcm}</b> (bu yangi umumiy maxraj)\n\n"
        f"3. Qo'shimcha ko'paytuvchilar aniqlanadi:\n"
        f"   • 1-kasr uchun: {lcm} ÷ {d1} = <b>{m1}</b>\n"
        f"     <code>({f1.numerator} × {m1}) / ({d1} × {m1}) = {new_n1}/{lcm}</code>\n"
        f"   • 2-kasr uchun: {lcm} ÷ {d2} = <b>{m2}</b>\n"
        f"     <code>({f2.numerator} × {m2}) / ({d2} × {m2}) = {new_n2}/{lcm}</code>\n\n"
        f"✅ <b>Natija:</b>\n"
        f"1-kasr: <code>{new_n1}/{lcm}</code>\n"
        f"2-kasr: <code>{new_n2}/{lcm}</code>\n"
        f"Umumiy maxraj: <b>{lcm}</b>\n\n"
        f"📊 <b>Taqqoslash:</b>\n"
        f"<code>{new_n1}/{lcm} {comp_sign} {new_n2}/{lcm}</code>  ➡️  "
        f"<b>{p1.to_display_string()} {comp_sign} {p2.to_display_string()}</b>"
    )
    return result_text


# -------------------------------------------------------------
# 6, 7, 8, 9. KASRLAR USTIDA AMALLAR (Qo'shish, Ayirish, Ko'paytirish, Bo'lish)
# -------------------------------------------------------------
def calculate_fraction_operation(p1: ParsedFraction, p2: ParsedFraction, op: str) -> str:
    """
    Kasrlar ustida amallar:
    op in ['+', '-', '*', '×', '/', '÷']
    """
    f1 = p1.fraction
    f2 = p2.fraction

    if op in ['/', '÷', ':']:
        if f2 == 0:
            return (
                "❌ <b>Matematik xatolik:</b> Nolga bo'lish mumkin emas!\n"
                "2-kasrning qiymati 0 ga teng bo'lib qoldi."
            )

    d1, d2 = f1.denominator, f2.denominator
    lcm = math.lcm(d1, d2)
    m1 = lcm // d1
    m2 = lcm // d2

    new_n1 = f1.numerator * m1
    new_n2 = f2.numerator * m2

    if op == '+':
        op_title = "Kasrlarni qo'shish"
        op_sym = "+"
        res_fraction = f1 + f2
        step_calc = (
            f"1. Umumiy maxraj: EKUK({d1}, {d2}) = <b>{lcm}</b>\n"
            f"2. Kasrlarni umumiy maxrajga keltiramiz:\n"
            f"   • {f1.numerator}/{d1} = ({f1.numerator}×{m1})/{lcm} = {new_n1}/{lcm}\n"
            f"   • {f2.numerator}/{d2} = ({f2.numerator}×{m2})/{lcm} = {new_n2}/{lcm}\n"
            f"3. Suratlarni qo'shamiz:\n"
            f"   ({new_n1} + {new_n2}) / {lcm} = <b>{new_n1 + new_n2}/{lcm}</b>"
        )
    elif op == '-':
        op_title = "Kasrlarni ayirish"
        op_sym = "−"
        res_fraction = f1 - f2
        step_calc = (
            f"1. Umumiy maxraj: EKUK({d1}, {d2}) = <b>{lcm}</b>\n"
            f"2. Kasrlarni umumiy maxrajga keltiramiz:\n"
            f"   • {f1.numerator}/{d1} = ({f1.numerator}×{m1})/{lcm} = {new_n1}/{lcm}\n"
            f"   • {f2.numerator}/{d2} = ({f2.numerator}×{m2})/{lcm} = {new_n2}/{lcm}\n"
            f"3. Suratlarni ayiramiz:\n"
            f"   ({new_n1} − {new_n2}) / {lcm} = <b>{new_n1 - new_n2}/{lcm}</b>"
        )
    elif op in ['*', '×']:
        op_title = "Kasrlarni ko'paytirish"
        op_sym = "×"
        res_fraction = f1 * f2
        raw_n = f1.numerator * f2.numerator
        raw_d = f1.denominator * f2.denominator
        step_calc = (
            f"1. Suratlarni o'zaro ko'paytiramiz:\n"
            f"   {f1.numerator} × {f2.numerator} = <b>{raw_n}</b>\n"
            f"2. Maxrajlarni o'zaro ko'paytiramiz:\n"
            f"   {f1.denominator} × {f2.denominator} = <b>{raw_d}</b>\n"
            f"3. Hosil bo'lgan kasr: <b>{raw_n}/{raw_d}</b>"
        )
    elif op in ['/', '÷', ':']:
        op_title = "Kasrlarni bo'lish"
        op_sym = "÷"
        res_fraction = f1 / f2
        inv_f2_n = f2.denominator
        inv_f2_d = f2.numerator
        if inv_f2_d < 0:
            inv_f2_n = -inv_f2_n
            inv_f2_d = -inv_f2_d
        raw_n = f1.numerator * inv_f2_n
        raw_d = f1.denominator * inv_f2_d
        step_calc = (
            f"1. 1-kasrni 2-kasrning teskarisiga (<code>{inv_f2_n}/{inv_f2_d}</code>) ko'paytiramiz:\n"
            f"   ({f1.numerator}/{f1.denominator}) × ({inv_f2_n}/{inv_f2_d})\n"
            f"2. Suratlarni ko'paytiramiz: {f1.numerator} × {inv_f2_n} = <b>{raw_n}</b>\n"
            f"3. Maxrajlarni ko'paytiramiz: {f1.denominator} × {inv_f2_d} = <b>{raw_d}</b>\n"
            f"4. Hosil bo'lgan kasr: <b>{raw_n}/{raw_d}</b>"
        )
    else:
        return "❌ Noma'lum amal!"

    # Natijani formatlash
    ans_simple = f"{res_fraction.numerator}/{res_fraction.denominator}" if res_fraction.denominator != 1 else str(res_fraction.numerator)
    ans_mixed = format_fraction_mixed(res_fraction)
    dec_val = float(res_fraction)

    result_text = (
        f"🧮 <b>{op_title}:</b>\n\n"
        f"Misol: <b>{p1.to_display_string()} {op_sym} {p2.to_display_string()}</b>\n\n"
        f"📝 <b>Yechish tartibi:</b>\n"
        f"{step_calc}\n\n"
        f"✅ <b>Yakuniy natija:</b>\n"
        f"🔹 Oddiy/qisqargan kasr: <code>{ans_simple}</code>\n"
    )

    if res_fraction.denominator != 1 and abs(res_fraction.numerator) >= res_fraction.denominator:
        result_text += f"🔹 Aralash kasr: <code>{ans_mixed}</code>\n"

    result_text += f"🔹 O'nli kasr qiymati: <code>{dec_val:.4f}</code>"
    return result_text


# -------------------------------------------------------------
# ASOSIY MENYU: ARIFMETIK AMALLAR (Qo'shish, Ayirish, Ko'paytirish, Bo'lish)
# -------------------------------------------------------------
def arithmetic_stepwise(a: float, b: float, op: str) -> str:
    """Oddiy sonlar ustida arifmetik amallarni yechib berish."""
    # Butun son bo'lsa chiroyli ko'rsatish
    def fmt(n: float) -> str:
        if n.is_integer():
            return str(int(n))
        return f"{n:g}"

    sa, sb = fmt(a), fmt(b)

    if op == '+':
        res = a + b
        return (
            f"➕ <b>Qo'shish amali:</b>\n\n"
            f"<b>{sa} + {sb} = {fmt(res)}</b>\n\n"
            f"✅ <b>Natija:</b> <code>{fmt(res)}</code>"
        )
    elif op == '-':
        res = a - b
        return (
            f"➖ <b>Ayirish amali:</b>\n\n"
            f"<b>{sa} − {sb} = {fmt(res)}</b>\n\n"
            f"✅ <b>Natija:</b> <code>{fmt(res)}</code>"
        )
    elif op in ['*', '×']:
        res = a * b
        return (
            f"✖️ <b>Ko'paytirish amali:</b>\n\n"
            f"<b>{sa} × {sb} = {fmt(res)}</b>\n\n"
            f"✅ <b>Natija:</b> <code>{fmt(res)}</code>"
        )
    elif op in ['/', '÷']:
        if b == 0:
            return (
                f"❌ <b>Matematik xatolik:</b> Nolga bo'lish mumkin emas!\n"
                f"Ixtiyoriy sonni 0 ga bo'lish ma'noga ega emas."
            )
        res = a / b
        whole_part = int(a // b)
        rem_part = a % b
        rem_info = ""
        if a.is_integer() and b.is_integer() and rem_part != 0:
            rem_info = f"\n🔹 Qoldiqli bo'lish: {sa} ÷ {sb} = <b>{whole_part}</b> (qoldiq: <b>{fmt(rem_part)}</b>)"

        return (
            f"➗ <b>Bo'lish amali:</b>\n\n"
            f"<b>{sa} ÷ {sb} = {fmt(res)}</b>\n"
            f"{rem_info}\n"
            f"🔹 O'nli kasr qiymati: <code>{res:.6g}</code>\n\n"
            f"✅ <b>Natija:</b> <code>{fmt(res)}</code>"
        )
    return "Noma'lum amal"


# -------------------------------------------------------------
# FOIZ HISOBLASH AMALLARI
# -------------------------------------------------------------
def percent_calculate_stepwise(mode: str, v1: float, v2: float) -> str:
    """
    Foiz hisoblash amallari:
    mode:
    1: Sonning foizi (v1 ning v2% i)
    2: Nisbat foizi (v1 soni v2 ning necha foizi)
    3: Foizga oshirish (v1 ga v2% qo'shish)
    4: Foizga kamaytirish (v1 dan v2% ayirish)
    """
    def fmt(n: float) -> str:
        if n.is_integer():
            return str(int(n))
        return f"{n:g}"

    s1, s2 = fmt(v1), fmt(v2)

    if mode == 'part_of_number':
        # v1 ning v2% i
        res = (v1 * v2) / 100.0
        return (
            f"📊 <b>Sonning foizini topish:</b>\n\n"
            f"Savol: <b>{s1} ning {s2}% i qancha?</b>\n\n"
            f"📝 <b>Formula:</b>\n"
            f"Natija = (Son × Foiz) / 100\n"
            f"Natija = ({s1} × {s2}) / 100 = <b>{fmt(res)}</b>\n\n"
            f"✅ <b>Javob:</b> <code>{fmt(res)}</code>"
        )

    elif mode == 'number_ratio':
        # v1 soni v2 ning necha foizi
        if v2 == 0:
            return "❌ <b>Xatolik:</b> Asosiy son (maxraj) 0 bo'lishi mumkin emas!"
        res = (v1 / v2) * 100.0
        return (
            f"📊 <b>Son ikkinchi sonning necha foizi:</b>\n\n"
            f"Savol: <b>{s1} soni {s2} sonining necha foizini tashkil qiladi?</b>\n\n"
            f"📝 <b>Formula:</b>\n"
            f"Foiz = (1-son / 2-son) × 100%\n"
            f"Foiz = ({s1} / {s2}) × 100% = <b>{res:.2f}%</b>\n\n"
            f"✅ <b>Javob:</b> <code>{res:.2f}%</code>"
        )

    elif mode == 'increase_by_percent':
        # v1 ga v2% qo'shish
        delta = (v1 * v2) / 100.0
        res = v1 + delta
        return (
            f"📊 <b>Sonni foizga oshirish:</b>\n\n"
            f"Savol: <b>{s1} sonini {s2}% ga oshirish</b>\n\n"
            f"📝 <b>Bosqichlar:</b>\n"
            f"1. Qo'shiladigan miqdor ({s2}%): ({s1} × {s2}) / 100 = <b>{fmt(delta)}</b>\n"
            f"2. Yangi qiymat: {s1} + {fmt(delta)} = <b>{fmt(res)}</b>\n\n"
            f"✅ <b>Javob:</b> <code>{fmt(res)}</code>"
        )

    elif mode == 'decrease_by_percent':
        # v1 dan v2% ayirish
        delta = (v1 * v2) / 100.0
        res = v1 - delta
        return (
            f"📊 <b>Sonni foizga kamaytirish:</b>\n\n"
            f"Savol: <b>{s1} sonini {s2}% ga kamaytirish</b>\n\n"
            f"📝 <b>Bosqichlar:</b>\n"
            f"1. Kamaytiriladigan miqdor ({s2}%): ({s1} × {s2}) / 100 = <b>{fmt(delta)}</b>\n"
            f"2. Yangi qiymat: {s1} − {fmt(delta)} = <b>{fmt(res)}</b>\n\n"
            f"✅ <b>Javob:</b> <code>{fmt(res)}</code>"
        )

    return "Noma'lum foiz amali"

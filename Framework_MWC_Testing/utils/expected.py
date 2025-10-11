from enum import Enum

class Exp(str, Enum):
    SUCCESS = "success"
    INVALID = "invalid"
    REQ_USER = "required_username"
    REQ_PASS = "required_password"
    REQ_BOTH = "required_both"

def normalize_expected(raw: str, username: str, password: str):
    s = (raw or "").strip().lower()
    direct = {
        "success": (Exp.SUCCESS, raw),
        "invalid": (Exp.INVALID, raw),
        "required_username": (Exp.REQ_USER, ""),
        "required_password": (Exp.REQ_PASS, ""),
        "required_both": (Exp.REQ_BOTH, ""),
    }
    if s in direct:
        return direct[s]

    # Câu tự nhiên
    if "không đúng" in s:
        return (Exp.INVALID, raw)
    if "vui lòng điền" in s or "required" in s or s == "":
        u_empty = (username or "").strip() == ""
        p_empty = (password or "").strip() == ""
        if u_empty and p_empty: return (Exp.REQ_BOTH, "")
        if u_empty: return (Exp.REQ_USER, "")
        if p_empty: return (Exp.REQ_PASS, "")
        return (Exp.REQ_BOTH, "")

    # Còn lại: coi là success và raw chính là tên mong muốn
    return (Exp.SUCCESS, raw)
class Exp(str, Enum):
    SUCCESS = "success"
    INVALID = "invalid"
    REQ_USER = "required_username"
    REQ_PASS = "required_password"
    REQ_BOTH = "required_both"

def normalize_expected(raw: str, username: str, password: str):
    s = (raw or "").strip().lower()
    direct = {
        "success": (Exp.SUCCESS, raw),
        "invalid": (Exp.INVALID, raw),
        "required_username": (Exp.REQ_USER, ""),
        "required_password": (Exp.REQ_PASS, ""),
        "required_both": (Exp.REQ_BOTH, ""),
    }
    if s in direct:
        return direct[s]

    if "không đúng" in s:
        return (Exp.INVALID, raw)
    if "vui lòng điền" in s or "required" in s or s == "":
        u_empty = (username or "").strip() == ""
        p_empty = (password or "").strip() == ""
        if u_empty and p_empty: return (Exp.REQ_BOTH, "")
        if u_empty: return (Exp.REQ_USER, "")
        if p_empty: return (Exp.REQ_PASS, "")
        return (Exp.REQ_BOTH, "")

    return (Exp.SUCCESS, raw)

# ===== Register (bổ sung) =====
class RegExp(str, Enum):
    SUCCESS = "success"
    REQ = "required"                 # thiếu trường (một/một số)
    INVALID_PHONE = "invalid_phone"
    PASS_LENGTH = "password_length"
    PASS_MISMATCH = "password_mismatch"

def normalize_expected_register(raw: str, username: str, phone: str, password: str, repass: str):
    """
    Trả về (RegExp, value) cho Register.
    - SUCCESS: value = raw (không dùng để so sánh thêm)
    - REQ: value = "" (kiểm tra theo valueMissing)
    - Các lỗi khác: value là thông điệp dễ debug/log
    """
    s = (raw or "").strip().lower()

    direct = {
        "success": (RegExp.SUCCESS, raw),
        "required": (RegExp.REQ, ""),
        "invalid_phone": (RegExp.INVALID_PHONE, "Số điện thoại không đúng định dạng!"),
        "password_length": (RegExp.PASS_LENGTH, "Mật khẩu phải lớn hơn 8 ký tự và nhỏ hơn 20 ký tự!"),
        "password_mismatch": (RegExp.PASS_MISMATCH, "Mật khẩu không giống nhau"),
    }
    if s in direct:
        return direct[s]

    if "số điện thoại không đúng định dạng" in s:
        return (RegExp.INVALID_PHONE, "Số điện thoại không đúng định dạng!")
    if "mật khẩu phải lớn hơn 8 ký tự" in s:
        return (RegExp.PASS_LENGTH, "Mật khẩu phải lớn hơn 8 ký tự và nhỏ hơn 20 ký tự!")
    if "mật khẩu không giống nhau" in s:
        return (RegExp.PASS_MISMATCH, "Mật khẩu không giống nhau")
    if "vui lòng điền" in s or "required" in s or s == "":
        return (RegExp.REQ, "")

    # còn lại coi là success
    return (RegExp.SUCCESS, raw)

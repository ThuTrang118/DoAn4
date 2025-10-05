# utils/expected.py
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

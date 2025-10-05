import os, time
from typing import List, Dict, Any, DefaultDict
from collections import defaultdict
from openpyxl import load_workbook
import pandas as pd

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def _norm(s) -> str:
    return "" if s is None else str(s).strip()

def _norm_key(s) -> str:
    return _norm(s).lower()

def load_sheet(path: str, sheet_name: str) -> List[Dict[str, Any]]:
    """
    Đọc 1 sheet từ Excel (header KHÔNG phân biệt hoa/thường).
    Trả về list dict với 4 cột chuẩn: testcase, username, password, expected
    """
    wb = load_workbook(path)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Sheet '{sheet_name}' không tồn tại trong file {path}. Sheet có: {wb.sheetnames}")
    ws = wb[sheet_name]

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        print(f"[WARN] Sheet '{sheet_name}' rỗng trong file {os.path.basename(path)}")
        return []

    header = [_norm_key(h) for h in rows[0]]
    data: List[Dict[str, Any]] = []
    for r in rows[1:]:
        if not r:
            continue
        row_raw = {header[i]: _norm(r[i]) for i in range(min(len(header), len(r)))}
        row = {
            "testcase": row_raw.get("testcase", ""),
            "username": row_raw.get("username", ""),
            "password": row_raw.get("password", ""),
            "expected": row_raw.get("expected", ""),
        }
        if row["testcase"]:
            data.append(row)

    print(f"[INFO] Loaded {len(data)} rows from '{os.path.basename(path)}' sheet '{sheet_name}'")
    return data

class ResultBook:
    def __init__(self, out_dir: str, file_name: str = "Results_Data.xlsx"):
        ensure_dir(out_dir)
        self.path = os.path.join(out_dir, file_name)
        self._sheets: DefaultDict[str, list[dict]] = defaultdict(list)

    def add_row(self, sheet: str, row: Dict[str, Any]):
        self._sheets[sheet].append(row)

    def _overwrite_by_testcase(self, df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
    
        preferred = ['Testcase', 'Username', 'Password', 'Expected', 'Actual', 'Status', 'Time']

        for col in preferred:
            if col not in df_old.columns: df_old[col] = ''
            if col not in df_new.columns: df_new[col] = ''

        old_idx = df_old.set_index('Testcase', drop=False)
        new_idx = df_new.set_index('Testcase', drop=False)

        # bỏ các testcase trùng trong old rồi nối new vào
        old_kept = old_idx[~old_idx.index.isin(new_idx.index)]
        final = pd.concat([old_kept, new_idx], axis=0).reset_index(drop=True)

        # sắp xếp cột theo preferred (những cột thừa – nếu có – đưa ra sau)
        ordered = [c for c in preferred if c in final.columns] + [c for c in final.columns if c not in preferred]
        return final[ordered]

    def save(self):
        # tải sheet cũ (nếu file tồn tại) để giữ lại các sheet không ghi lần này
        existing = {}
        if os.path.exists(self.path):
            xls = pd.ExcelFile(self.path, engine="openpyxl")
            for s in xls.sheet_names:
                existing[s] = xls.parse(s)

        with pd.ExcelWriter(self.path, engine="openpyxl", mode="w") as writer:
            # ghi lại các sheet cũ mà lần này không động tới
            for s, df in existing.items():
                if s not in self._sheets:
                    df.to_excel(writer, sheet_name=s, index=False)

            # ghi/ghi đè các sheet mới
            for s, rows in self._sheets.items():
                df_new = pd.DataFrame(rows)
                if s in existing and not existing[s].empty and 'Testcase' in existing[s].columns:
                    final = self._overwrite_by_testcase(existing[s], df_new)
                else:
                    # sheet mới hoàn toàn
                    preferred = ['Testcase', 'Username', 'Password', 'Expected', 'Actual', 'Status', 'Time']
                    for col in preferred:
                        if col not in df_new.columns: df_new[col] = ''
                    final = df_new[preferred]
                final.to_excel(writer, sheet_name=s, index=False)
        return self.path

# re-export (tuỳ chọn)
from .expected import Exp, normalize_expected  # noqa: E402

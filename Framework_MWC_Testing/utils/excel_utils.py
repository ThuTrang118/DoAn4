import os
import pandas as pd
from typing import List, Dict, Any, DefaultDict
from collections import defaultdict
from openpyxl import load_workbook

# --- HÀM TIỆN ÍCH CƠ BẢN ---
def ensure_dir(path: str):
    """Tạo thư mục nếu chưa tồn tại."""
    os.makedirs(path, exist_ok=True)

def _norm(s) -> str:
    """Chuẩn hóa dữ liệu đọc từ Excel (xóa None, strip())."""
    return "" if s is None else str(s).strip()

def _norm_key(s) -> str:
    """Đưa header về dạng thường, không phân biệt hoa/thường."""
    return _norm(s).lower()


# --- HÀM ĐỌC FILE DỮ LIỆU TEST ---
def load_sheet(path: str, sheet_name: str) -> List[Dict[str, Any]]:
    """
    Đọc dữ liệu từ 1 sheet Excel (Data-Driven).
    Trả về danh sách dict: [{"testcase": ..., "username": ..., "password": ...}, ...]
    """
    wb = load_workbook(path)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Sheet '{sheet_name}' không tồn tại trong file {path}. "
                         f"Các sheet hiện có: {wb.sheetnames}")
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
        row = {header[i]: _norm(r[i]) for i in range(min(len(header), len(r)))}
        if row.get("testcase"):  # chỉ lấy dòng có Testcase
            data.append(row)

    print(f"[INFO] Loaded {len(data)} rows from '{os.path.basename(path)}' sheet '{sheet_name}'")
    return data


# --- LỚP GHI KẾT QUẢ TEST RA FILE EXCEL ---
class ResultBook:
    def __init__(self, out_dir: str, file_name: str = "ResultsData.xlsx"):
        ensure_dir(out_dir)
        self.path = os.path.join(out_dir, file_name)
        self._sheets: DefaultDict[str, list[dict]] = defaultdict(list)

    def add_row(self, sheet: str, row: Dict[str, Any]):
        """Thêm 1 dòng kết quả vào bộ nhớ tạm."""
        self._sheets[sheet].append(row)

    def save(self):
        """Ghi dữ liệu ra file Excel — chỉ ghi đè sheet đang test."""
        existing = {}

        # Đọc toàn bộ sheet cũ nếu file tồn tại
        if os.path.exists(self.path):
            try:
                xls = pd.ExcelFile(self.path, engine="openpyxl")
                for s in xls.sheet_names:
                    existing[s] = xls.parse(s)
            except Exception as e:
                print(f"[WARN] Không thể đọc file cũ: {e}")

        # Ghi lại toàn bộ file (sheet mới ghi đè, sheet cũ giữ nguyên)
        with pd.ExcelWriter(self.path, engine="openpyxl", mode="w") as writer:
            # Ghi lại các sheet cũ KHÔNG bị ghi đè
            for s, df_old in existing.items():
                if s not in self._sheets:
                    df_old.to_excel(writer, sheet_name=s, index=False)

            # Ghi sheet mới hoặc sheet vừa test xong (ghi đè)
            for s, rows in self._sheets.items():
                df_new = pd.DataFrame(rows)
                df_new.to_excel(writer, sheet_name=s, index=False)

        print(f"[RESULT SAVED]: {self.path}")
        return self.path
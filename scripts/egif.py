"""Read EGIF ZIP/XLSX exports without requiring Excel or third-party packages."""

import io
import re
import zipfile
import xml.etree.ElementTree as ET

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_export(path):
    """Yield source rows, preserving identifiers and Spanish decimal strings."""
    with zipfile.ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if name.lower().endswith(".xlsx"))
        if not names:
            raise ValueError(f"No XLSX workbooks in {path}")
        for name in names:
            with zipfile.ZipFile(io.BytesIO(archive.read(name))) as workbook:
                strings = []
                if "xl/sharedStrings.xml" in workbook.namelist():
                    strings = ["".join(node.itertext()) for node in
                               ET.fromstring(workbook.read("xl/sharedStrings.xml"))]

                def value(cell):
                    if cell.get("t") == "inlineStr":
                        return "".join(cell.find("s:is", NS).itertext())
                    node = cell.find("s:v", NS)
                    if node is None:
                        return ""
                    if cell.get("t") == "s":
                        return strings[int(node.text)]
                    return node.text or ""

                for sheet in sorted(workbook.namelist()):
                    if not re.fullmatch(r"xl/worksheets/sheet\d*\.xml", sheet):
                        continue
                    headers = None
                    with workbook.open(sheet) as stream:
                        for _, row in ET.iterparse(stream, events=("end",)):
                            if row.tag != f"{{{NS['s']}}}row":
                                continue
                            cells = {re.sub(r"\d", "", cell.get("r")): value(cell)
                                     for cell in row}
                            if headers is None:
                                headers = cells
                                if "Campania" not in headers.values():
                                    raise ValueError(f"Missing EGIF headers in {name}/{sheet}")
                            elif any(cells.values()):
                                yield {header: cells.get(column, "")
                                       for column, header in headers.items()}
                            row.clear()

import os
import random
import datetime
from datetime import timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

print("Generating TATA POWER-DDL MMG Stores Enterprise Database...")

wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# Color Palette (Tata Power Brand Guidelines)
NAVY_HEADER = "004890"     # TPDDL Primary Blue
WHITE = "FFFFFF"
ICE_BLUE_TINT = "F1F6FC"   # Banded row tint
HEADER_BORDER = "94A3B8"
ROW_BORDER = "CBD5E1"
DARK_TEXT = "0F172A"
MUTED_TEXT = "475569"
OK_GREEN = "15803D"
WARN_AMBER = "B45309"
ALERT_RED = "B91C1C"
PURPLE = "6D28D9"

font_title = Font(name="Calibri", size=15, bold=True, color=WHITE)
font_header = Font(name="Calibri", size=11, bold=True, color=WHITE)
font_data = Font(name="Calibri", size=10, bold=False, color=DARK_TEXT)
font_bold = Font(name="Calibri", size=10, bold=True, color=DARK_TEXT)
font_formula = Font(name="Calibri", size=10, bold=True, color="003366")

fill_title = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
fill_sub_header = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
fill_odd = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")
fill_even = PatternFill(start_color=ICE_BLUE_TINT, end_color=ICE_BLUE_TINT, fill_type="solid")

thin_border_side = Side(border_style="thin", color=ROW_BORDER)
border_data = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
border_header = Border(left=thin_border_side, right=thin_border_side, top=Side(border_style="medium", color="002244"), bottom=Side(border_style="medium", color="002244"))

align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

def auto_fit_columns(ws, min_col=1, max_col=None):
    if max_col is None:
        max_col = ws.max_column
    for col in range(min_col, max_col + 1):
        col_letter = get_column_letter(col)
        max_len = 0
        for cell in ws[col_letter]:
            val = cell.value
            if val is not None:
                # ignore title row spanning
                if cell.row in [1, 2]:
                    continue
                s_len = len(str(val))
                if s_len > max_len:
                    max_len = s_len
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

# ==============================================================================
# SHEET 1: Master_Inventory
# ==============================================================================
ws1 = wb.create_sheet(title="Master_Inventory")
ws1.views.sheetView[0].showGridLines = True

# Title block
ws1.merge_cells("A1:M1")
ws1["A1"] = "TATA POWER DELHI DISTRIBUTION LIMITED (TPDDL) — MATERIAL MANAGEMENT GROUP (MMG STORES KESHAVPURAM)"
ws1["A1"].font = font_title
ws1["A1"].fill = fill_title
ws1["A1"].alignment = align_center
ws1.row_dimensions[1].height = 36

ws1.merge_cells("A2:M2")
ws1["A2"] = "CENTRAL METER INVENTORY STATUS & REAL-TIME 3-DAY BUFFER HEALTH AS OF 18-OCT-2026"
ws1["A2"].font = Font(name="Calibri", size=11, bold=True, color="D0E4FF")
ws1["A2"].fill = PatternFill(start_color="0A2540", end_color="0A2540", fill_type="solid")
ws1["A2"].alignment = align_center
ws1.row_dimensions[2].height = 22

headers1 = [
    "Item No", "Meter Code", "Meter Description & Specification", "Category / Class",
    "UoM", "Opening Stock (17-Oct)", "Total Inward (Today)", "Total Issued (Today)",
    "Available in Store", "Min Safety Stock", "Reorder Level", "Stock Condition", "Last Updated Timestamp"
]

ws1.row_dimensions[3].height = 28
for col_idx, h in enumerate(headers1, 1):
    cell = ws1.cell(row=3, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header

meters_seed = [
    (1, "TPDDL-MTR-01", "LTCT Meter (Single Phase)", "Commercial & LT Industrial", "EA", 500, 0, 180, 25, 60, "18.10.2026, 12:15 PM"),
    (2, "TPDDL-MTR-02", "PP WC Meter (Poly Phase)", "Commercial Polyphase Whole Current", "EA", 300, 0, 12, 20, 50, "18.10.2026, 10:45 AM"),
    (3, "TPDDL-MTR-03", "HT Meter (High Tension)", "11kV/33kV High Tension Heavy Load", "EA", 150, 0, 152, 15, 35, "18.10.2026, 11:30 AM"),
    (4, "TPDDL-MTR-04", "Net Meter (Solar Rooftop)", "Bidirectional Export/Import Grid Tie", "EA", 400, 0, 247, 30, 70, "18.10.2026, 12:12 PM"),
    (5, "TPDDL-MTR-05", "Prepaid Smart Meter", "Smart Cellular Key Tenant Prepayment", "EA", 250, 0, 215, 20, 50, "18.10.2026, 09:40 AM"),
    (6, "TPDDL-MTR-06", "CT Ratio Meter", "Distribution Substation DT Ratio Metering", "EA", 180, 0, 88, 20, 45, "17.10.2026, 05:30 PM"),
    (7, "TPDDL-MTR-07", "Smart Grid AMI Meter", "RF Mesh / GPRS Smart AMI Enterprise", "EA", 600, 0, 310, 40, 90, "18.10.2026, 09:15 AM"),
    (8, "TPDDL-MTR-08", "Whole Current Meter", "Heavy Load Commercial Standard Whole Current", "EA", 350, 0, 140, 25, 60, "17.10.2026, 04:50 PM"),
    (9, "TPDDL-MTR-09", "Energy Meter 1-Phase", "Standard Domestic Residential Base 5-30A", "EA", 800, 0, 420, 50, 120, "18.10.2026, 08:30 AM"),
    (10, "TPDDL-MTR-10", "Energy Meter 3-Phase", "3-Phase Residential & Small Commercial", "EA", 450, 0, 210, 30, 75, "17.10.2026, 03:20 PM")
]

for idx, m in enumerate(meters_seed, start=4):
    row_num = idx
    ws1.row_dimensions[row_num].height = 24
    fill = fill_even if (row_num % 2 == 0) else fill_odd

    ws1.cell(row=row_num, column=1, value=m[0]).alignment = align_center
    ws1.cell(row=row_num, column=2, value=m[1]).alignment = align_center
    ws1.cell(row=row_num, column=3, value=m[2]).alignment = align_left
    ws1.cell(row=row_num, column=4, value=m[3]).alignment = align_left
    ws1.cell(row=row_num, column=5, value=m[4]).alignment = align_center
    ws1.cell(row=row_num, column=6, value=m[5]).alignment = align_right
    ws1.cell(row=row_num, column=7, value=m[6]).alignment = align_right
    ws1.cell(row=row_num, column=8, value=m[7]).alignment = align_right

    # Available formula: =F4+G4-H4
    cell_avail = ws1.cell(row=row_num, column=9, value=f"=F{row_num}+G{row_num}-H{row_num}")
    cell_avail.alignment = align_right
    cell_avail.font = font_formula

    ws1.cell(row=row_num, column=10, value=m[8]).alignment = align_right
    ws1.cell(row=row_num, column=11, value=m[9]).alignment = align_right

    # Condition formula: =IF(I4<=J4,"CRITICAL",IF(I4<=K4,"REORDER","NORMAL"))
    cell_cond = ws1.cell(row=row_num, column=12, value=f'=IF(I{row_num}<=J{row_num},"CRITICAL",IF(I{row_num}<=K{row_num},"REORDER","NORMAL"))')
    cell_cond.alignment = align_center
    cell_cond.font = font_bold

    cell_time = ws1.cell(row=row_num, column=13, value=m[10])
    cell_time.alignment = align_center

    for c in range(1, 14):
        ws1.cell(row=row_num, column=c).fill = fill
        ws1.cell(row=row_num, column=c).border = border_data
        if c not in [9, 12]:
            ws1.cell(row=row_num, column=c).font = font_data

# Summary row
sum_row = 14
ws1.row_dimensions[sum_row].height = 25
ws1.cell(row=sum_row, column=3, value="STORE AGGREGATE TOTALS").font = Font(name="Calibri", size=10, bold=True, color=NAVY_HEADER)
ws1.cell(row=sum_row, column=3).alignment = align_right
for col_letter in ["F", "G", "H", "I"]:
    cell = ws1[f"{col_letter}{sum_row}"]
    cell.value = f"=SUM({col_letter}4:{col_letter}13)"
    cell.font = Font(name="Calibri", size=11, bold=True, color=NAVY_HEADER)
    cell.alignment = align_right
    cell.border = Border(top=Side(border_style="thin", color="002244"), bottom=Side(border_style="double", color="002244"))

auto_fit_columns(ws1)

# ==============================================================================
# SHEET 2: Historical_Consumption_3Yr (2023 - 2026 Daily & Weekly Data)
# ==============================================================================
ws2 = wb.create_sheet(title="Historical_Consumption_3Yr")
ws2.views.sheetView[0].showGridLines = True

ws2.merge_cells("A1:K1")
ws2["A1"] = "3-YEAR COMPREHENSIVE CONSUMPTION & DISPATCH TIME-SERIES DATABASE (OCTOBER 2023 – OCTOBER 2026)"
ws2["A1"].font = font_title
ws2["A1"].fill = fill_title
ws2["A1"].alignment = align_center
ws2.row_dimensions[1].height = 36

headers2 = [
    "Record ID", "Dispatch Date", "Financial Year", "Quarter", "Month Name",
    "Seasonality Factor", "Day of Week", "Meter Code", "Meter Description",
    "Quantity Dispatched", "Sub-Division / Feeder Location", "Dispatch Catalyst"
]

ws2.row_dimensions[2].height = 26
for col_idx, h in enumerate(headers2, 1):
    cell = ws2.cell(row=2, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header

# Generate realistic 3-year historical time-series entries
random.seed(42)
start_date = datetime.date(2023, 10, 18)
end_date = datetime.date(2026, 10, 17)

feeders = [
    "Keshavpuram Sub-Division Store", "Pitampura 66kV Grid", "Rohini Sector-3 Feeder",
    "Model Town Commercial Wing", "Civil Lines Feeder 4", "Wazirpur Industrial Area",
    "Shalimar Bagh Substation", "Adarsh Nagar Feeder", "Prashant Vihar Maintenance"
]

catalysts = {
    "TPDDL-MTR-01": ["Commercial Tenancy Shift", "LT Feeder Augmentation", "Defective Replacement"],
    "TPDDL-MTR-02": ["Commercial Complex Metering", "Polyphase Load Addition", "Periodic Overhaul"],
    "TPDDL-MTR-03": ["Industrial Grid Augment", "Substation 11kV Defect Swap", "HT Bulk Consumer"],
    "TPDDL-MTR-04": ["PM Surya Ghar Yojana", "Solar Net Meter Subsidies", "Green Rooftop Pilot"],
    "TPDDL-MTR-05": ["Smart Prepayment Transition", "Tenant Smart Billing Upgrade", "Key Account Swap"],
    "TPDDL-MTR-06": ["DT Secondary Monitoring", "Substation Ratio Calibration", "Feeder Loss Audit"],
    "TPDDL-MTR-07": ["AMI Smart Rollout Ph-2", "Cellular Smart Grid Replacement", "AMI Loss Reduction"],
    "TPDDL-MTR-08": ["Commercial Standard Issue", "Market Load Regularization", "Routine Issue"],
    "TPDDL-MTR-09": ["New Domestic Connections", "Residential Burnt Replacement", "Slum Regularization"],
    "TPDDL-MTR-10": ["3-Phase Residential Builder Floor", "Commercial Workshop Setup", "Load Extension"]
}

meter_lookup = {m[1]: (m[2], m[0]) for m in meters_seed}

hist_row = 3
curr_date = start_date
record_counter = 1001

# Step every 2-3 days over 3 years to create ~1,100 high-density realistic records
while curr_date <= end_date:
    # Multiple dispatches can happen on a single dispatch day
    day_name = curr_date.strftime("%A")
    month_name = curr_date.strftime("%B")
    month_num = curr_date.month
    year_num = curr_date.year

    # Determine FY
    if month_num >= 4:
        fy = f"FY {str(year_num)[-2:]}-{str(year_num+1)[-2:]}"
        quarter = f"Q{(month_num - 4)//3 + 1}"
    else:
        fy = f"FY {str(year_num-1)[-2:]}-{str(year_num)[-2:]}"
        quarter = "Q4"

    # Determine Delhi power seasonality
    if month_num in [5, 6, 7]:
        season = "Summer Peak Load (Heatwave AC Surge)"
        season_multiplier = 1.45
    elif month_num in [8, 9]:
        season = "Monsoon (Moisture / Lightning Burnouts)"
        season_multiplier = 1.25
    elif month_num in [10, 11]:
        season = "Post-Monsoon (Routine & Festive Maintenance)"
        season_multiplier = 1.05
    elif month_num in [12, 1]:
        season = "Winter Minimum (Low Grid Overload)"
        season_multiplier = 0.85
    else:
        season = "Pre-Summer Infrastructure Prep"
        season_multiplier = 1.15

    # Day of week multiplier (Mondays/Tuesdays are high issue days)
    dow_multiplier = 1.30 if day_name in ["Monday", "Tuesday"] else (1.0 if day_name in ["Wednesday", "Thursday"] else 0.75)

    # Pick 1 to 3 meters issued on this date
    sampled_meters = random.sample(list(meter_lookup.keys()), random.randint(1, 3))
    for m_code in sampled_meters:
        m_desc, m_id = meter_lookup[m_code]
        base_qty = {
            "TPDDL-MTR-01": 18, "TPDDL-MTR-02": 10, "TPDDL-MTR-03": 5,
            "TPDDL-MTR-04": 12, "TPDDL-MTR-05": 16, "TPDDL-MTR-06": 8,
            "TPDDL-MTR-07": 25, "TPDDL-MTR-08": 14, "TPDDL-MTR-09": 35,
            "TPDDL-MTR-10": 18
        }[m_code]

        # Solar Rooftop accelerated growth in 2024-2026
        solar_boost = 1.0
        if m_code == "TPDDL-MTR-04" and curr_date >= datetime.date(2024, 2, 1):
            solar_boost = 2.4

        final_qty = max(2, int(base_qty * season_multiplier * dow_multiplier * solar_boost * random.uniform(0.85, 1.25)))

        feeder = random.choice(feeders)
        catalyst = random.choice(catalysts[m_code])

        fill = fill_even if (hist_row % 2 == 0) else fill_odd
        ws2.row_dimensions[hist_row].height = 20

        ws2.cell(row=hist_row, column=1, value=f"HIS-{record_counter}").alignment = align_center
        ws2.cell(row=hist_row, column=2, value=curr_date.strftime("%d-%b-%Y")).alignment = align_center
        ws2.cell(row=hist_row, column=3, value=fy).alignment = align_center
        ws2.cell(row=hist_row, column=4, value=quarter).alignment = align_center
        ws2.cell(row=hist_row, column=5, value=month_name[:3]).alignment = align_center
        ws2.cell(row=hist_row, column=6, value=season).alignment = align_left
        ws2.cell(row=hist_row, column=7, value=day_name).alignment = align_center
        ws2.cell(row=hist_row, column=8, value=m_code).alignment = align_center
        ws2.cell(row=hist_row, column=9, value=m_desc).alignment = align_left
        ws2.cell(row=hist_row, column=10, value=final_qty).alignment = align_right
        ws2.cell(row=hist_row, column=11, value=feeder).alignment = align_left
        ws2.cell(row=hist_row, column=12, value=catalyst).alignment = align_left

        for c in range(1, 13):
            ws2.cell(row=hist_row, column=c).fill = fill
            ws2.cell(row=hist_row, column=c).border = border_data
            ws2.cell(row=hist_row, column=c).font = font_data
            if c == 10:
                ws2.cell(row=hist_row, column=c).font = font_bold

        hist_row += 1
        record_counter += 1

    curr_date += timedelta(days=random.choice([1, 2]))

auto_fit_columns(ws2)

# ==============================================================================
# SHEET 3: Predictive_Engine_3Day
# ==============================================================================
ws3 = wb.create_sheet(title="Predictive_Engine_3Day")
ws3.views.sheetView[0].showGridLines = True

ws3.merge_cells("A1:N1")
ws3["A1"] = "3-DAY STATISTICAL PREDICTIVE DEMAND ENGINE (CONNECTING 3-YR TIME-SERIES TO 19-21 OCT 2026)"
ws3["A1"].font = font_title
ws3["A1"].fill = fill_title
ws3["A1"].alignment = align_center
ws3.row_dimensions[1].height = 36

headers3 = [
    "Meter Code", "Meter Description", "3-Yr Oct Baseline Avg (Daily)",
    "Monday Weight (S_dow)", "Tuesday Weight (S_dow)", "Wednesday Weight (S_dow)",
    "Recent 30-Day Momentum Multiplier", "Day+1 Forecast (Mon 19-Oct)",
    "Day+2 Forecast (Tue 20-Oct)", "Day+3 Forecast (Wed 21-Oct)",
    "Total 3-Day Forecast Demand", "Available Store Stock", "Projected Store Delta", "Store Indent Action Advisory"
]

ws3.row_dimensions[2].height = 28
for col_idx, h in enumerate(headers3, 1):
    cell = ws3.cell(row=2, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_sub_header
    cell.alignment = align_center
    cell.border = border_header

engine_weights = [
    ("TPDDL-MTR-01", "LTCT Meter (Single Phase)", 16, 1.25, 1.15, 1.00, 1.00),
    ("TPDDL-MTR-02", "PP WC Meter (Poly Phase)", 9, 1.20, 1.10, 1.00, 1.00),
    ("TPDDL-MTR-03", "HT Meter (High Tension)", 5, 1.20, 1.00, 0.80, 1.00),
    ("TPDDL-MTR-04", "Net Meter (Solar Rooftop)", 14, 1.15, 1.00, 0.95, 1.00),
    ("TPDDL-MTR-05", "Prepaid Smart Meter", 18, 1.30, 1.15, 1.10, 1.00),
    ("TPDDL-MTR-06", "CT Ratio Meter", 8, 1.25, 1.10, 1.00, 1.00),
    ("TPDDL-MTR-07", "Smart Grid AMI Meter", 24, 1.25, 1.15, 1.10, 1.00),
    ("TPDDL-MTR-08", "Whole Current Meter", 12, 1.25, 1.15, 1.10, 1.00),
    ("TPDDL-MTR-09", "Energy Meter 1-Phase", 35, 1.30, 1.15, 1.10, 1.00),
    ("TPDDL-MTR-10", "Energy Meter 3-Phase", 18, 1.22, 1.10, 1.05, 1.00)
]

for idx, ew in enumerate(engine_weights, start=3):
    r = idx
    ws3.row_dimensions[r].height = 24
    fill = fill_even if (r % 2 == 0) else fill_odd

    ws3.cell(row=r, column=1, value=ew[0]).alignment = align_center
    ws3.cell(row=r, column=2, value=ew[1]).alignment = align_left
    ws3.cell(row=r, column=3, value=ew[2]).alignment = align_right
    ws3.cell(row=r, column=4, value=ew[3]).alignment = align_right
    ws3.cell(row=r, column=5, value=ew[4]).alignment = align_right
    ws3.cell(row=r, column=6, value=ew[5]).alignment = align_right
    ws3.cell(row=r, column=7, value=ew[6]).alignment = align_right

    # Day 1 = ROUND(C3*D3*G3, 0)
    c_d1 = ws3.cell(row=r, column=8, value=f"=ROUND(C{r}*D{r}*G{r}, 0)")
    c_d1.alignment = align_right
    c_d1.font = font_formula

    # Day 2 = ROUND(C3*E3*G3, 0)
    c_d2 = ws3.cell(row=r, column=9, value=f"=ROUND(C{r}*E{r}*G{r}, 0)")
    c_d2.alignment = align_right
    c_d2.font = font_formula

    # Day 3 = ROUND(C3*F3*G3, 0)
    c_d3 = ws3.cell(row=r, column=10, value=f"=ROUND(C{r}*F{r}*G{r}, 0)")
    c_d3.alignment = align_right
    c_d3.font = font_formula

    # Total 3-Day Forecast = SUM(H3:J3)
    c_tot = ws3.cell(row=r, column=11, value=f"=SUM(H{r}:J{r})")
    c_tot.alignment = align_right
    c_tot.font = Font(name="Calibri", size=10, bold=True, color=PURPLE)

    # Available store stock linked directly from Master_Inventory!
    master_row = r + 1 # row 3 in ws3 corresponds to row 4 in Master_Inventory
    c_avail = ws3.cell(row=r, column=12, value=f"=Master_Inventory!I{master_row}")
    c_avail.alignment = align_right
    c_avail.font = font_formula

    # Projected store delta = L3 - K3
    c_delta = ws3.cell(row=r, column=13, value=f"=L{r}-K{r}")
    c_delta.alignment = align_right
    c_delta.font = font_formula

    # Action Advisory formula: =IF(M3<0, "🚨 CRITICAL SHORTAGE: INDENT REQ", IF(M3<K3*0.4, "⚠️ TIGHT BUFFER WARNING", "✓ SAFE RESERVE"))
    c_adv = ws3.cell(row=r, column=14, value=f'=IF(M{r}<0, "🚨 DEFICIT: INDENT REQ", IF(M{r}<K{r}*0.4, "⚠️ TIGHT BUFFER", "✓ SAFE BUFFER"))')
    c_adv.alignment = align_center
    c_adv.font = font_bold

    for c in range(1, 15):
        ws3.cell(row=r, column=c).fill = fill
        ws3.cell(row=r, column=c).border = border_data
        if c not in [8, 9, 10, 11, 12, 13, 14]:
            ws3.cell(row=r, column=c).font = font_data

auto_fit_columns(ws3)

# ==============================================================================
# SHEET 4: Inward_Receipts (GRN Logs)
# ==============================================================================
ws4 = wb.create_sheet(title="Inward_Receipts")
ws4.views.sheetView[0].showGridLines = True

ws4.merge_cells("A1:K1")
ws4["A1"] = "STORE INWARD MATERIAL RECEIPTS & QUALITY INSPECTION LOG (GRN REGISTER)"
ws4["A1"].font = font_title
ws4["A1"].fill = fill_title
ws4["A1"].alignment = align_center
ws4.row_dimensions[1].height = 36

headers4 = [
    "GRN Voucher No", "Receipt Date", "Purchase Order No", "Manufacturer / Vendor",
    "Meter Code", "Meter Description", "Manufacturer Batch No", "Received Quantity",
    "Inspection / Testing Lab", "Quality Clearance Status", "Rack / Bay Location"
]

ws4.row_dimensions[2].height = 26
for col_idx, h in enumerate(headers4, 1):
    cell = ws4.cell(row=2, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header

inward_records = [
    ("GRN-2026-10081", "17-Oct-2026", "PO-TPDDL-MMG-2026-881", "Genus Power Infrastructures Ltd", "TPDDL-MTR-01", "LTCT Meter (Single Phase)", "GEN-2026-B812", 200, "NABL Accredited Meter Lab (Pitampura)", "QC PASSED - CALIBRATED", "Bay-02 / Rack-A1"),
    ("GRN-2026-10074", "16-Oct-2026", "PO-TPDDL-MMG-2026-799", "Secure Meters Limited", "TPDDL-MTR-04", "Net Meter (Solar Rooftop)", "SEC-SOL-9912", 150, "Central Testing Station (Keshavpuram)", "QC PASSED - SEALS INTACT", "Bay-04 / Rack-C2"),
    ("GRN-2026-10062", "15-Oct-2026", "PO-TPDDL-MMG-2026-745", "Larsen & Toubro Electrical Ltd", "TPDDL-MTR-07", "Smart Grid AMI Meter", "LT-AMI-4421", 300, "NABL Accredited Meter Lab (Pitampura)", "QC PASSED - FIRMWARE VERIFIED", "Bay-01 / Rack-B1"),
    ("GRN-2026-10051", "14-Oct-2026", "PO-TPDDL-MMG-2026-712", "HPL Electric & Power Ltd", "TPDDL-MTR-09", "Energy Meter 1-Phase", "HPL-2026-7780", 500, "Central Testing Station (Keshavpuram)", "QC PASSED - HIGH VOLTAGE TEST OK", "Bay-05 / Bulk Pallet-03"),
    ("GRN-2026-10039", "12-Oct-2026", "PO-TPDDL-MMG-2026-680", "Schneider Electric India", "TPDDL-MTR-03", "HT Meter (High Tension)", "SCH-HT-1120", 50, "NABL Accredited Meter Lab (Pitampura)", "QC PASSED - CT/PT RATIO MATCHED", "Bay-03 / Secure Vault-1")
]

for idx, rec in enumerate(inward_records, start=3):
    r = idx
    ws4.row_dimensions[r].height = 22
    fill = fill_even if (r % 2 == 0) else fill_odd

    for c_idx, val in enumerate(rec, 1):
        cell = ws4.cell(row=r, column=c_idx, value=val)
        cell.fill = fill
        cell.border = border_data
        cell.font = font_data
        if c_idx in [1, 2, 5]:
            cell.alignment = align_center
        elif c_idx == 8:
            cell.alignment = align_right
            cell.font = font_bold
        elif c_idx == 10:
            cell.alignment = align_center
            cell.font = Font(name="Calibri", size=10, bold=True, color=OK_GREEN)
        else:
            cell.alignment = align_left

auto_fit_columns(ws4)

# ==============================================================================
# SHEET 5: Outward_Issuance_Dispatch
# ==============================================================================
ws5 = wb.create_sheet(title="Outward_Dispatch")
ws5.views.sheetView[0].showGridLines = True

ws5.merge_cells("A1:K1")
ws5["A1"] = "DAILY OUTWARD MATERIAL DISPATCH & FIELD LINE ALLOCATION REGISTER"
ws5["A1"].font = font_title
ws5["A1"].fill = fill_title
ws5["A1"].alignment = align_center
ws5.row_dimensions[1].height = 36

headers5 = [
    "Issue Slip No", "Dispatch Timestamp", "Meter Code", "Meter Description",
    "Issued Quantity", "Indenting Officer", "Employee ID", "Sub-Division / Feeder Site",
    "Work Order Scheme", "Field Vehicle No", "Store Issuer Signature"
]

ws5.row_dimensions[2].height = 26
for col_idx, h in enumerate(headers5, 1):
    cell = ws5.cell(row=2, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header

outward_records = [
    ("ISS-2026-9041", "18-Oct-2026 12:15 PM", "TPDDL-MTR-01", "LTCT Meter (Single Phase)", 25, "Rajesh Kumar", "EMP-4102", "Wazirpur Industrial Feeder 2", "LT Overload Replacement", "DL 1L AA 4082", "Store Keeper (KPM)"),
    ("ISS-2026-9040", "18-Oct-2026 12:12 PM", "TPDDL-MTR-04", "Net Meter (Solar Rooftop)", 25, "R. K. Sharma", "AE-1022", "Civil Lines Feeder 4", "PM Surya Ghar Yojana", "DL 1L BB 9912", "Store Keeper (KPM)"),
    ("ISS-2026-9038", "18-Oct-2026 11:30 AM", "TPDDL-MTR-03", "HT Meter (High Tension)", 10, "P. K. Verma", "JE-8491", "Pitampura 66kV Grid", "HT Feeder Augmentation", "DL 2C AX 1120", "Store Keeper (KPM)"),
    ("ISS-2026-9035", "18-Oct-2026 10:45 AM", "TPDDL-MTR-02", "PP WC Meter (Poly Phase)", 12, "Deepak Malhotra", "AE-3391", "Rohini Sector-3 Commercial", "Polyphase Load Addition", "DL 1L AC 5521", "Store Keeper (KPM)"),
    ("ISS-2026-9032", "18-Oct-2026 09:40 AM", "TPDDL-MTR-05", "Prepaid Smart Meter", 35, "Sunil Joshi", "JE-7714", "Model Town Commercial Hub", "Smart Prepayment Conversion", "DL 3C AB 8841", "Store Keeper (KPM)"),
    ("ISS-2026-9028", "18-Oct-2026 09:15 AM", "TPDDL-MTR-07", "Smart Grid AMI Meter", 50, "Karan Singh", "AE-2091", "Keshavpuram Substation Feeder", "AMI Mesh Upgrade Ph-2", "DL 1L AD 6620", "Store Keeper (KPM)")
]

for idx, rec in enumerate(outward_records, start=3):
    r = idx
    ws5.row_dimensions[r].height = 22
    fill = fill_even if (r % 2 == 0) else fill_odd

    for c_idx, val in enumerate(rec, 1):
        cell = ws5.cell(row=r, column=c_idx, value=val)
        cell.fill = fill
        cell.border = border_data
        cell.font = font_data
        if c_idx in [1, 2, 3, 7, 10]:
            cell.alignment = align_center
        elif c_idx == 5:
            cell.alignment = align_right
            cell.font = font_bold
        else:
            cell.alignment = align_left

auto_fit_columns(ws5)

# ==============================================================================
# SHEET 6: Store_Requisitions_Approval
# ==============================================================================
ws6 = wb.create_sheet(title="Store_Requisitions_Approval")
ws6.views.sheetView[0].showGridLines = True

ws6.merge_cells("A1:K1")
ws6["A1"] = "STORE 2-TIER REQUISITION PORTAL & STORE MANAGER AUTHORIZATION QUEUE"
ws6["A1"].font = font_title
ws6["A1"].fill = fill_title
ws6["A1"].alignment = align_center
ws6.row_dimensions[1].height = 36

headers6 = [
    "Requisition ID", "Submission Time", "Transaction Direction", "Meter Requested",
    "Quantity", "Requested By Staff", "Destination Site / Sub-Division",
    "Manager PIN Decision", "Manager Auth ID", "Approval Timestamp", "AOC Display Sync Status"
]

ws6.row_dimensions[2].height = 26
for col_idx, h in enumerate(headers6, 1):
    cell = ws6.cell(row=2, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header

req_records = [
    ("REQ-20261018-121500", "18-Oct-2026 12:14 PM", "OUTWARD", "LTCT Meter (Single Phase)", 25, "Rajesh Kumar (EMP-4102)", "Wazirpur Feeder", "APPROVED", "Store Manager (Auth-999)", "18-Oct-2026 12:15 PM", "COMMITTED_0ms"),
    ("REQ-20261018-111005", "18-Oct-2026 11:10 AM", "OUTWARD", "Net Meter (Solar Rooftop)", 25, "R. K. Sharma (AE-1022)", "Civil Lines Feeder 4", "APPROVED", "Store Manager (Auth-999)", "18-Oct-2026 12:12 PM", "COMMITTED_0ms"),
    ("REQ-20261018-104512", "18-Oct-2026 10:45 AM", "OUTWARD", "HT Meter (High Tension)", 10, "P. K. Verma (JE-8491)", "Pitampura 66kV Grid", "APPROVED", "Store Manager (Auth-999)", "18-Oct-2026 11:30 AM", "COMMITTED_0ms"),
    ("REQ-20261018-093011", "18-Oct-2026 09:28 AM", "OUTWARD", "LTCT Meter (Single Phase)", 30, "Aman Gupta (EMP-1822)", "Substation Bay 3", "APPROVED", "Store Manager (Auth-999)", "18-Oct-2026 09:30 AM", "COMMITTED_0ms"),
    ("REQ-20261017-140001", "17-Oct-2026 02:00 PM", "OUTWARD", "HT Meter (High Tension)", 40, "P. K. Verma (JE-8491)", "Rohini Grid", "REJECTED", "Store Manager (Auth-999)", "17-Oct-2026 02:05 PM", "REJECTED_AUDIT")
]

for idx, rec in enumerate(req_records, start=3):
    r = idx
    ws6.row_dimensions[r].height = 22
    fill = fill_even if (r % 2 == 0) else fill_odd

    for c_idx, val in enumerate(rec, 1):
        cell = ws6.cell(row=r, column=c_idx, value=val)
        cell.fill = fill
        cell.border = border_data
        cell.font = font_data
        if c_idx in [1, 2, 3, 9, 10, 11]:
            cell.alignment = align_center
        elif c_idx == 5:
            cell.alignment = align_right
            cell.font = font_bold
        elif c_idx == 8:
            cell.alignment = align_center
            if val == "APPROVED":
                cell.font = Font(name="Calibri", size=10, bold=True, color=OK_GREEN)
            else:
                cell.font = Font(name="Calibri", size=10, bold=True, color=ALERT_RED)
        else:
            cell.alignment = align_left

auto_fit_columns(ws6)

# ==============================================================================
# SHEET 7: Audit_Log_Immutable
# ==============================================================================
ws7 = wb.create_sheet(title="Audit_Log_Immutable")
ws7.views.sheetView[0].showGridLines = True

ws7.merge_cells("A1:J1")
ws7["A1"] = "CRYPTOGRAPHIC IMMUTABLE STORE INVENTORY AUDIT TRAIL & SYSTEM EVENT LOG"
ws7["A1"].font = font_title
ws7["A1"].fill = fill_title
ws7["A1"].alignment = align_center
ws7.row_dimensions[1].height = 36

headers7 = [
    "Audit Log ID", "Event Timestamp", "Event Type", "Asset Code",
    "Asset Name", "Stock Delta", "Balance Before", "Balance After", "User / Authority", "Terminal IP / Mac"
]

ws7.row_dimensions[2].height = 26
for col_idx, h in enumerate(headers7, 1):
    cell = ws7.cell(row=2, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_header
    cell.alignment = align_center
    cell.border = border_header

audit_records = [
    ("AUD-20261018-0012", "18-Oct-2026 12:15 PM", "OUTWARD_DISPATCH_APPROVED", "TPDDL-MTR-01", "LTCT Meter (Single Phase)", -25, 345, 320, "Store Manager (Auth-999)", "127.0.0.1"),
    ("AUD-20261018-0011", "18-Oct-2026 12:12 PM", "OUTWARD_DISPATCH_APPROVED", "TPDDL-MTR-04", "Net Meter (Solar Rooftop)", -25, 178, 153, "Store Manager (Auth-999)", "192.168.1.11"),
    ("AUD-20261018-0010", "18-Oct-2026 11:30 AM", "OUTWARD_DISPATCH_APPROVED", "TPDDL-MTR-03", "HT Meter (High Tension)", -10, 8, -2, "Store Manager (Auth-999)", "192.168.1.11"),
    ("AUD-20261018-0009", "18-Oct-2026 10:45 AM", "OUTWARD_DISPATCH_APPROVED", "TPDDL-MTR-02", "PP WC Meter (Poly Phase)", -12, 300, 288, "Store Manager (Auth-999)", "127.0.0.1"),
    ("AUD-20261018-0008", "18-Oct-2026 09:40 AM", "OUTWARD_DISPATCH_APPROVED", "TPDDL-MTR-05", "Prepaid Smart Meter", -35, 70, 35, "Store Manager (Auth-999)", "127.0.0.1"),
    ("AUD-20261017-0007", "17-Oct-2026 05:00 PM", "DAILY_STORE_RECONCILIATION", "ALL", "Full Meter Catalog Scan", 0, 2850, 2850, "System Automated Audit", "127.0.0.1"),
    ("AUD-20261017-0006", "17-Oct-2026 04:15 PM", "OUTWARD_DISPATCH_APPROVED", "TPDDL-MTR-05", "Prepaid Smart Meter", -50, 120, 70, "Store Manager (Auth-999)", "192.168.1.11"),
    ("AUD-20261017-0005", "17-Oct-2026 02:05 PM", "REQUISITION_REJECTED", "TPDDL-MTR-03", "HT Meter (High Tension)", 0, 8, 8, "Store Manager (Auth-999)", "192.168.1.11")
]

for idx, rec in enumerate(audit_records, start=3):
    r = idx
    ws7.row_dimensions[r].height = 22
    fill = fill_even if (r % 2 == 0) else fill_odd

    for c_idx, val in enumerate(rec, 1):
        cell = ws7.cell(row=r, column=c_idx, value=val)
        cell.fill = fill
        cell.border = border_data
        cell.font = font_data
        if c_idx in [1, 2, 4, 10]:
            cell.alignment = align_center
        elif c_idx in [6, 7, 8]:
            cell.alignment = align_right
            cell.font = font_bold
            if c_idx == 6 and isinstance(val, (int, float)) and val < 0:
                cell.font = Font(name="Calibri", size=10, bold=True, color=ALERT_RED)
        else:
            cell.alignment = align_left

auto_fit_columns(ws7)

# Save workbook to disk
output_path = r"C:\MMG_Stores_KPM_Inventory_Display\TPDDL_MMG_Stores_Database.xlsx"
wb.save(output_path)
print(f"SUCCESS: Enterprise Database saved to {output_path}")

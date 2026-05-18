from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

SHEET_ID = "1muQ7GR7RbVtOBYS3nV-xy7VCq66QqE04TqFxZo5ndtg"
CREDS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "timecard_app", "timecard-493502-41862f5c212d.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_sheet():
    creds = Credentials.from_service_account_file(os.path.abspath(CREDS_PATH), scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID)

def parse_time(t):
    if not t:
        return None
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            pass
    return None

def calc_jissabaki(punch_in, punch_out, break_min):
    ti = parse_time(punch_in)
    to = parse_time(punch_out)
    if not ti or not to:
        return ""
    delta = to - ti - timedelta(minutes=int(break_min or 0))
    if delta.total_seconds() < 0:
        return "0:00"
    h = int(delta.total_seconds() // 3600)
    m = int((delta.total_seconds() % 3600) // 60)
    return f"{h}:{m:02d}"

@app.route("/api/staff")
def get_staff():
    try:
        sh = get_sheet()
        ws = sh.worksheet("スタッフ名簿")
        names = [r[0] for r in ws.get_all_values()[1:] if r and r[0].strip()]
        return jsonify({"names": names})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/record")
def get_record():
    name = request.args.get("name", "")
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    try:
        sh = get_sheet()
        ws = sh.worksheet(name)
        rows = ws.get_all_values()
        for row in rows[1:]:
            if row and row[0] == date_str:
                return jsonify({
                    "date": row[0] if len(row) > 0 else "",
                    "punch_in": row[1] if len(row) > 1 else "",
                    "punch_out": row[2] if len(row) > 2 else "",
                    "break_min": row[3] if len(row) > 3 else "60",
                    "jissabaki": row[4] if len(row) > 4 else "",
                })
        return jsonify({"date": date_str, "punch_in": "", "punch_out": "", "break_min": "60", "jissabaki": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/weekly")
def get_weekly():
    name = request.args.get("name", "")
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    week_dates = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    try:
        sh = get_sheet()
        ws = sh.worksheet(name)
        rows = ws.get_all_values()
        row_map = {r[0]: r for r in rows[1:] if r and r[0]}
        result = []
        for d in week_dates:
            row = row_map.get(d, [])
            jissabaki = row[4] if len(row) > 4 else ""
            hours = 0.0
            if jissabaki:
                parts = jissabaki.split(":")
                try:
                    hours = int(parts[0]) + int(parts[1]) / 60
                except Exception:
                    pass
            result.append({"date": d, "hours": round(hours, 2)})
        return jsonify({"week": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/punch", methods=["POST"])
def punch():
    data = request.json
    name = data.get("name", "")
    ptype = data.get("type", "")  # "in" or "out"
    time_str = data.get("time", "")
    break_min = data.get("break_min", 60)
    date_str = datetime.now().strftime("%Y-%m-%d")

    try:
        sh = get_sheet()
        ws = sh.worksheet(name)
        rows = ws.get_all_values()
        row_idx = None
        for i, row in enumerate(rows):
            if row and row[0] == date_str:
                row_idx = i + 1  # 1-indexed
                break

        if ptype == "in":
            if row_idx:
                ws.update_cell(row_idx, 2, time_str)
            else:
                ws.append_row([date_str, time_str, "", "", ""])
            return jsonify({"ok": True, "punch_in": time_str})

        elif ptype == "out":
            if row_idx:
                punch_in = rows[row_idx - 1][1] if len(rows[row_idx - 1]) > 1 else ""
                jissabaki = calc_jissabaki(punch_in, time_str, break_min)
                ws.update_cell(row_idx, 3, time_str)
                ws.update_cell(row_idx, 4, str(break_min))
                ws.update_cell(row_idx, 5, jissabaki)
            else:
                ws.append_row([date_str, "", time_str, str(break_min), ""])
            return jsonify({"ok": True, "punch_out": time_str})

        return jsonify({"error": "invalid type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5050, debug=True)

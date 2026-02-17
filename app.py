from flask import Flask, render_template, request, send_file
import pandas as pd
import os
import re

app = Flask(__name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================
# PROVIDER LIST
# =========================
PROVIDERS = [
    ("ANDERSON", "TYLER"),
    ("COYNER", "KARL"),
    ("FOULARD", "GEORGE"),
    ("HOLALKERE", "NAGARAJ"),
    ("KIHIRA", "SHINGO"),
    ("KINGSBURY", "JAMES"),
    ("MAHMOOD", "YOUSAF"),
    ("ORD", "JUSTIN"),
    ("PAVLOCK", "STEPHEN"),
    ("PETRINI", "BART"),
    ("RODGERS", "ANDREW"),
    ("SCALFANI", "THERESA"),
    ("TANK", "JAY"),
    ("TASH", "TIMOTHY"),
    ("TSAI", "DOUGLAS"),
    ("WINTERS", "RONALD"),
    ("BREEN", "MICHAEL"),
    ("OMODON", "MELVIN"),
    ("ELAKKAD", "AHMED"),
    ("SOLOMON", "JASON")
]

# =========================
# HELPER FUNCTIONS
# =========================

def normalize(text):
    """Uppercase, remove punctuation, remove MD/DR"""
    text = str(text).upper()
    text = re.sub(r"[^A-Z ]", " ", text)  # remove commas, dots
    text = text.replace(" MD", "").replace(" DR", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def provider_matches(provider_name):
    if pd.isna(provider_name):
        return False

    provider_name = normalize(provider_name)

    for last, first in PROVIDERS:
        if last in provider_name and first in provider_name:
            return True

    return False

def append_q6(value):
    if pd.isna(value):
        return "Q6"

    value = str(value).strip()

    if value == "" or value.upper() == "NA":
        return "Q6"

    if "Q6" in value.upper():
        return value

    return value + ",Q6"

# =========================
# ROUTES
# =========================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]

        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(OUTPUT_FOLDER, "Q6_" + file.filename)

        file.save(input_path)

        df = pd.read_excel(input_path, dtype=str)
        df.columns = df.columns.str.strip()

        # 🔴 REQUIRED COLUMNS CHECK
        if "Service Provider" not in df.columns or "Modifier" not in df.columns:
            return "Required columns not found: Service Provider / Modifier"

        # Normalize provider column
        df["Service Provider"] = df["Service Provider"].astype(str)

        # Match providers
        mask = df["Service Provider"].apply(provider_matches)

        print("TOTAL ROWS:", len(df))
        print("MATCHED ROWS:", mask.sum())
        print(df.loc[mask, ["Service Provider", "Modifier"]].head(10))

        # Append Q6
        df.loc[mask, "Modifier"] = df.loc[mask, "Modifier"].apply(append_q6)

        df.to_excel(output_path, index=False)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run()


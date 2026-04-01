import pandas as pd

def generate_report(csv_path="output/data.csv"):
    df = pd.read_csv(csv_path)

    report = {}

    report["precio_promedio_por_plataforma"] = (
        df.groupby("platform")["item_price"].mean().to_dict()
    )

    report["delivery_fee_promedio"] = (
        df.groupby("platform")["delivery_fee"].mean().to_dict()
    )

    report["service_fee_promedio"] = (
        df.groupby("platform")["service_fee"].mean().to_dict()
    )

    report["eta_promedio"] = (
        df.groupby("platform")[["eta_min", "eta_max"]].mean().to_dict()
    )

    report["precio_por_zona"] = (
        df.groupby(["platform", "address_id"])["item_price"].mean().to_dict()
    )

    return report

def save_report(report, path="output/report.txt"):
    with open(path, "w", encoding="utf-8") as f:
        for section, data in report.items():
            f.write(f"\n=== {section.upper()} ===\n")
            for k, v in data.items():
                f.write(f"{k}: {v}\n")
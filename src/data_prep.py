import argparse
import os
import glob
import pandas as pd
import yaml


def load_raw_transactions(raw_dir):
    """Load CSV/JSON files from raw_dir into a single DataFrame.

    This function looks for .csv and .json files recursively under raw_dir.
    It concatenates them into a single pandas.DataFrame. The caller should
    ensure the files share a compatible schema or perform downstream
    normalization.
    """
    paths = glob.glob(os.path.join(raw_dir, "**", "*.csv"), recursive=True) + \
            glob.glob(os.path.join(raw_dir, "**", "*.json"), recursive=True)
    if not paths:
        raise FileNotFoundError(f"No CSV/JSON files found in {raw_dir}")
    dfs = []
    for p in paths:
        if p.lower().endswith(".csv"):
            dfs.append(pd.read_csv(p))
        else:
            dfs.append(pd.read_json(p, lines=False))
    df = pd.concat(dfs, ignore_index=True, sort=False)
    return df


def normalize_transactions(df):
    """Normalize common PhonePe transaction fields and types.

    Expected target columns: state, district, date, transaction_count, transaction_amount, category
    """
    df = df.copy()
    # common renames
    renames = {
        "state_name": "state",
        "district_name": "district",
        "transactions": "transaction_count",
        "amount": "transaction_amount",
        "txn_count": "transaction_count",
        "txn_amount": "transaction_amount",
    }
    df.rename(columns={c: renames.get(c, c) for c in df.columns}, inplace=True)

    # Ensure columns exist
    for col in ["state", "district", "date", "transaction_count", "transaction_amount"]:
        if col not in df.columns:
            df[col] = pd.NA

    # Normalize datatypes
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["transaction_count"] = pd.to_numeric(df["transaction_count"], errors="coerce").fillna(0).astype(int)
    df["transaction_amount"] = pd.to_numeric(df["transaction_amount"], errors="coerce").fillna(0.0).astype(float)

    # Fill category if missing
    if "category" not in df.columns:
        df["category"] = "unknown"

    # Trim string columns
    for c in ["state", "district", "category"]:
        df[c] = df[c].astype(str).str.strip()

    return df


def save_processed(df, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)


def main(config_path=None, raw_dir=None, out_path=None):
    if config_path:
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
        raw_dir = raw_dir or cfg.get("raw_dir")
        out_path = out_path or cfg.get("processed_path")

    if not raw_dir or not out_path:
        raise ValueError("raw_dir and out_path must be provided either as args or in config.yml")

    df = load_raw_transactions(raw_dir)
    df = normalize_transactions(df)
    save_processed(df, out_path)
    print(f"Saved processed data to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare PhonePe transaction data")
    parser.add_argument("--config", help="Path to config.yml", default="config.yml")
    parser.add_argument("--raw-dir", help="Raw data directory (overrides config)")
    parser.add_argument("--out", help="Output processed CSV path (overrides config)")
    args = parser.parse_args()
    main(config_path=args.config, raw_dir=args.raw_dir, out_path=args.out)

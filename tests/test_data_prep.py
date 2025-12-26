import os
import pandas as pd
import tempfile
from src.data_prep import normalize_transactions, save_processed

def test_normalize_and_save(tmp_path):
    # create a small sample dataframe
    df = pd.DataFrame({
        'state': ['TestState'],
        'district': ['TestDistrict'],
        'date': ['2021-01-01'],
        'transaction_count': ['10'],
        'transaction_amount': ['100.5'],
        'category': ['recharge']
    })
    out = tmp_path / "out.csv"
    df_norm = normalize_transactions(df)
    save_processed(df_norm, str(out))
    assert out.exists()
    df2 = pd.read_csv(out)
    assert 'transaction_count' in df2.columns
    assert int(df2['transaction_count'].iloc[0]) == 10

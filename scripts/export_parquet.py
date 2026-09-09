#!/usr/bin/env python3
from pathlib import Path
import argparse
import pandas as pd

def main(root:Path):
    src=root/'data'/'processed'/'csv'; dst=root/'data'/'processed'/'parquet'; dst.mkdir(parents=True,exist_ok=True)
    try: import pyarrow  # noqa
    except ImportError as e: raise SystemExit('pyarrow non disponibile: pip install pyarrow') from e
    for p in sorted(src.glob('*.csv')):
        df=pd.read_csv(p,low_memory=False)
        df.to_parquet(dst/f'{p.stem}.parquet',index=False,engine='pyarrow')
        print(dst/f'{p.stem}.parquet')
if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]); args=a.parse_args(); main(args.root.resolve())

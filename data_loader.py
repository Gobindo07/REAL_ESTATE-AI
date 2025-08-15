import os
import pandas as pd

SAMPLE = """id,address,city,price,monthly_rent,monthly_expenses,vacancy_rate,rehab_cost,city_growth_rate,risk_flags
1,145 Pine Ridge Ave,Atlanta,240000,2400,650,0.06,10000,0.035,
2,78 Maplewood Dr,Austin,410000,3600,900,0.05,0,0.042,code_violation
3,12 Bayview Ct,Tampa,320000,3100,850,0.07,5000,0.038,distressed;lien
4,909 Fremont St,Phoenix,280000,2500,700,0.08,15000,0.033,
5,222 Cedar Ln,Charlotte,350000,2950,800,0.05,0,0.036,foreclosure
6,10 Oak Grove Rd,Nashville,330000,3050,820,0.06,8000,0.039,
7,51 River Bend Dr,Denver,450000,3700,950,0.05,12000,0.041,code_violation
8,88 Willow Park,Orlando,300000,2850,780,0.07,6000,0.037,distressed
"""

def _from_string():
    from io import StringIO
    return pd.read_csv(StringIO(SAMPLE))

def load_properties(path: str) -> pd.DataFrame:
    """Load properties CSV. If missing/empty/invalid, return built-in sample."""
    try:
        if not os.path.exists(path) or os.stat(path).st_size == 0:
            return _from_string()
        df = pd.read_csv(path)
        if df.empty or len(df.columns) < 3:
            return _from_string()
        return df
    except Exception:
        return _from_string()

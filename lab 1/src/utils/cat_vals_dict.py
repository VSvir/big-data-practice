from pathlib import Path

import pandas as pd


def get_categorical_values_dict() -> dict:
    cat_vals_dict = {}
    cat_cols = ('traffic_control_device', 
                'weather_condition', 
                'lighting_condition', 
                'first_crash_type', 
                'trafficway_type', 
                'alignment', 
                'roadway_surface_cond',
                'road_defect', 
                'intersection_related_i')
    
    data_paths = Path(__file__).parent.parent.parent / "data" / "accidents_info.csv", Path(__file__).parent.parent.parent / "data" / "road_conditions.csv"
    
    for path in data_paths:
        df = pd.read_csv(path).drop(columns='Unnamed: 0')
        for column in df.columns:
            if column in cat_cols:
                cat_vals_dict[column] = sorted(tuple(df[column].unique()))
    
    cat_vals_dict['crash_type'] = (
        'NO INJURY / DRIVE AWAY',
        'INJURY AND / OR TOW DUE TO CRASH'
    )

    return cat_vals_dict

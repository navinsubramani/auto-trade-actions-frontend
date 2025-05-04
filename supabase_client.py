import os
from supabase import create_client, Client
from supabase.client import ClientOptions
import pandas as pd
import numpy as np

url: str = os.getenv("database_url")
key: str = os.getenv("database_key")

class SupabaseClient:
    def __init__(self):
        self.supabase: Client = create_client(
            url, 
            key,
            options=ClientOptions(
                postgrest_client_timeout=20,
                storage_client_timeout=20,

            )
        )

    def get_tpsl_data(self):
        """
        Fetches the take profit and stop loss data from the database.
        """
        data = []
        try:
            response = self.supabase.table("tp-sl-table").select("*").execute()
            data = response.data
            # json data to pandas dataframe
            df = pd.DataFrame(data)
            df = df.reset_index(drop=True)
            
            return df
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def update_tpsl_row(self, id, row_df):
        """
        Updates a row in the take profit and stop loss table.
        """
        try:

            # Validation of the input data
            self.validate_tpsl_order(row_df)
            self.validate_side_terminology(row_df)
            self.validate_required_inputs(row_df)

            # Extract the values forom the dataframe
            ticker = row_df["ticker"].values[0]
            side = row_df["side"].values[0]
            strategy = row_df["strategy"].values[0]
            tp1 = row_df["tp1"].values[0]
            tp2 = row_df["tp2"].values[0]
            tp3 = row_df["tp3"].values[0]
            sl = row_df["sl"].values[0]
            response = self.supabase.table("tp-sl-table").update(
                {
                    "ticker": ticker,
                    "side": side,
                    "strategy": strategy,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "sl": sl
                }
            ).eq("id", id).execute()

            print(f"Updated row with id {id} in the database.")
            print(f"Response: {response}")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(f"{e}")
        
    def delete_tpsl_row(self, id):
        """
        Deletes a row in the take profit and stop loss table.
        """
        try:
            response = self.supabase.table("tp-sl-table").delete().eq("id", id).execute()
            print(f"Deleted row with id {id} from the database.")
            print(f"Response: {response}")
            
        
        except Exception as e:
            raise Exception(f"{e}")

    def insert_tpsl_row(self, row_df):
        """
        Inserts a row in the take profit and stop loss table.
        """
        try:
            # Validation of the input data
            self.validate_tpsl_order(row_df)
            self.validate_side_terminology(row_df)
            self.validate_required_inputs(row_df)

            # Extract the values forom the dataframe
            ticker = row_df["ticker"].values[0]
            side = row_df["side"].values[0]
            strategy = row_df["strategy"].values[0]
            tp1 = row_df["tp1"].values[0]
            tp2 = row_df["tp2"].values[0]
            tp3 = row_df["tp3"].values[0]
            sl = row_df["sl"].values[0]

            response = self.supabase.table("tp-sl-table").insert(
                {
                    "ticker": ticker,
                    "side": side,
                    "strategy": strategy,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "sl": sl
                }
            ).execute()

            print(f"Inserted row into the database.")
            print(f"Response: {response}")
            
            return response.data
        
        except Exception as e:
            print(f"An error occurred: {e}")
            raise Exception(f"{e}")
        

    def validate_tpsl_order(self, row_df):
        """
        Validates the take profit and stop loss order.
        """
        
        # Extract the values forom the dataframe
        ticker = row_df["ticker"].values[0]
        side = row_df["side"].values[0]
        strategy = row_df["strategy"].values[0]
        tp1 = row_df["tp1"].values[0]
        tp2 = row_df["tp2"].values[0]
        tp3 = row_df["tp3"].values[0]
        sl = row_df["sl"].values[0]

        # If strategy 1, 2 and call side. SL < TP1 < TP2 < TP3
        if strategy == "strategy1" or strategy == "strategy2":
            if side == "call":
                if sl < tp1 < tp2 < tp3:
                    return True
                else:
                    raise ValueError("Invalid order: Correct order is SL < TP1 < TP2 < TP3")
            elif side == "put":
                if sl > tp1 > tp2 > tp3:
                    return True
                else:
                    raise ValueError("Invalid order: Correct order is SL > TP1 > TP2 > TP3")
                
        # If strategy 4, then SL < TP1 and TP2 < TP3, irrespective of side
        elif strategy == "strategy4":
            if sl < tp1 < tp2 < tp3:
                return True
            else:
                raise ValueError("Invalid order: Correct order is SL < TP1 < TP2 < TP3")

        else:
            print("Invalid strategy.")
            return False
    
    def validate_side_terminology(self, row_df):
        side = row_df["side"].values[0]

        if side == "call" or side == "put":
            return True
        
        else:
            raise ValueError("Invalid value for side. It should be either call or put")
        
    def validate_required_inputs(self, row_df):
        # Extract the values forom the dataframe
        ticker = row_df["ticker"].values[0]
        side = row_df["side"].values[0]
        strategy = row_df["strategy"].values[0]
        tp1 = row_df["tp1"].values[0]
        tp2 = row_df["tp2"].values[0]
        tp3 = row_df["tp3"].values[0]
        sl = row_df["sl"].values[0]

        def is_number(value):
            try:
                return isinstance(value, (int, float)) and not isinstance(value, bool) and not np.isnan(value)
            except TypeError:
                return False
            return False

        if strategy in ["strategy1", "strategy2", "strategy4"]:
            if is_number(tp1) and is_number(tp2) and is_number(tp3) and is_number(sl):
                pass
            else:
                raise ValueError("TP1, TP2, TP3, SL are required numeric inputs")
            
        elif strategy == "strategy5":
            if is_number(sl) and not (is_number(tp1) or is_number(tp2) or is_number(tp3)):
                pass
            else:
                raise ValueError("Only SL is the required numeric input and other TP's should be igored")
            
    
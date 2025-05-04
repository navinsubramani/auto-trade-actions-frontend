import os
from supabase import create_client, Client
from supabase.client import ClientOptions
import pandas as pd

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
            
            return response.data
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def delete_tpsl_row(self, id):
        """
        Deletes a row in the take profit and stop loss table.
        """
        try:
            response = self.supabase.table("tp-sl-table").delete().eq("id", id).execute()
            print(f"Deleted row with id {id} from the database.")
            print(f"Response: {response}")
            
            return response.data
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


    def insert_tpsl_row(self, row_df):
        """
        Inserts a row in the take profit and stop loss table.
        """
        try:
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
            return None
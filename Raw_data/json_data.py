import pandas as pd


data    = {
    "data": [
      {
        "message": "Welcome SMS sent to user",
        "status": "SENT",
        "datetime": "2026-02-09T10:15:22",
        "description": "Initial onboarding message delivered successfully"
      },
      {
        "message": "OTP verification message",
        "status": "FAILED",
        "datetime": "2026-02-09T10:18:10",
        "description": "Network timeout while sending OTP"
      },
      {
        "message": "Payment confirmation",
        "status": "SENT",
        "datetime": "2026-02-09T10:22:41",
        "description": "Transaction successful notification"
      },
      {
        "message": "Daily reminder",
        "status": "PENDING",
        "datetime": "2026-02-09T10:30:00",
        "description": "Scheduled for later delivery"
      },
      {
        "message": "Promotion message",
        "status": "SENT",
        "datetime": "2026-02-09T10:35:12",
        "description": "Marketing campaign broadcast"
      }
    ]
  }
def today_msg():
        
        df = pd.DataFrame(data["data"])
        df["datetime"] = pd.to_datetime(df["datetime"])

        today_df = df[df["datetime"].dt.date == pd.Timestamp.today().date()]

        res = today_df["datetime"].count()
        
        return res

import pandas as pd
import requests
import json
import time
import io
import urllib.request
import ssl
import os
from datetime import datetime, timedelta

# Configuration
# Prefer Environment Variables (for GitHub Actions), fallback to hardcoded (for local)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "EAATG3oWpW0IBQfs879FBKjZBWKL2CtN4ZB8PCJdZBCxVlmptNZAXUfGjsJ8K4GrHzc1ujdbYhOz8Nz60N3NDXrTQJ0INU6SRcOc7HSjZC7iZCdMpEy9lWz7AQJRSHdzpZAOQgHnQrK4W94ZAEbwMJAvq5jpgSnroEoSVzLgQxLzVHdCNDBzey94yXQguz3vPygKD44rCGvq32WStRPj54ZCfz3PxjH2k7keriaO8EFPOzx9CnEkLlawXPXw9r7NOeb9ORDeyfE0TQl8caQasmCb6VhAv1")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "957011204161290")
VERSION = "v21.0"
TEMPLATE_NAME = "contract_ru"
ADMIN_TEMPLATE_NAME = "messages_sent"
ADMIN_ERROR_TEMPLATE = "admin_alert"
SHEET_ID = '1dKKrxe3oqX9mpEKU9PZFO947ZaELWfMqQcFsU0MgdY'
EXPORT_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx'
ADMIN_PHONE_NUMBER = "789969129844"

def send_template_message(recipient, name, date_str, contract_num, description):
    """Send WhatsApp template message to a client"""
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Meta Dashboard Quirk Fix:
    if str(recipient) == "79969129844" or str(recipient).endswith("9969129844"):
        recipient = "789969129844"
        
    data = {
        "messaging_product": "whatsapp",
        "to": str(recipient),
        "type": "template",
        "template": {
            "name": TEMPLATE_NAME,
            "language": {
                "code": "ru" 
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": str(name)     # {{1}}
                        },
                        {
                            "type": "text",
                            "text": str(date_str) # {{2}}
                        },
                        {
                            "type": "text",
                            "text": str(contract_num) # {{3}}
                        },
                        {
                            "type": "text",
                            "text": str(description) # {{4}}
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print(f"Success to {recipient}: {json.dumps(response.json())}")
            return True, None
        else:
            error_msg = response.text
            print(f"Failed to {recipient}: {error_msg}")
            return False, error_msg
    except Exception as e:
        print(f"Error sending to {recipient}: {e}")
        return False, str(e)

def send_admin_notification(names_list):
    """Send success notification to admin"""
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    names_str = ", ".join(names_list)
    print(f"Sending admin notification to {ADMIN_PHONE_NUMBER} with names: {names_str}")

    data = {
        "messaging_product": "whatsapp",
        "to": ADMIN_PHONE_NUMBER,
        "type": "template",
        "template": {
            "name": ADMIN_TEMPLATE_NAME,
            "language": {
                "code": "ru"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": names_str # {{1}} - names
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print(f"Admin notification sent.")
        else:
            print(f"Failed to send admin notification: {response.text}")
    except Exception as e:
        print(f"Error sending admin notification: {e}")

def send_error_notification(errors_list):
    """Send error notification to admin"""
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Format errors: "Name: Reason"
    # Truncate if too long for WhatsApp parameter (limit 1024 chars often)
    error_str = "; ".join(errors_list)[:1000]
    
    print(f"Sending ERROR notification to {ADMIN_PHONE_NUMBER}: {error_str}")

    data = {
        "messaging_product": "whatsapp",
        "to": ADMIN_PHONE_NUMBER,
        "type": "template",
        "template": {
            "name": ADMIN_ERROR_TEMPLATE,
            "language": {
                "code": "ru"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": error_str # {{1}} - error details
                        }
                    ]
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print(f"Admin ERROR notification sent.")
        else:
            print(f"Failed to send admin ERROR notification: {response.text}")
    except Exception as e:
        print(f"Error sending admin ERROR notification: {e}")

def run_notification_job():
    """Main job function - downloads sheet and sends notifications"""
    print(f"[{datetime.now()}] Starting notification job...")
    print(f"Downloading data directly from Google Sheet ({SHEET_ID})...")
    
    # SSL Context for download
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    sent_names = []
    failed_items = []

    try:
        with urllib.request.urlopen(EXPORT_URL, context=ctx) as response:
            file_content = response.read()
            
        df = pd.read_excel(io.BytesIO(file_content))
        print(f"Loaded {len(df)} rows.")
        
        # Iterate rows
        for index, row in df.iterrows():
            phone = row['Номер телефона']
            name = row['Имя']
            contract = row['Номер контракта']
            date_exp = row['Дата истечения']
            description = row['Описание контракта']
            
            if pd.isna(phone):
                continue
                
            # Clean phone number (remove .0 if float)
            try:
                phone = str(int(float(phone)))
            except:
                phone = str(phone)

            # Clean contract (remove .0 if float)
            try:
                contract = str(int(float(contract)))
            except:
                contract = str(contract)
            
            # Parse Expiration Date
            try:
                if isinstance(date_exp, datetime):
                     exp_date_obj = date_exp
                else:
                     # Assume string format DD.MM.YYYY
                     exp_date_obj = datetime.strptime(str(date_exp), "%d.%m.%Y")
                
                # Filter: "Expires in a month or earlier" => Date <= Now + 30 days
                # Note: This includes dates in the past (already expired).
                threshold_date = datetime.now() + timedelta(days=30)
                
                if exp_date_obj > threshold_date:
                    print(f"Skipping {name}: Contract expires later ({exp_date_obj.date()})")
                    continue
                    
            except Exception as e:
                print(f"Warning parsing date for {name} ({date_exp}): {e}. Skipping to avoid spam.")
                print(f"Skipping {name} due to invalid date: {date_exp}")
                failed_items.append(f"{name} (Invalid Date: {date_exp})")
                continue
            
            print(f"Sending to {name} ({phone}) - Exp: {exp_date_obj.date()}...")
            success, error_msg = send_template_message(phone, name, date_exp, contract, description)
            
            if success:
                sent_names.append(str(name))
            else:
                # Add to failures: "Name (Reason)"
                short_error = error_msg if error_msg else "Unknown"
                if "131048" in short_error:
                    short_error = "Spam/Limit"
                elif "131030" in short_error:
                    short_error = "Not Allowed"
                    
                failed_items.append(f"{name} ({short_error})")
            
            time.sleep(1) # Rate limit protection

        # Notify Admin about SUCCESS
        if sent_names:
            send_admin_notification(sent_names)
        else:
            print("No messages sent.")

        # Notify Admin about FAILURES
        if failed_items:
            send_error_notification(failed_items)

    except Exception as e:
        print(f"Error fetching/processing data: {e}")
    
    print(f"[{datetime.now()}] Job finished.")

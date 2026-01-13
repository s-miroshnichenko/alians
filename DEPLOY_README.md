# Deployment Instructions

To run this script on a server (VPS, AWS, DigitalOcean, etc.), follow these steps:

## 1. Prepare Files
Upload the following files to your server (e.g., using `scp` or FileZilla):
- `daily_contract_notifier.py` (The main script)
- `requirements.txt` (Dependencies)

## 2. Setup Environment (On Server)
SSH into your server and run:

```bash
# Update package list
sudo apt update

# Install Python3 and pip and venv if validation fails
sudo apt install python3 python3-pip python3-venv

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 3. Configure Background Execution based on OS
You want the script to run forever, even if you disconnect.

### Option A: Using `nohup` (Simple)
```bash
nohup python3 daily_contract_notifier.py > output.log 2>&1 &
```
*To stop it later:* `pkill -f daily_contract_notifier.py`

### Option B: Using `systemd` (Recommended for Auto-Restart)
1. Create a service file:
   `sudo nano /etc/systemd/system/whatsapp_bot.service`

2. Paste this content (adjust paths!):
   ```ini
   [Unit]
   Description=WhatsApp Daily Sender
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/root/whatsapp_bot
   ExecStart=/root/whatsapp_bot/venv/bin/python3 /root/whatsapp_bot/daily_contract_notifier.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable whatsapp_bot
   sudo systemctl start whatsapp_bot
   ```

## 4. Verification
The script will print logs to `output.log` (if using nohup) or `journalctl -u whatsapp_bot` (if using systemd).
It is scheduled to run at **09:00 AM** local time of the server. Check `date` on the server to ensure timezone matches your expectations!

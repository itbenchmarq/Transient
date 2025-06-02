#Gathers public IP from AWS instance and updates Cloudflare DNS record
#Variables to update include Credentials & section under Update Cloudflre DNS Record
import requests
import json
import time


# Cloudflare credentials
CF_EMAIL = "test@itbenchmarq.com"  # Replace with your Cloudflare email
CF_API_TOKEN = "XXX"  # Replace with your Cloudflare API key
CF_ZONE_ID = "XXX"  # Replace with your Cloudflare Zone ID
CF_RECORD_ID = "XXX"  # Replace with your Cloudflare Record ID (A record)


# Get EC2 instance's public IP
def get_aws_metadata_token():
    try:
        token_url = "http://169.254.169.254/latest/api/token"
        headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        response = requests.put(token_url, headers=headers, timeout=2)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to get metadata token: {e}")
        return None

def get_public_ip(token,metadata_path="public-ipv4"):
    try:
        metadata_url = f"http://169.254.169.254/latest/meta-data/{metadata_path}"
        headers = {"X-aws-ec2-metadata-token": token}
        response = requests.get(metadata_url, headers=headers, timeout=2)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None

# Update Cloudflare DNS record
def update_cloudflare_dns(new_ip):
    url =f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/dns_records/{CF_RECORD_ID}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": "test.itbenchmarq.com",  # Replace with your domain name
        "content": new_ip,
        "ttl": 300,
        "proxied": True  # Or False, depending on your needs
    }
    try:
        response = requests.put(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print("Cloudflare DNS record updated successfully!")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error updating Cloudflare DNS record: {e}")
        print(response.text)
        return False


# Main function
def main():
    token = get_aws_metadata_token()

    new_ip = get_public_ip(token,"public-ipv4")
    if new_ip:
        print(f"Public IP: {new_ip}")
        if update_cloudflare_dns(new_ip):
            print(f"Updated Cloudflare DNS record with {new_ip}")
        else:
            print("Failed to update Cloudflare DNS record.")
    else:
        print("Failed to get public IP.")

# Run the script
if __name__ == "__main__":
    while True:
        main()
        time.sleep(900)  # Check IP every 15 minutes (adjust as needed)

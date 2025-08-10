# cf_ddns_multi.py

Dynamic DNS updater for multiple A/AAAA records on Cloudflare, designed to run inside Docker.

The script periodically checks the current public IP address and updates the configured Cloudflare DNS records (root domain, `www`, `images`, etc.) only when a change is detected.  
It supports both IPv4 and IPv6 and minimizes unnecessary API calls, following best practices from the official [cloudflare-python](https://github.com/cloudflare/python-cloudflare) SDK.

---

## Features

- Updates **multiple DNS records** in one run (root domain and subdomains).
- **IPv4 and IPv6** detection and updating.
- **Avoids unnecessary updates** if the IP hasn’t changed.
- **Optional** creation of missing DNS records (disabled by default for Docker use).
- Ping check for your local router before attempting an update.

---

## Requirements

The only requirement is **Docker**.

---

## Environment Variables

| Variable           | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `DOMAIN_NAME`      | Base domain name (e.g., `example.com`).                                     |
| `ROUTER_IP`        | Local router IP address to ping before updates (e.g., `192.168.1.1`).       |
| `CF_API_TOKEN`     | Cloudflare API Token (recommended).                                         |
| `CF_API_KEY`       | Cloudflare API Key (if not using a token).                                  |
| `CF_API_EMAIL`     | Email associated with your Cloudflare account (if using API Key).           |
| `CF_RECORDS`       | Comma-separated list of full record names to manage.<br>Example: `example.com,www.example.com,images.example.com`. If omitted, the script will default to `DOMAIN_NAME`, `www.DOMAIN_NAME`, and `images.DOMAIN_NAME`. |
| `CF_ALLOW_CREATE`  | `true` or `false`. When `true`, the script will attempt to create missing DNS records if API permissions allow it. Default: `false` (recommended for Docker). |

> **Note:**  
> The API token must have **Zone:Read** and **DNS:Edit** permissions for the target zone.

---

## Docker Usage

### 1. Create an environment file (`.env`)

Example:

CF_API_EMAIL='example@gmail.com'
CF_API_KEY='example_api_key'
CF_ZONE_ID='example_zone_id'
CF_RECORDS=example.com,www.example.com,images.example.com


ROUTER_IP   ='192.168.1.1'
DOMAIN_NAME ='example.com'

### 2. Build and execute the image

`docker compose build && docker compose up -d`
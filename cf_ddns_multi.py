import CloudFlare
import requests
import time
import logging
import ping3
import os
from CloudFlare.exceptions import CloudFlareAPIError
from requests.exceptions import RequestException

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CHECK_INTERVAL = 60  # seconds


def read_env_or_fail(env_name: str) -> str:
    value = os.environ.get(env_name)
    if not value:
        logger.critical(f"Environment variable {env_name} is not set")
        raise SystemExit(1)
    return value


def get_current_ip() -> str | None:
    try:
        response = requests.get("https://ifconfig.me/ip", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except RequestException as e:
        logger.error(f"Error fetching current IP: {e}")
        return None


def update_cloudflare_records(current_ip: str, cf_data: dict, record_names: list[str]):
    if not current_ip:
        return

    try:
        cf = CloudFlare.CloudFlare(email=cf_data["email"], key=cf_data["api_key"])

        for name in record_names:
            records = cf.zones.dns_records.get(cf_data["zone_id"], params={"name": name, "type": "A"})
            if not records:
                logger.warning(f"No DNS record found for {name}")
                continue

            record = records[0]
            if record["content"] != current_ip:
                logger.info(f"Updating {name} from {record['content']} to {current_ip}")
                cf.zones.dns_records.put(
                    cf_data["zone_id"],
                    record["id"],
                    data={
                        "type": record["type"],
                        "name": record["name"],
                        "content": current_ip,
                        "ttl": record["ttl"],
                        "proxied": record.get("proxied", False),
                    }
                )
                logger.info(f"Updated {name} successfully")
            else:
                logger.info(f"{name} already up-to-date")

    except CloudFlareAPIError as e:
        logger.error(f"CloudFlare API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def main():
    logger.info("Starting Cloudflare Dynamic DNS Updater")

    router_ip = read_env_or_fail("ROUTER_IP")
    cf_data = {
        "email": read_env_or_fail("CF_API_EMAIL"),
        "api_key": read_env_or_fail("CF_API_KEY"),
        "zone_id": read_env_or_fail("CF_ZONE_ID"),
    }

    cf_records_env = os.environ.get("CF_RECORDS")
    if cf_records_env:
        record_names = [r.strip() for r in cf_records_env.split(",") if r.strip()]
    else:
        domain_name = read_env_or_fail("DOMAIN_NAME")
        record_names = [
            domain_name,
            f"www.{domain_name}",
            f"images.{domain_name}",
        ]


    last_ip = None

    try:
        while True:
            latency = ping3.ping(router_ip, timeout=1, unit="ms")
            if latency is None:
                logger.warning(f"Router {router_ip} is unreachable")
            else:
                logger.info(f"Router {router_ip} is UP - {latency:.2f} ms")
                current_ip = get_current_ip()

                if current_ip and current_ip != last_ip:
                    update_cloudflare_records(current_ip, cf_data, record_names)
                    last_ip = current_ip
                else:
                    logger.info("Public IP has not changed")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Shutting down updater")


if __name__ == "__main__":
    main()

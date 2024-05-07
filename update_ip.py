import CloudFlare
import requests
import time
import logging
import ping3
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_env(env_name):
    env_value = os.environ.get(env_name)
    if not env_value:
        logger.error(f'{env_name} undefined: {env_value}')
        return None
    else:
        return str(env_value)

def get_current_ip():
    try:
        response = requests.get("https://ifconfig.me/ip")
        current_ip = response.text
        logger.info(f'The current IP is: {current_ip}')
        return current_ip
    except:
        logger.error(f'Error reaching ifconfig. Is internet connection down?')
        return None

def update_cloudflare_dns(current_ip, cf_data):
    cf = CloudFlare.CloudFlare(email=cf_data["email"], key=cf_data["api_key"])

    if not current_ip:
        logger.error(f'Current IP is missing {current_ip}')   
        return

    try:
        dns_records = cf.zones.dns_records.get(cf_data["zone_id"])
        if not dns_records:
            logger.warning('DNS records not found')            

        for domain_name in dns_records:
            if domain_name['zone_name'] == cf_data["dns_record_name"] and domain_name['content'] != current_ip:
                dns_record_id = domain_name
                dns_record_id['content'] = current_ip
                cf.zones.dns_records.put(cf_data["zone_id"], dns_record_id['id'], data=dns_record_id)
                logger.info(f'DNS record: {dns_record_id["id"]} updated to: {current_ip}')

            elif domain_name['zone_name'] != cf_data["dns_record_name"]:
                logger.warning('DNS_RECORD_NAME does not match')
            else:
                logger.info('The IP address is already updated')
    except:
        logger.error(f'Error updating DNS record. Is internet connection down?')


def main():
    logger.info(f'The pogram has started')

    router_ip = read_env('ROUTER_IP')
    cf_data = {
        'email' : read_env('CF_API_EMAIL'),
        'api_key' : read_env('CF_API_KEY'),
        'zone_id' : read_env('CF_ZONE_ID'),
        'dns_record_name' : read_env('DNS_RECORD_NAME'),
    }
    logger.info(f"cf_data: {cf_data}")

    while True:
        result = ping3.ping(router_ip, timeout=1, unit='ms')  
        if not result:
            logger.error(f'{router_ip} is down')
        else:
            logger.info(f'{router_ip} is UP - ping result: {round(result, 2)} ms')
            current_ip = get_current_ip()
            update_cloudflare_dns(current_ip, cf_data)
        time.sleep(60)


main()

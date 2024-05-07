import CloudFlare
import requests
import time
import logging
import ping3
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cloudflare API credentials
CF_API_EMAIL = os.environ.get('CF_API_EMAIL')
CF_API_KEY   = os.environ.get('CF_API_KEY')
CF_ZONE_ID   = os.environ.get('CF_ZONE_ID')
ROUTER_IP    = os.environ.get('ROUTER_IP')
DNS_RECORD_NAME = os.environ.get('DNS_RECORD_NAME')

def get_current_ip():
    try:
        response = requests.get("https://ifconfig.me/ip")
        current_ip = response.text
        logger.info(f'The current IP is: {current_ip}')
        return current_ip
    except:
        logger.error(f'Error reaching ifconfig. Is internet connection down?')
        return None

def update_cloudflare_dns(current_ip):
    cf = CloudFlare.CloudFlare(email=CF_API_EMAIL, token=CF_API_KEY)

    try:
        if not current_ip:
            logger.error(f'Current IP is missing {current_ip}')   
            return
        
        dns_record = cf.zones.dns_records.get(CF_ZONE_ID)
        if not dns_record:
            logger.warning('DNS records not found')            

        logger.info(f'dns_record: {dns_record}')
        for single_record in dns_record:
            if single_record['zone_name'] == DNS_RECORD_NAME and single_record['content'] != current_ip:
                dns_record_id = single_record
                dns_record_id['content'] = current_ip
                cf.zones.dns_records.put(CF_ZONE_ID, dns_record_id['id'], data=dns_record_id)
                logger.info(f'DNS record: {dns_record_id["id"]} updated to: {current_ip}')

            elif single_record['zone_name'] != DNS_RECORD_NAME:
                logger.warning('DNS_RECORD_NAME does not match')
            else:
                logger.info('The IP address is already updated')

    except:
        logger.error(f'Error updating DNS record. Is internet connection down?')

def main():
    logger.info(f'The pogram has started')

    if not CF_API_EMAIL:
        logger.error(f'CF_API_EMAIL undefined: {CF_API_EMAIL}')
        return
    if not CF_API_KEY:
        logger.error(f'CF_API_KEY undefined: {CF_API_KEY}')
        return
    if not CF_ZONE_ID:
        logger.error(f'CF_ZONE_ID undefined: {CF_ZONE_ID}')
        return
    if not ROUTER_IP:
        logger.error(f'ROUTER_IP undefined: {ROUTER_IP}')
        return
    if not DNS_RECORD_NAME:
        logger.error(f'DNS_RECORD_NAME undefined: {DNS_RECORD_NAME}')
        return

    CF_API_EMAIL    = str(CF_API_EMAIL)
    CF_API_KEY      = str(CF_API_KEY)
    CF_ZONE_ID      = str(CF_ZONE_ID)
    ROUTER_IP       = str(ROUTER_IP)
    DNS_RECORD_NAME = str(DNS_RECORD_NAME)

    logger.info(f"CF_API_EMAIL: {CF_API_EMAIL} - CF_API_KEY: {CF_API_KEY} - CF_ZONE_ID: {CF_ZONE_ID} - ROUTER_IP: {ROUTER_IP} - DNS_RECORD_NAME: {DNS_RECORD_NAME}")
    while True:
        result = ping3.ping(ROUTER_IP, timeout=1, unit='ms')  
        if not result:
            logger.error(f'{ROUTER_IP} is down')
        else:
            logger.info(f'{ROUTER_IP} is UP - ping result: {round(result, 2)} ms')
            current_ip = get_current_ip()
            update_cloudflare_dns(current_ip)
        time.sleep(60)


main()

import json
import pingparsing
import concurrent.futures
import speedtest
import platform
import hashlib
import getmac
import logging
import sys
import datetime
import requests


# Server
server_url = 'http://ispmon.cloud'

# Logging parameters
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)


# Global PING objects and parameters
ping_parser = pingparsing.PingParsing()
transmitter = pingparsing.PingTransmitter()
ping_hosts = ["google.com", "youtube.com", "facebook.com", "whatsapp.com", "tiktok.com"]
ping_duration = 60  # sec
ping_option = "-i 1"  # Additional PING option command


# SpeedTest Parameters
speedtest_interval = 30  # Minutes

# Following the above parameters, the program will run ping for 'ping_duration' before sending results.
# Sppedtest check will run every 'speedtest_interval', right after ping test ends.


def ping_check(host):
    transmitter.destination = host
    transmitter.deadline = ping_duration
    transmitter.ping_option = ping_option
    result = transmitter.ping()
    ping.append(json.dumps(ping_parser.parse(result).as_dict(), indent=4))


def run_speedtest():
    s = speedtest.Speedtest()
    s.get_best_server()
    s.upload(pre_allocate=False)
    s.download(threads=5)
    s.upload(threads=5)

    result = s.results.dict()

    return result


def push_results(u_id, ping_results, speed_results):
    results = {'unique_id': u_id, 'country': country, 'isp': ISP}
    print(ping_results)
    results['ping'] = {}
    results['speed'] = {}
    results['speed']['available'] = False
    for host in ping_results:
        host = json.loads(host)
        results['ping'][host["destination"]] = host
    if speed_results is not None:
        results['speed']['available'] = True
        results['speed']['results'] = speed_results
    try:
        status = requests.post(server_url+"/metrics", json=results)
        print(status.status_code)
    except Exception as push_error:
        log.error("PUSH results error: ", push_error)
        print(push_error)

if __name__ == "__main__":
    
    # Calculate Hash based on hostname and MAC address
    sha = hashlib.sha1()
    sha.update(platform.node().encode('utf-8'))
    sha.update(getmac.get_mac_address().encode('utf-8'))
    unique_id = str(sha.hexdigest()[:10])
    log.info("Connect to https://ispmon.cloud to see your results. Yours UNIQUE ID: " + unique_id)

    # Get current time
    time_now = datetime.datetime.now()

    # Get Client Country
    try:
        req = requests.get('https://ipinfo.io')
        country = req.json()['country']
        ISP = req.json()['org']
    except Exception as ipinfo_error:
        log.error("Error while getting client info from IPINFO: ", ipinfo_error)
        country = "NONE"
        ISP = "NONE"

    # Main Loop
    while True:

        # run ping check
        ping = list()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(ping_check, ping_hosts)
        except Exception as ping_error:
            log.error("PING check execution fail: ", ping_error)
            pass

        if datetime.datetime.now() >= time_now + datetime.timedelta(minutes=speedtest_interval):
            try:
                speed = run_speedtest()
            except Exception as speed_error:
                log.error("SPEED check execution fail: ", speed_error)
                pass
            try:
                push_results(unique_id, ping, speed)
                time_now = datetime.datetime.now()
            except Exception as push_error:
                log.error("PUSH results execution fail: ", push_error)
                pass
        else:
            try:
                push_results(unique_id, ping, None)
            except Exception as push_error:
                log.error("PUSH results execution fail: ", push_error)
                pass


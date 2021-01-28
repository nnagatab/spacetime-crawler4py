import requests
import cbor
import time

from utils.response import Response

def download(url, config, logger=None):
    host, port = config.cache_server
    resp = requests.get(
        f"http://{host}:{port}/",
        params=[("q", f"{url}"), ("u", f"{config.user_agent}")], timeout = 3)
    if resp and resp.content:  #added to make sure page has content
        return Response(cbor.loads(resp.content))
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})

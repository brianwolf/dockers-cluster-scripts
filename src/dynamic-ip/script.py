import logging
import subprocess
import sys

import requests

# ================================================
# VARS
# ================================================

DNS_ENDPOINT = (
    "https://administracion.donweb.com/apiv3/servicios/zonaDNS/editarRegistro"
)

WHICH_IS_MY_IP_ENDPOINT = "https://ipinfo.io/ip"

# ================================================
# CONFIGS
# ================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s (%(process)d) - %(levelname)s - %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)

# ================================================
# METHODS
# ================================================


def sh(cmd: str, echo: bool = False) -> str:

    if echo:
        logging.info(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    return p.stdout.read().decode()  # type: ignore


# ================================================
# SCRIPT
# ================================================

public_ip = sh(f"curl {WHICH_IS_MY_IP_ENDPOINT}")

response = requests.post(
    url=DNS_ENDPOINT,
    params={
        "servicioID": "4047439",
        "tipo": "A",
        "nombre": "lobezzzno.com.ar",
        "contenido": public_ip,
        "ttl": "14400",
        "prioridad": "0",
        "registroID": "146337447",
    },
)

logging.info(f"Response -> {response.status_code} | {response.json()}")

from dotenv import load_dotenv
from piazza_api import Piazza
from pprint import pprint
import os
import json

def load_config():
    load_dotenv()
    email = os.getenv("PIAZZA_EMAIL")
    password = os.getenv("PIAZZA_PASSWORD")
    network_id = os.getenv("PIAZZA_NETWORK_ID_CPSC310_2025W2")
    return (email, password, network_id)

if __name__ == "__main__":
    email, password, network_id = load_config()

    p = Piazza()
    p.user_login(email, password)
    network = p.network(network_id)

    post = network.get_post(6)
    with open("sample.json", "w") as f:
        json.dump(post, f, indent=2)

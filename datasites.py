import syft as sy

from datasets import load_data, generate_mock
from datasets import NAMES, MNIST_PART_1, MNIST_PART_2

from threading import current_thread
from time import sleep
from typing import Optional


DATASITE_PORTS = {name: (54879 + i) for i, name in enumerate(NAMES)}
DATASITE_URLS = {
    name: f"http://localhost:{port}" for name, port in DATASITE_PORTS.items()
}

INSTITUTE_FULLNAMES = {
    MNIST_PART_1: "MNIST Split 1 (images 0–29999, aléatoires)",
    MNIST_PART_2: "MNIST Split 2 (images 30000–59999, aléatoires)",
}

def create_syft_dataset(name: str) -> Optional[sy.Dataset]:
    data = load_data(name=name)          # -> (X, y)
    if data is None:
        return None

    full_name = INSTITUTE_FULLNAMES[name]

    dataset = sy.Dataset(
        name="MNIST Dataset",
        summary=f"MNIST split hosted at {full_name}",
        description=f"""
## MNIST Dataset

**Split**: {full_name}
- Images: 28x28 niveaux de gris
- Nombre d'exemples dans ce split: {len(data[0])}
- Labels: 10 classes (0–9)
""",
    )  # type: ignore

    dataset.add_asset(
        sy.Asset(
            name="MNIST Data",
            data=data,                          # (X, y) : tuple de tensors
            mock=generate_mock(data=data, seed=len(name)),
        )
    )
    return dataset


def _get_welcome_message(name: str, full_name: str) -> str:
    return f"""
<img src="data:image/png;base64,..."
     alt="Logo" style="width:48px;height:48px;padding:3px;">

## Welcome to the {name} Datasite

**Split**: {full_name}

**Deployment Type**: Local
"""


def spawn_server(sid: int):
    name = NAMES[sid % len(NAMES)]

    data_site = sy.orchestra.launch(
        name=name,
        port=DATASITE_PORTS[name],
        reset=True,
        n_consumers=3,
        create_producer=True,
    )
    client = data_site.login(email="info@openmined.org", password="changethis")

    client.settings.allow_guest_signup(True)
    client.settings.welcome_customize(
        markdown=_get_welcome_message(name=name, full_name=INSTITUTE_FULLNAMES[name])
    )
    client.users.create(
        email="researcher@openmined.org",
        password="****",
        password_verify="****",
        name="OpenMined Researcher",
        institution="OpenMined",
        website="https://openmined.org",
    )
    ds = create_syft_dataset(name)
    if ds is not None:
        client.upload_dataset(ds)

    print(f"Datasite {name} is up and running: {data_site.url}:{data_site.port}")
    return data_site, client


def check_and_approve_incoming_requests(client, thread=None):
    """Automatically approve all incoming requests."""
    while True:
        # If thread is passed, check if it should stop
        if thread is not None and thread.stopped():
            break
        try:
            requests = client.requests
            for r in filter(lambda r: r.status.value != 2, requests):
                r.approve(approve_nested=True)
        except Exception as e:
            print(f"Error approving requests: {e}")
        sleep(1)
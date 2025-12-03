#!/usr/bin/env python
# coding: utf-8

from threading import Thread, Event
from time import sleep
from datasites import spawn_server, check_and_approve_incoming_requests
from datasites import DATASITE_URLS


class DataSiteThread(Thread):
    """
    Thread class with a stop() method.
    The thread itself has to check regularly for the stopped() condition.
    """

    def __init__(self, *args, **kwargs):
        super(DataSiteThread, self).__init__(*args, **kwargs)
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def show_connections_info():
    print(f"{'='*65}")
    print(
        f"\n\t{len(DATASITE_URLS)} DataSite{'s' if len(DATASITE_URLS) > 1 else ''} Up and Running.",
        end="\n\n",
    )
    for dsid, (name, url) in enumerate(DATASITE_URLS.items()):
        print(f"{dsid+1}. {name}: {url}")
    print(f"{'='*65}")


def launch_datasites(show_conn_info: bool = True) -> None:
    data_sites = []
    client_threads = []

    # IMPORTANT: lancer exactement un serveur par entrée dans DATASITE_URLS
    for sid in range(len(DATASITE_URLS)):
        data_site, client = spawn_server(sid=sid)
        data_sites.append(data_site)
        thread = DataSiteThread(
            target=check_and_approve_incoming_requests,
            args=(client, None),  # Will be set to thread after creation
            daemon=True,
        )
        client_threads.append(thread)
        # Update the thread argument to pass the thread itself
        thread.args = (client, thread)

    for t in client_threads:
        t.start()

    if show_conn_info:
        show_connections_info()

    try:
        while True:
            sleep(2)
    except KeyboardInterrupt:
        for data_site in data_sites:
            data_site.land()
        for t in client_threads:
            t.stop()


def launch_from_notebook() -> None:
    t = Thread(target=launch_datasites, kwargs={"show_conn_info": True}, daemon=True)
    t.start()


if __name__ == "__main__":
    launch_datasites()

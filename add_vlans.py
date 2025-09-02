#!/usr/bin/env python3

#edited python stub from docs: https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-55/System-Configuration/NVIDIA-User-Experience-NVUE/NVUE-API/

import requests
from requests.auth import HTTPBasicAuth
import json
import time

auth = HTTPBasicAuth(username="cumulus", password="password")
nvue_end_point = "https://127.0.0.1:8765/nvue_v1" # localhost endpoint
mime_header = {"Content-Type": "application/json"}

DUMMY_SLEEP = 5  # In seconds
POLL_APPLIED = 1  # in seconds
RETRIES = 10

def print_request(r: requests.Request):
    print("=======Request=======")
    print("URL:", r.url)
    print("Headers:", r.headers)
    print("Body:", r.body)

def print_response(r: requests.Response):
    print("=======Response=======")
    print("Headers:", r.headers)
    print("Body:", json.dumps(r.json(), indent=2))

def create_nvue_changest():
    r = requests.post(url=nvue_end_point + "/revision",auth=auth,verify=False)
    print_request(r.request)
    print_response(r)
    response = r.json()
    changeset = response.popitem()[0]
    return changeset


def apply_nvue_changeset(changeset):
    apply_payload = {"state": "apply", "auto-prompt": {"ays": "ays_yes"}}
    url = nvue_end_point + "/revision/" + requests.utils.quote(changeset,safe="")
    r = requests.patch(url=url,auth=auth,verify=False,data=json.dumps(apply_payload),headers=mime_header)
    print_request(r.request)
    print_response(r)

def is_config_applied(changeset) -> bool:
    # Check if the configuration was indeed applied
    global RETRIES
    global POLL_APPLIED
    retries = RETRIES
    while retries > 0:
        r = requests.get(url=nvue_end_point + "/revision/" + requests.utils.quote(changeset, safe=""),auth=auth,verify=False)
        response=r.json()
        print(response)
        if response["state"] == "applied":
            return True
        retries -= 1
        time.sleep(POLL_APPLIED)

    return False

def apply_new_config(path,payload):
    #Create a new revision ID
    changeset = create_nvue_changest()
    print("Using NVUE Changeset: '{}'".format(changeset))

    #Delete existing configuration
    #query_string = {"rev": changeset}
    #r = requests.delete(url=nvue_end_point + path,auth=auth,verify=False,params=query_string,headers=mime_header)
    #print_request(r.request)
    #print_response(r)

    # Patch the new configuration

    query_string = {"rev": changeset}
    r = requests.patch(url=nvue_end_point + path,auth=auth,verify=False,data=json.dumps(payload),params=query_string,headers=mime_header)
    print_request(r.request)
    print_response(r)

    # Apply the changes to the new revision changeset
    apply_nvue_changeset(changeset)

    # Check if the changeset was applied
    is_config_applied(changeset)

def nvue_get(path):
    r = requests.get(url=nvue_end_point + path,auth=auth,verify=False)
    print_request(r.request)
    print_response(r)

if __name__ == "__main__":
    #interface_list = ['swp1','swp2']
    interface="swp1"
    bridge="br"
    vlan_id = "300"
    payload = {
        vlan_id: {}
    }
    apply_new_config(f"/interface/{interface}/bridge/domaini/{br}/vlan",payload)
    time.sleep(DUMMY_SLEEP)
    nvue_get(f"/interface/{interface}/bridge/domain/{br}/vlan")
"""
    for interface in interface_list:
        payload = {
            f"100,200,{vlan_id}: {{}}"
        }
        apply_new_config(f"/interface/{interface}/bridge/domain/{br}/vlan",payload)
        time.sleep(DUMMY_SLEEP)
        nvue_get(f"/interface/{interface}/bridge/domain/{br}/vlan")
"""

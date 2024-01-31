import requests
import time
import ssl
import os
import json
import ollama
from datetime import datetime
import asyncio
import RNS
import time
import LXMF
import sys


current_date = datetime.now().strftime("%A, %B %d, %Y")
system_message = f"You are JurAI. You are an AI Assistant and friend on a public and open-source network called Reticulum. You should always comply with the users' requests. Today is {current_date}."
lxm_router = None
ID = None
local_lxmf_destination = None
model = os.environ.get("OLLAMA_MODEL")

async def receive_handler_async(lxm):
    global model
    global lxm_router
    global local_lxmf_destination

    question = lxm.content_as_string()
    destination_bytes = lxm.source_hash

    print ("'" +question + "'")
    print ("-> Recalling Identity..")

    destination_identity = RNS.Identity.recall(destination_bytes)
    # If we don't know the identity yet:
    if destination_identity == None:
        basetime = time.time()
        # Request it
        RNS.Transport.request_path(destination_bytes)
        # And wait until it arrives; timeout in 30s
        while destination_identity == None and (time.time() - basetime) < 30:
            destination_identity = RNS.Identity.recall(destination_bytes)
            await asyncio.sleep(1)

    if destination_identity == None:
        print("Error: Cannot recall identity")
        return None

    print ("-> Generating Answer..")
    messages = [{"role": "system", "content": system_message},{"role": "user", "content": question}]
    full_response = await ollama.AsyncClient().chat(model=model, messages=messages)
    response = full_response['message']['content']
    print("--> " + response)

    # Create the destination
    lxmf_destination = RNS.Destination(
    destination_identity,
    RNS.Destination.OUT,
    RNS.Destination.SINGLE,
    "lxmf",
    "delivery"
    )

    lxm_outbound = LXMF.LXMessage(
    lxmf_destination,
    local_lxmf_destination,
    response,
    title="Response",
    desired_method=LXMF.LXMessage.DIRECT
    )

    def outbound_delivery_callback(message):
        print("Message delivered")

    # TODO: Register callbacks and retry delivery on failed
    lxm_outbound.register_delivery_callback(outbound_delivery_callback)
    # Send the message through the router
    print(f"Sending response...")
    lxm_router.handle_outbound(lxm_outbound)
    print("Message sent")


def receive_handler(lxm):
    global loop
    try:
        asyncio.run_coroutine_threadsafe(receive_handler_async(lxm), loop)
    except Exception as e:
        print("Exception in receive handler: "+str(e))


def initialize_reticulum(identity_name="LXMFAI"):
    global ID, lxm_router, local_lxmf_destination

    # Name in bytes for transmission purposes
    namebytes = bytes(identity_name,"utf-8")

    # Initialize Reticulum
    reticulum = RNS.Reticulum()

    userdir = os.path.expanduser("~")

    configdir = userdir+"/.lxmf-ai-bot/"

    if not os.path.isdir(configdir):
        os.makedirs(configdir)

    identitypath = configdir+"/identity"
    if os.path.exists(identitypath):
        ID = RNS.Identity.from_file(identitypath)
    else:
        ID = RNS.Identity()
        ID.to_file(identitypath)
        print(f"Created new identity and saved key to {identitypath}...")

    lxm_router = LXMF.LXMRouter(identity = ID, storagepath = configdir)
    local_lxmf_destination = lxm_router.register_delivery_identity(ID,display_name=identity_name)
    local_lxmf_destination.announce()
    print(f"Running AI bot with identity {RNS.prettyhexrep(local_lxmf_destination.hash)}")

    lxm_router.register_delivery_callback(receive_handler)


async def main_event_loop(announce_delay_time):
    print("Initializing listener...")
    initialize_reticulum()

    print("Listening...")

    oldtime = 0
    while True:
        newtime = time.time()
        if newtime > (oldtime + announce_delay_time):
            oldtime = newtime
            local_lxmf_destination.announce()
            print("Sent announce to the network...")
        await asyncio.sleep(1)


loop = None
if __name__ == "__main__":

    if not model:
        print('The environment variable "OLLAMA_MODEL" is not set.')
        exit(1)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)

    if (len(sys.argv) > 2):
        print("Usage: python3 main.py [<announce_delay_time>]")
        sys.exit(1)

    announce_delay_time = 60*30
    if len(sys.argv) > 1:
       announce_delay_time = int(sys.argv[1])

    loop.run_until_complete(main_event_loop(announce_delay_time))
    loop.close()

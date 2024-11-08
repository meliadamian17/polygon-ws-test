import asyncio
import websockets
import json
from datetime import datetime
import random


connected_clients = {}


async def send_data_to_client(websocket):

    while True:

        await asyncio.sleep(1)

        trade_data = {
            "ev": "T",
            "sym": "MSFT",
            "x": 4,
            "i": str(random.randint(10000, 99999)),
            "z": 3,
            "p": round(random.uniform(100, 200), 2),
            "s": random.randint(1, 100),
            "c": [0, 12],
            "t": int(datetime.now().timestamp() * 1000),
            "q": random.randint(1000, 2000)
        }

        quote_data = {
            "ev": "Q",
            "sym": "AAPL",
            "bx": 4,
            "bp": round(random.uniform(150, 200), 2),
            "bs": random.randint(1, 10),
            "ax": 7,
            "ap": round(random.uniform(150, 200), 2),
            "as": random.randint(1, 10),
            "c": 0,
            "i": [604],
            "t": int(datetime.now().timestamp() * 1000),
            "q": random.randint(50000, 60000),
            "z": 3
        }

        aggregate_data = {
            "ev": "AM",
            "sym": "GOOG",
            "v": random.randint(1000, 5000),
            "av": random.randint(500000, 1000000),
            "op": round(random.uniform(2000, 2500), 2),
            "vw": round(random.uniform(2000, 2500), 2),
            "o": round(random.uniform(2000, 2500), 2),
            "c": round(random.uniform(2000, 2500), 2),
            "h": round(random.uniform(2000, 2500), 2),
            "l": round(random.uniform(2000, 2500), 2),
            "a": round(random.uniform(2000, 2500), 2),
            "z": random.randint(500, 1000),
            "s": int(datetime.now().timestamp() * 1000),
            "e": int(datetime.now().timestamp() * 1000) + 60000
        }

        if websocket in connected_clients:
            channels = connected_clients[websocket]
            if "T.MSFT" in channels:
                await websocket.send(json.dumps(trade_data))
            if "Q.AAPL" in channels:
                await websocket.send(json.dumps(quote_data))
            if "AM.GOOG" in channels:
                await websocket.send(json.dumps(aggregate_data))


async def handler(websocket, path):
    connected_clients[websocket] = []

    await websocket.send(json.dumps([{"ev": "status", "status": "connected", "message": "Connected Successfully"}]))

    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "auth":

                if data.get("params") == "valid_api_key":
                    await websocket.send(json.dumps([{"ev": "status", "status": "auth_success", "message": "authenticated"}]))
                else:
                    await websocket.send(json.dumps([{"ev": "status", "status": "auth_failed", "message": "invalid API key"}]))

            elif action == "subscribe":

                params = data.get("params", "").split(",")
                connected_clients[websocket].extend(params)
                await websocket.send(json.dumps([{"ev": "status", "status": "subscribed", "channels": params}]))

                asyncio.create_task(send_data_to_client(websocket))

    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected")

    finally:

        if websocket in connected_clients:
            del connected_clients[websocket]


async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

asyncio.run(main())

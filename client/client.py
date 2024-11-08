import asyncio
import websockets
import json


async def test_client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:

        await websocket.send(json.dumps({"action": "connect"}))
        connection_response = await websocket.recv()
        print(f"Connection Response: {connection_response}")

        await websocket.send(json.dumps({"action": "auth", "params": "valid_api_key"}))
        auth_response = await websocket.recv()
        print(f"Auth Response: {auth_response}")

        await websocket.send(json.dumps({"action": "subscribe", "params": "T.MSFT,Q.AAPL,AM.GOOG"}))
        print("Subscribed to T.MSFT, Q.AAPL, and AM.GOOG")

        for _ in range(5):
            response = await websocket.recv()
            print(f"Received: {response}")
            await asyncio.sleep(1)

        print("Closing connection...")
        await websocket.close()


asyncio.get_event_loop().run_until_complete(test_client())

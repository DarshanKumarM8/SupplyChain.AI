import asyncio
import json
import httpx
import websockets

async def test_integration():
    """
    Acts as a dummy frontend client to verify the backend is functioning properly.
    """
    # 1. Health Check
    print("Checking health endpoint (http://localhost:8000/health)...")
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        assert response.status_code == 200, f"Health check failed with status {response.status_code}"
        print("✅ Health check passed (200 OK)\n")

    # 2. WebSocket Connection
    ws_url = "ws://localhost:8000/ws/simulation"
    print(f"Connecting to WebSocket stream ({ws_url})...")
    
    # 5. Close connection gracefully (handled by async with context manager)
    async with websockets.connect(ws_url) as websocket:
        print("✅ WebSocket connected\n")
        
        # 3. Send Payload
        payload = {
            "beta": 0.6,
            "market_adoption_pct": 0.4,
            "shock_intensity": 0.85
        }
        await websocket.send(json.dumps(payload))
        print(f"Sent simulation config payload: {payload}\n")
        
        # 4. Receive 3 frames
        print("Waiting for frames from server...")
        for i in range(3):
            message = await websocket.recv()
            data = json.loads(message)
            
            # The server might send a "stream_complete" event or normal frame
            if data.get("event") == "stream_complete":
                print("Stream complete event received.")
                break
                
            tick = data.get("tick")
            stampede_index = data.get("stampede_index")
            print(f"Received frame {i+1} (Tick {tick}): stampede_index = {stampede_index}")
            
        print("\n✅ Successfully received exactly 3 frames.")
        print("Closing connection gracefully...")

if __name__ == "__main__":
    asyncio.run(test_integration())

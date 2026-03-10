"""WebSocket routes for QA-FRAMEWORK Dashboard."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict

from websocket.manager import manager
from services.auth_service import verify_token
from models.user import User
from database import get_db

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications."""
    await websocket.accept()

    user_id = None

    try:
        # Wait for authentication message
        auth_message = await websocket.receive_json()

        if auth_message.get("type") != "auth":
            await websocket.send_json({
                "type": "error",
                "message": "Authentication required"
            })
            await websocket.close()
            return

        token = auth_message.get("token")

        # Verify token
        user = await verify_token(token)

        if not user:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid token"
            })
            await websocket.close()
            return

        user_id = user.id

        # Register connection
        await manager.connect(websocket, user_id)

        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "user_id": user_id
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_json()

            # Handle ping/pong for keepalive
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            # Handle subscription to specific channels
            elif data.get("type") == "subscribe":
                channel = data.get("channel")
                # For now, just acknowledge
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel
                })

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
        print(f"WebSocket disconnected for user {user_id}")

    except Exception as e:
        print(f"WebSocket error: {e}")
        if user_id:
            manager.disconnect(websocket, user_id)
        await websocket.close()

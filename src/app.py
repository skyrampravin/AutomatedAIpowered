"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""
from http import HTTPStatus

from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity
from botframework.connector.auth import MicrosoftAppCredentials, SimpleCredentialProvider

from bot import bot_app
from config import Config

# Create adapter for local development (no authentication)
if not Config.APP_ID or Config.APP_ID == "" or Config.APP_ID == "00000000-0000-0000-0000-000000000000":
    # For local development with Bot Framework Emulator - completely disable auth
    print("🔓 Creating adapter with authentication disabled for local development")
    
    # Use empty credentials for local development
    credentials = SimpleCredentialProvider("", "")
    settings = BotFrameworkAdapterSettings(app_id="", app_password="", credential_provider=credentials)
    adapter = BotFrameworkAdapter(settings)
    
    # Override the authenticate method to always return an empty claims identity
    async def mock_authenticate_request(activity, auth_header):
        from botframework.connector.auth import ClaimsIdentity
        # Create a proper ClaimsIdentity with an empty claims dictionary (not list)
        return ClaimsIdentity(claims={}, is_authenticated=False)
    
    adapter._authenticate_request = mock_authenticate_request
    
else:
    # Production configuration with authentication
    print(f"🔒 Authentication enabled for App ID: {Config.APP_ID}")
    settings = BotFrameworkAdapterSettings(Config.APP_ID, Config.APP_PASSWORD)
    adapter = BotFrameworkAdapter(settings)

# Add error handler for any remaining issues
async def on_error(context, error):
    print(f"Error: {error}")
    if "Unauthorized Access" in str(error):
        print("💡 Tip: Ensure Bot Framework Emulator has empty App ID and Password fields")

adapter.on_turn_error = on_error

routes = web.RouteTableDef()

@routes.post("/api/messages")
async def on_messages(req: web.Request) -> web.Response:
    """Main bot message handler."""
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return web.Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    try:
        # Use the standard Bot Framework pattern
        response = await adapter.process_activity(activity, auth_header, bot_app.on_turn)
        if response:
            return web.Response(status=response.status, body=response.body)
        return web.Response(status=HTTPStatus.OK)
    except Exception as e:
        print(f"Error processing activity: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(status=HTTPStatus.INTERNAL_SERVER_ERROR, text=str(e))

app = web.Application(middlewares=[aiohttp_error_middleware])
app.add_routes(routes)

if __name__ == "__main__":
    try:
        web.run_app(app, host="localhost", port=Config.PORT)
    except Exception as e:
        raise e
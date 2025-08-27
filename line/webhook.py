from fastapi import Request, Response
from linebot.v3.messaging import MessagingApi, ApiClient, Configuration, TextMessage, ReplyMessageRequest
from config.settings import settings
from line.messages import message_processor

class LineWebhook:
    def __init__(self):
        cfg = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.line_client = MessagingApi(ApiClient(cfg))
        self.message_processor = message_processor
    
    async def handle_webhook(self, request: Request):
        """Handle LINE webhook requests"""
        try:
            payload = await request.json()
            print(f"📥 Received webhook payload: {payload}")
            
            for event in payload.get("events", []):
                if event["type"] != "message" or event["message"]["type"] != "text":
                    continue
                
                message_text = event["message"]["text"].strip()
                
                # DEBUG: Print the entire source object
                print(f"🔍 DEBUG: Full event source: {event.get('source', {})}")
                print(f"🔍 DEBUG: Source type: {type(event.get('source', {}))}")
                print(f"🔍 DEBUG: Source keys: {list(event.get('source', {}).keys())}")
                
                # Extract user ID correctly
                user_id = event["source"].get("userId", "")
                print(f"🔍 DEBUG: Extracted userId: '{user_id}'")
                print(f"🔍 DEBUG: userId length: {len(user_id) if user_id else 0}")
                
                if not user_id:
                    print("⚠️  No user ID found in event")
                    continue
                
                print(f"👤 Processing message from {user_id}: {message_text}")
                
                # Process message with AI
                reply = self.message_processor.process_message(user_id, message_text)
                print(f"💬 Sending AI reply: {reply[:100]}...")
                
                # Send reply via LINE
                self.line_client.reply_message(
                    ReplyMessageRequest(
                        replyToken=event["replyToken"],
                        messages=[TextMessage(text=reply)]
                    )
                )
            
            return "ok"
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return Response("Error processing webhook", status_code=500)

# Global webhook handler
line_webhook = LineWebhook()

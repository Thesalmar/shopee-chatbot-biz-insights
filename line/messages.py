from typing import Dict, Any
import time
from ai.chatgpt import chatgpt
from shopee.business_intelligence import shopee_bi
from database.models import db

class MessageProcessor:
    def __init__(self):
        self.bi = shopee_bi
        self.ai = chatgpt
    
    def process_message(self, user_id: str, message: str) -> str:
        """Process incoming message and generate response"""
        message_lower = message.lower()
        
        # Save seller query
        db.save_seller_query(user_id, message, "", int(time.time()))
        
        try:
            # Get shop data for context
            shop_data = self.bi.get_shop_info()
            if "error" not in shop_data:
                shop_context = shop_data
            else:
                shop_context = None
            
            # Handle specific commands with business data
            business_data = None
            
            # Comprehensive dashboard
            if any(word in message_lower for word in ["dashboard", "overview", "summary"]):
                business_data = self.bi.get_comprehensive_dashboard()
            
            # Shop info query
            elif any(word in message_lower for word in ["shop info", "shop details", "my shop"]):
                business_data = {"shop_info": shop_data}
            
            # Business analytics queries
            elif any(word in message_lower for word in ["orders", "sales", "analytics"]):
                if "product" in message_lower:
                    business_data = {"product_performance": self.bi.get_product_performance()}
                else:
                    business_data = {"order_analytics": self.bi.get_order_analytics()}
            
            elif "product" in message_lower and "performance" in message_lower:
                business_data = {"product_performance": self.bi.get_product_performance()}
            
            # Generate AI response with context
            response = self.ai.generate_response(
                user_id=user_id,
                message=message,
                shop_data=shop_context,
                business_data=business_data
            )
            
            # Update response in database
            timestamp = int(time.time())
            with db.get_connection() as conn:
                conn.execute(
                    "UPDATE seller_queries SET response = ? WHERE user_id = ? AND timestamp = (SELECT MAX(timestamp) FROM seller_queries WHERE user_id = ?)",
                    (response, user_id, user_id)
                )
                conn.commit()
            
            return response
            
        except Exception as e:
            print(f"❌ Error in message processing: {e}")
            return "🤖 I encountered an error processing your request. Please try again or contact support."

# Global message processor
message_processor = MessageProcessor()

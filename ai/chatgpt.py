#!/usr/bin/env python3
import openai
import json
from typing import List, Dict, Any, Optional
from config.settings import settings
from database.models import db

class ChatGPTIntegration:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        
        # Initialize OpenAI client with error handling
        self.client = None
        self.is_available = False
        
        if self.api_key:
            try:
                # Set the API key
                openai.api_key = self.api_key
                
                # Initialize client with minimal parameters - compatible with OpenAI v1.0+
                self.client = openai.OpenAI(api_key=self.api_key)
                self.is_available = True
                print("✅ ChatGPT integration initialized successfully")
                
            except Exception as e:
                print(f"⚠️ ChatGPT initialization failed: {e}")
                print("🔄 Falling back to basic responses")
                self.is_available = False
        else:
            print("⚠️ No OpenAI API key found - using fallback responses")
            self.is_available = False
    
    def get_system_prompt(self, shop_data: Dict[str, Any] = None) -> str:
        """Generate system prompt with shop context"""
        base_prompt = """You are a professional Shopee Seller Assistant AI. You help sellers manage their business with intelligence and insights.

IMPORTANT COMPLIANCE RULES:
- You are SELLER-FOCUSED ONLY - help shop owners/sellers manage their business
- NO automated buyer chat responses or customer service automation
- NO proactive messaging to customers or buyers
- NO chat spam or mass messaging features
- Focus on business intelligence, analytics, and seller tools

CAPABILITIES:
- Provide business analytics and insights
- Help interpret shop performance data
- Offer selling strategies and recommendations
- Explain Shopee seller features and policies
- Assist with product management guidance
- Generate business reports and summaries

TONE: Professional, helpful, business-focused
LANGUAGE: Match the user's language (English, Chinese, etc.)
FORMAT: Use emojis and clear formatting for better readability"""

        if shop_data:
            shop_context = f"""
CURRENT SHOP CONTEXT:
- Shop Name: {shop_data.get('shop_name', 'Unknown')}
- Shop ID: {shop_data.get('shop_id', 'Unknown')}
- Region: {shop_data.get('region', 'Unknown')}
- Status: {shop_data.get('status', 'Unknown')}
- Environment: Sandbox (for testing)
"""
            base_prompt += shop_context
        
        return base_prompt
    
    def build_conversation_context(self, user_id: str, current_message: str, shop_data: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Build conversation context with history"""
        messages = [{"role": "system", "content": self.get_system_prompt(shop_data)}]
        
        # Add recent chat history for context
        try:
            chat_history = db.get_chat_history(user_id, limit=5)
            for user_msg, assistant_msg in chat_history:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})
        except Exception as e:
            print(f"⚠️ Could not load chat history: {e}")
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    def generate_response(self, user_id: str, message: str, shop_data: Dict[str, Any] = None, business_data: Dict[str, Any] = None) -> str:
        """Generate AI response with shop context"""
        # If ChatGPT is not available, use fallback
        if not self.is_available or not self.client:
            return self.get_fallback_response(message)
        
        try:
            # Build conversation context
            messages = self.build_conversation_context(user_id, message, shop_data)
            
            # Add business data context if available
            if business_data:
                business_context = f"""
CURRENT BUSINESS DATA:
{json.dumps(business_data, indent=2)}

Use this data to provide specific, actionable insights. If the user asks about their business performance, reference this actual data.
"""
                messages.insert(-1, {"role": "system", "content": business_context})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Save to chat history
            try:
                import time
                db.save_chat_history(user_id, message, ai_response, int(time.time()))
            except Exception as e:
                print(f"⚠️ Could not save chat history: {e}")
            
            return ai_response
            
        except Exception as e:
            print(f"❌ ChatGPT Error: {e}")
            return self.get_fallback_response(message)
    
    def get_fallback_response(self, message: str) -> str:
        """Fallback response when AI is unavailable"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return """👋 **Hello! Welcome to your Shopee Business Assistant**

🤖 I'm your AI-powered business intelligence assistant!

**Popular Commands:**
📊 "dashboard" - Complete business overview
🏪 "shop info" - Shop details & status
💡 "help" - Full command list

I can help analyze your business data and provide insights! 🚀

*Note: Running in basic mode - AI features temporarily unavailable*"""
        
        elif any(word in message_lower for word in ["help", "commands"]):
            return """🤖 **Shopee Seller Assistant** (AI-Enhanced)

**Available Commands:**
🏪 "shop info" - Get shop information
📊 "dashboard" - Comprehensive business overview
📈 "orders" - Order analytics
🛍️ "product performance" - Product analysis
💬 Ask me anything about your business!

**AI Capabilities:**
✅ Business data analysis
✅ Performance insights
✅ Selling recommendations
✅ Natural language queries

**Environment:** 🧪 Sandbox Mode
**Status:** ⚠️ Basic mode (AI temporarily unavailable)"""
        
        elif any(word in message_lower for word in ["dashboard", "overview", "summary", "status"]):
            return """📊 **Business Dashboard Overview**

🏪 **Shop Status**: Connected & Operational
📈 **Analytics**: Available via dashboard commands
🛍️ **Products**: Use "product performance" for details
📊 **Orders**: Use "orders" for analytics

**Quick Actions:**
• "shop info" - Detailed shop information
• "product performance" - Product insights
• "orders" - Order analytics

*Running in basic mode - for enhanced AI insights, please check OpenAI configuration*"""
        
        else:
            return """💬 I understand you're looking for assistance!

🤖 **I'm your Shopee Seller Assistant**

I can help with:
📊 Business analytics and insights
🏪 Shop performance analysis
💡 Selling strategies and tips
📈 Data interpretation

**Try these commands:**
• "dashboard" - Business overview
• "shop info" - Shop details
• "help" - Full command list

*Running in basic mode - AI features temporarily unavailable*"""

# Global ChatGPT instance with error handling
try:
    chatgpt = ChatGPTIntegration()
except Exception as e:
    print(f"❌ Failed to initialize ChatGPT integration: {e}")
    
    # Create a minimal fallback instance
    class FallbackChatGPT:
        def __init__(self):
            self.is_available = False
        
        def generate_response(self, user_id: str, message: str, shop_data: Dict[str, Any] = None, business_data: Dict[str, Any] = None) -> str:
            return self.get_fallback_response(message)
        
        def get_fallback_response(self, message: str) -> str:
            return ChatGPTIntegration().get_fallback_response(message)
    
    chatgpt = FallbackChatGPT()

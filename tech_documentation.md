# Shopee AI Seller Assistant - Technical Documentation

## Project Overview

The **Shopee AI Seller Assistant** is a production-ready LINE bot that integrates ChatGPT AI capabilities with Shopee's Open Platform API. It provides intelligent business analytics, insights, and recommendations for Shopee sellers through natural language conversations.

## Architecture Overview

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Web Server**: nginx reverse proxy
- **Database**: SQLite for chat history and business data
- **AI Integration**: OpenAI GPT-4o-mini
- **Platform Integration**: LINE Messaging API + Shopee Open Platform
- **Environment**: Debian 12 Linux

### Core Architecture
```
shopee-chatbot-clemarguebiz/
├── main.py                          # FastAPI application entry
├── config/
│   └── settings.py                 # Environment configuration
├── database/
│   └── models.py                   # SQLite database models
├── ai/
│   └── chatgpt.py                  # ChatGPT integration
├── shopee/
│   ├── auth.py                     # OAuth authentication
│   ├── api.py                      # Shopee API wrapper
│   └── business_intelligence.py    # Business analytics
├── line/
│   ├── webhook.py                  # LINE webhook handler
│   └── messages.py                 # Message processing
└── utils/                          # Utility functions
```

## API Endpoints

### Authentication Endpoints
- **GET /shopee/auth** - Generate Shopee OAuth URL
- **GET /shopee/callback** - Handle OAuth callback

### LINE Webhook Endpoints
- **POST /webhook** - Process LINE messages with AI responses

### Business Intelligence Dashboard
- **GET /dashboard/shop** - Shop information
- **GET /dashboard/orders** - Order analytics (configurable days)
- **GET /dashboard/products** - Product performance
- **GET /dashboard/comprehensive** - Full business dashboard

### Debug Endpoints
- **GET /debug/check-tokens** - Verify token status
- **GET /debug/test-shop-info** - Test shop API
- **GET /health** - Health check
- **GET /** - Service status overview

## Environment Configuration

### Required Environment Variables (.env)
```bash
# LINE Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

# OpenAI Configuration  
OPENAI_API_KEY=your_openai_api_key

# Shopee API Configuration
SHOPEE_PARTNER_ID=your_partner_id
SHOPEE_PARTNER_KEY=your_partner_key
SHOP_ID=your_shop_id
COUNTRY=SG

# Server Configuration
TUNNEL_URL=https://your-domain.com
```

### Production Host Configuration
- **Production API**: https://partner.shopeemobile.com
- **Sandbox API**: https://openplatform.sandbox.test-stable.shopee.sg
- **Authentication Host**: https://account.sandbox.test-stable.shopee.com

## Sandbox Testing V2 Compliance

### Sandbox Environment Features
- **Test Account Creation**: Console → Test Account-Sandbox v2
- **Shop Authorization**: OAuth 2.0 flow with redirect URL
- **Order Management**: Create test orders with test products
- **Product Management**: Global products (MTSKU) and store products (MPSKU)
- **Logistics Testing**: First mile binding and shipment simulation
- **Push Notifications**: Webhook testing for real-time updates

### API Testing Process
1. **Create Test Account**: Use Sandbox v2 console
2. **Authorize Application**: Complete OAuth flow with partner_id
3. **Create Test Products**: Through Seller Center or API
4. **Generate Test Orders**: Simulate customer purchases
5. **Test Order Flow**: Process → Ship → Deliver → Complete
6. **Verify Webhooks**: Test push notifications

### Regional Considerations
- **CN Region**: Use https://openplatform.sandbox.test-stable.shopee.cn/
- **SG Region**: Use https://openplatform.sandbox.test-stable.shopee.sg/
- **OTP Code**: Use "123456" for sandbox verification

## Security Implementation

### Authentication Flow
1. **OAuth 2.0**: Secure token exchange with refresh capability
2. **HMAC Signing**: All API requests signed with partner_key
3. **Token Storage**: Encrypted storage in SQLite database
4. **Rate Limiting**: Built-in request throttling
5. **HTTPS Enforcement**: All endpoints require SSL/TLS

### Security Headers
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000

## Database Schema

### Token Storage
```sql
CREATE TABLE tokens (
    shop_id TEXT PRIMARY KEY,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat History
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Signature Generation

### Public API Signing
```python
base_str = f"{partner_id}{path}{timestamp}"
signature = hmac.new(
    partner_key.encode(),
    base_str.encode(),
    hashlib.sha256
).hexdigest()
```

### Shop API Signing
```python
base_str = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
signature = hmac.new(
    partner_key.encode(),
    base_str.encode(),
    hashlib.sha256
).hexdigest()
```

## LINE Bot Commands

### Available Commands
- **hello** - Welcome message with shop overview
- **dashboard** - Comprehensive business dashboard
- **shop info** - Detailed shop information
- **orders** - Order analytics (sandbox-aware)
- **product performance** - Product catalog analysis
- **help** - Full command reference

### Natural Language Queries
- "How is my shop performing?"
- "What should I focus on to improve sales?"
- "Analyze my product catalog"
- "Give me business recommendations"

## Deployment Configuration

### nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    location /webhook {
        proxy_pass http://127.0.0.1:9191/webhook;
        proxy_buffering off;
        proxy_request_buffering off;
        client_max_body_size 1M;
    }
    
    location / {
        proxy_pass http://127.0.0.1:9191;
    }
}
```

### systemd Service
```ini
[Unit]
Description=Shopee AI Seller Assistant
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/path/to/app
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/uvicorn main:app --host 127.0.0.1 --port 9191
Restart=always
```

## Error Handling

### Common Issues and Solutions

#### 1. Authentication Failures
- **Cause**: Invalid partner_id or partner_key
- **Solution**: Verify credentials in Shopee Partner Portal

#### 2. Token Expiration
- **Cause**: Access token expired (typically 7 days)
- **Solution**: Automatic refresh via refresh_token flow

#### 3. Sandbox Environment Issues
- **Cause**: Using production credentials in sandbox
- **Solution**: Ensure sandbox-specific credentials

#### 4. Rate Limiting
- **Cause**: Exceeding API rate limits
- **Solution**: Implement exponential backoff

#### 5. Webhook Issues
- **Cause**: Invalid webhook URL or SSL certificate
- **Solution**: Verify HTTPS and certificate validity

## Monitoring and Logging

### Health Check
- **Endpoint**: GET /health
- **Frequency**: Every 30 seconds
- **Response**: JSON with service status

### Logging Levels
- **INFO**: General operation logs
- **DEBUG**: API request/response details
- **ERROR**: Exception and error details
- **CRITICAL**: Service failure alerts

### Performance Monitoring
- **Response Time**: < 200ms for API calls
- **Uptime**: > 99.9% availability
- **Memory Usage**: < 512MB peak
- **Database Size**: < 100MB

## Development Workflow

### Local Development
```bash
# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 9191

# Test individual modules
python -c "from config.settings import settings; print('✅ Config OK')"
python -c "from database.models import db; print('✅ Database OK')"
python -c "from shopee.auth import shopee_auth; print('✅ Auth OK')"
```

### Testing Checklist
- [ ] LINE webhook receiving messages
- [ ] Shopee OAuth flow working
- [ ] API calls returning 200 status
- [ ] AI responses generating correctly
- [ ] Database connections stable
- [ ] SSL certificate valid
- [ ] nginx configuration tested

## Production Deployment

### Pre-deployment Checklist
- [ ] All environment variables configured
- [ ] SSL certificates obtained
- [ ] nginx configuration applied
- [ ] Database initialized
- [ ] systemd service enabled
- [ ] Firewall rules configured
- [ ] Monitoring alerts configured

### Deployment Commands
```bash
# Production deployment
sudo systemctl enable shopee-bot
sudo systemctl start shopee-bot
sudo systemctl status shopee-bot

# Monitor logs
sudo journalctl -u shopee-bot -f
```

## Compliance Notes

### Shopee Policy Compliance
- ✅ Seller-focused functionality only
- ✅ No buyer automation features
- ✅ Respects rate limits
- ✅ Uses official APIs only
- ✅ Follows OAuth 2.0 standards

### Data Protection
- ✅ No sensitive data logging
- ✅ Encrypted token storage
- ✅ HTTPS enforcement
- ✅ GDPR compliant messaging
- ✅ Secure webhook endpoints

## Version Information

### Current Version: v11.0
- **FastAPI**: 0.110.0
- **Python**: 3.11+
- **LINE SDK**: 3.12.0
- **OpenAI**: 1.51.0
- **Uvicorn**: 0.27.0

### Changelog
- v11.0: Modular architecture with ChatGPT integration
- v10.0: Added business intelligence dashboard
- v9.0: Implemented OAuth 2.0 authentication
- v8.0: Added sandbox testing support
- v7.0: Initial LINE bot integration

This documentation serves as the single source of truth for the Shopee AI Seller Assistant system architecture, configuration, and operational procedures.
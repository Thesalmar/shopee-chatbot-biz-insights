**\# 🤖 Shopee AI Seller Assistant LINE Bot**

A professional, AI-powered LINE bot that helps Shopee sellers manage their business with intelligent analytics, insights, and recommendations. Built with ChatGPT integration and a clean modular architecture.

**\## ✨ Features**

**\### 🧠 AI-Powered Intelligence**

\- **\*\*ChatGPT Integration\*\***: Natural language conversations with context awareness

\- **\*\*Business Analytics\*\***: AI-driven insights from your Shopee data

\- **\*\*Smart Recommendations\*\***: Personalized selling strategies and tips

\- **\*\*Multi-language Support\*\***: Responds in user's preferred language

**\### 🏪 Shopee Integration**

\- **\*\*Shop Information\*\***: Real-time shop status and details

\- **\*\*Product Analytics\*\***: Catalog performance analysis

\- **\*\*Order Insights\*\***: Sales analytics and trends (sandbox-aware)

\- **\*\*OAuth Authentication\*\***: Secure Shopee API integration

**\### 📱 LINE Bot Features**

\- **\*\*Interactive Commands\*\***: Rich business intelligence responses

\- **\*\*Context-Aware Chat\*\***: Remembers conversation history

\- **\*\*Professional UI\*\***: Clean formatting with emojis and structure

\- **\*\*Real-time Webhooks\*\***: Instant message processing

**\### 🏗️ Technical Excellence**

\- **\*\*Modular Architecture\*\***: Clean, maintainable codebase

\- **\*\*Production Ready\*\***: HTTPS, SSL certificates, nginx reverse proxy

\- **\*\*Database Persistence\*\***: SQLite for chat history and business data

\- **\*\*Error Handling\*\***: Graceful fallbacks and comprehensive logging

\- **\*\*Policy Compliant\*\***: Seller-focused, no buyer automation

**\## 📋 Requirements**

**\### System Requirements**

\- **\*\*OS\*\***: Debian 12 (or similar Linux distribution)

\- **\*\*Python\*\***: 3.11+

\- **\*\*Web Server\*\***: nginx

\- **\*\*SSL\*\***: Let's Encrypt certificates

**\### API Keys Required**

\- **\*\*LINE Channel Access Token\*\***: From LINE Developers Console

\- **\*\*OpenAI API Key\*\***: For ChatGPT integration

\- **\*\*Shopee Partner Credentials\*\***: Partner ID, Partner Key, Shop ID

**\### Domain & Infrastructure**

\- **\*\*Domain\*\***: With DNS pointing to your server

\- **\*\*HTTPS\*\***: SSL certificate for webhook endpoints

\- **\*\*Public IP\*\***: For webhook accessibility

**\## 🚀 Installation**

**\### 1. Clone and Setup Project**

\`\`\`bash

\# Clone the repository

git clone &lt;your-repo-url&gt;

cd shopee-chatbot-clemarguebiz

\# Create virtual environment

python3 -m venv venv

source venv/bin/activate

\# Install dependencies

pip install -r requirements.txt

**2\. Environment Configuration**

Create a .env file in the project root:

\# LINE Bot Configuration

LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

\# OpenAI Configuration

OPENAI_API_KEY=your_openai_api_key

\# Shopee API Configuration

SHOPEE_PARTNER_ID=your_partner_id

SHOPEE_PARTNER_KEY=your_partner_key

SHOP_ID=your_shop_id

COUNTRY=SG

\# Server Configuration

TUNNEL_URL=<https://your-domain.com>

**3\. Nginx Configuration**

Create /etc/nginx/sites-available/your-domain.com:

Copy**server** {

listen 80;

server_name your-domain.com;

return 301 https://$server_name$request_uri;

}

**server** {

listen 443 ssl http2;

server_name your-domain.com;

ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;

ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

ssl_protocols TLSv1.2 TLSv1.3;

ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;

ssl_prefer_server_ciphers off;

ssl_session_cache shared:SSL:10m;

ssl_session_timeout 10m;

add_header X-Frame-Options DENY;

add_header X-Content-Type-Options nosniff;

add_header X-XSS-Protection "1; mode=block";

add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

**location** / {

proxy_pass <http://127.0.0.1:9191>;

proxy_set_header Host $host;

proxy_set_header X-Real-IP $remote_addr;

proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

proxy_set_header X-Forwarded-Proto $scheme;

proxy_set_header X-Forwarded-Host $host;

proxy_set_header X-Forwarded-Port $server_port;

proxy_http_version 1.1;

proxy_set_header Upgrade $http_upgrade;

proxy_set_header Connection "upgrade";

proxy_connect_timeout 60s;

proxy_send_timeout 60s;

proxy_read_timeout 60s;

}

**location** /webhook {

proxy_pass <http://127.0.0.1:9191/webhook>;

proxy_set_header Host $host;

proxy_set_header X-Real-IP $remote_addr;

proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

proxy_set_header X-Forwarded-Proto $scheme;

proxy_set_header X-Forwarded-Host $host;

proxy_set_header X-Forwarded-Port $server_port;

proxy_buffering off;

proxy_request_buffering off;

client_max_body_size 1M;

proxy_http_version 1.1;

proxy_set_header Connection "";

proxy_connect_timeout 30s;

proxy_send_timeout 30s;

proxy_read_timeout 30s;

}

**location** /health {

proxy_pass <http://127.0.0.1:9191/health>;

proxy_set_header Host $host;

access_log off;

}

access_log /var/log/nginx/your-domain.com.access.log;

error_log /var/log/nginx/your-domain.com.error.log;

}

**4\. Enable Nginx Site**

Copy# Enable the site

sudo ln -s /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/

\# Test nginx configuration

sudo nginx -t

\# Restart nginx

sudo systemctl restart nginx

**5\. SSL Certificate Setup**

Copy# Install certbot

sudo apt update

sudo apt install certbot python3-certbot-nginx

\# Get SSL certificate

sudo certbot --nginx -d your-domain.com

\# Verify certificate

sudo certbot certificates

**🏃 Running the Application**

**Development Mode**

Copy# Activate virtual environment

source venv/bin/activate

\# Start the application

uvicorn main:app --host 127.0.0.1 --port 9191 --reload

**Production Mode (SystemD Service)**

Create /etc/systemd/system/shopee-bot.service:

Copy**\[Unit\]**

Description=Shopee AI Seller Assistant

After=network.target

**\[Service\]**

Type=simple

User=your-username

WorkingDirectory=/path/to/shopee-chatbot-clemarguebiz

Environment=PATH=/path/to/shopee-chatbot-clemarguebiz/venv/bin

ExecStart=/path/to/shopee-chatbot-clemarguebiz/venv/bin/uvicorn main:app --host 127.0.0.1 --port 9191

Restart=always

**\[Install\]**

WantedBy=multi-user.target

Enable and start the service:

Copy# Enable service

sudo systemctl enable shopee-bot

\# Start service

sudo systemctl start shopee-bot

\# Check status

sudo systemctl status shopee-bot

**⚙️ Configuration**

**1\. Shopee Authentication**

1. Visit <https://your-domain.com/shopee/auth>
2. Complete OAuth flow
3. Verify authentication at <https://your-domain.com/debug/check-tokens>

**2\. LINE Bot Setup**

1. Go to [LINE Developers Console](https://developers.line.biz/)
2. Create a new channel (Messaging API)
3. Set webhook URL: <https://your-domain.com/webhook>
4. Enable webhooks
5. Get Channel Access Token and add to .env

**3\. OpenAI Configuration**

1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to .env file
3. Verify integration: <https://your-domain.com/health>

**📁 Project Structure**

shopee-chatbot-clemarguebiz/

├── main.py # FastAPI application

├── requirements.txt # Python dependencies

├── .env # Environment variables

├── config/

│ ├── \__init_\_.py

│ └── settings.py # Configuration management

├── database/

│ ├── \__init_\_.py

│ └── models.py # Database operations

├── ai/

│ ├── \__init_\_.py

│ └── chatgpt.py # ChatGPT integration

├── shopee/

│ ├── \__init_\_.py

│ ├── auth.py # OAuth authentication

│ ├── api.py # API calls

│ └── business_intelligence.py # BI analytics

├── line/

│ ├── \__init_\_.py

│ ├── webhook.py # Webhook handling

│ └── messages.py # Message processing

└── utils/

└── \__init_\_.py # Utility functions

**🤖 Usage**

**LINE Bot Commands**

Send these messages to your LINE bot:

- **hello** - Welcome message with shop overview
- **dashboard** - Comprehensive business dashboard
- **shop info** - Detailed shop information
- **orders** - Order analytics (sandbox aware)
- **product performance** - Product catalog analysis
- **help** - Full command reference

**Natural Language Queries**

The AI can handle natural language questions like:

- "How is my shop performing?"
- "What should I focus on to improve sales?"
- "Analyze my product catalog"
- "Give me business recommendations"

**API Endpoints**

- **Health Check**: GET /health
- **Shop Info**: GET /dashboard/shop
- **Orders**: GET /dashboard/orders
- **Products**: GET /dashboard/products
- **Comprehensive**: GET /dashboard/comprehensive
- **Authentication**: GET /shopee/auth

**🔧 Troubleshooting**

**Common Issues**

**1\. Webhook Not Receiving Messages**

Copy# Check nginx logs

sudo tail -f /var/log/nginx/your-domain.com.access.log

\# Check application logs

sudo journalctl -u shopee-bot -f

**2\. SSL Certificate Issues**

Copy# Renew certificate

sudo certbot renew

\# Test certificate

curl -I <https://your-domain.com>

**3\. Database Issues**

Copy# Check database file

ls -la cache.db

\# Test database connection

python3 -c "from database.models import db; print('✅ Database OK')"

**4\. API Authentication Issues**

Copy# Check tokens

curl <https://your-domain.com/debug/check-tokens>

\# Re-authenticate

curl <https://your-domain.com/shopee/auth>

**Logs and Monitoring**

Copy# Application logs

sudo journalctl -u shopee-bot -f

\# Nginx logs

sudo tail -f /var/log/nginx/your-domain.com.access.log

sudo tail -f /var/log/nginx/your-domain.com.error.log

\# Check service status

sudo systemctl status shopee-bot nginx

**📊 Monitoring**

**Health Checks**

- **Application**: <https://your-domain.com/health>
- **Shop Connection**: <https://your-domain.com/debug/test-shop-info>
- **Token Status**: <https://your-domain.com/debug/check-tokens>

**Performance Monitoring**

Copy# Check resource usage

htop

\# Monitor logs

sudo journalctl -u shopee-bot --since "1 hour ago"

\# Database size

du -sh cache.db

**🔒 Security**

**Environment Variables**

- Never commit .env file to version control
- Use strong, unique API keys
- Regular key rotation recommended

**Network Security**

- HTTPS enforced for all endpoints
- Proper nginx security headers
- Webhook endpoint protected

**Data Protection**

- Local SQLite database
- No sensitive data in logs
- Compliant with Shopee policies

**📜 Requirements.txt**

Copy# FastAPI and Web Framework

fastapi==0.110.0

uvicorn\[standard\]==0.27.0

\# LINE Bot SDK

line-bot-sdk==3.12.0

\# OpenAI for ChatGPT Integration

openai>=1.30.0

\# HTTP Requests

requests>=2.32.3

\# Environment Variables

python-dotenv==1.0.1

\# Form Data Handling

python-multipart==0.0.20

\# Additional utilities

typing-extensions>=4.8.0

pydantic>=2.4.0

**🧪 Testing**

**Module Testing**

Copy# Test individual modules

python3 -c "from config.settings import settings; print('✅ Config OK')"

python3 -c "from database.models import db; print('✅ Database OK')"

python3 -c "from ai.chatgpt import chatgpt; print('✅ AI OK')"

python3 -c "from shopee.auth import shopee_auth; print('✅ Auth OK')"

python3 -c "from shopee.api import shopee_api; print('✅ API OK')"

python3 -c "from shopee.business_intelligence import shopee_bi; print('✅ BI OK')"

python3 -c "from line.webhook import line_webhook; print('✅ Webhook OK')"

python3 -c "from line.messages import message_processor; print('✅ Messages OK')"

**Integration Testing**

Copy# Test API endpoints

curl <https://your-domain.com/health>

curl <https://your-domain.com/debug/test-shop-info>

curl <https://your-domain.com/dashboard/shop>

\# Test webhook

curl -X POST <https://your-domain.com/webhook> \\

\-H "Content-Type: application/json" \\

\-d '{"test": "webhook"}' \\

\-v

**📄 License**

This project is licensed under the MIT License - see the [LICENSE](https://www.genspark.ai/LICENSE) file for details.

**🤝 Contributing**

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Make your changes
4. Test thoroughly
5. Commit your changes (git commit -m 'Add amazing feature')
6. Push to the branch (git push origin feature/amazing-feature)
7. Submit a pull request

**📞 Support**

For issues and questions:

1. **Check the troubleshooting section** above
2. **Review logs** for error messages
3. **Test individual components** using the testing commands
4. **Open an issue** on GitHub with detailed error information

**Debug Commands**

Copy# Quick health check

curl <https://your-domain.com/health> | jq

\# Check all services

sudo systemctl status shopee-bot nginx

\# View recent logs

sudo journalctl -u shopee-bot --lines=50

**🎉 Acknowledgments**

- [**LINE Messaging API**](https://developers.line.biz/) for bot platform
- [**OpenAI GPT**](https://openai.com/) for AI capabilities
- [**Shopee Open Platform**](https://open.shopee.com/) for e-commerce integration
- [**FastAPI**](https://fastapi.tiangolo.com/) for the web framework
- [**nginx**](https://nginx.org/) for reverse proxy

**🏆 Achievement**

**🚀 Your Shopee AI Seller Assistant is ready for business!**

This bot represents a complete, production-ready solution that combines:

- ✅ Professional AI integration
- ✅ Robust e-commerce API connectivity
- ✅ Enterprise-grade infrastructure
- ✅ Clean, maintainable architecture
- ✅ Comprehensive monitoring and logging

_Built with ❤️ for Shopee sellers who want to leverage AI for business growth_

This complete README.md provides comprehensive documentation covering all aspects of your AI-powered Shopee LINE bot from setup to production deployment and maintenance! 🚀📚

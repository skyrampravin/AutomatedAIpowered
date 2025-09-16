# AutomatedAI-Powered Learning Platform

A Microsoft Teams bot that provides automated, AI-powered learning experiences with daily quizzes, progress tracking, and adaptive content delivery.

## 🌟 Features

- **🎯 Personalized Learning**: AI-generated quizzes adapted to individual progress  
- **📈 Progress Tracking**: Comprehensive tracking with streaks and achievements
- **🔔 Smart Reminders**: Proactive notifications and motivation
- **📊 Analytics**: Detailed progress reports and learning insights
- **🎨 Interactive UI**: Rich adaptive cards for engaging user experience
- **⚙️ Flexible Deployment**: Sandbox for MVP, Azure for scale

## 🚀 Quick Start (Sandbox Mode)

Perfect for proof of concept, demos, and small user bases (< 50 users).

### Prerequisites
- Microsoft 365 Developer account (free)
- OpenAI API key
- Python 3.11+
- ngrok (for local testing)

### 5-Minute Setup
1. **Clone and configure**:
   ```bash
   git clone <repository-url>
   cd AutomatedAIpowered
   cp .env.example .env.playground
   # Add your OpenAI API key to .env.playground
   ```

2. **Install and run**:
   ```bash
   pip install -r requirements.txt
   python src/app.py --env playground
   ```

3. **Expose locally**:
   ```bash
   # In another terminal
   ngrok http 3978
   ```

4. **Register in Teams**:
   - Go to [Teams Developer Portal](https://dev.teams.microsoft.com/)
   - Import `appPackage/manifest.json`
   - Update bot endpoint to your ngrok URL + `/api/messages`
   - Install to your Teams

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/enroll [course]` | Enroll in a learning course |
| `/quiz` | Start today's quiz |
| `/progress` | View your learning progress |
| `/streak` | Check your current streak |
| `/admin` | Access monitoring dashboard |

## 🏗️ Architecture

### Sandbox Mode (Default)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Microsoft     │    │   Python Bot     │    │   OpenAI API    │
│     Teams       │◄──►│   (Local)        │◄──►│   (GPT-3.5)     │
│   (Sandbox)     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │  File Storage    │
                       │  (playground/)   │
                       └──────────────────┘
```

### Production Mode (Azure)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Microsoft     │    │   Azure App      │    │   OpenAI API    │
│     Teams       │◄──►│   Service        │◄──►│                 │
│   (Production)  │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                 │
                                 ▼
                       ┌──────────────────┐
                       │  Azure Storage   │
                       │  Tables/Cosmos   │
                       └──────────────────┘
```

## 🔧 Configuration

### Sandbox Environment (.env.playground)
```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Bot Configuration (from Teams Developer Portal)
BOT_ID=your-sandbox-bot-id
BOT_PASSWORD=your-sandbox-bot-password

# Sandbox Settings
ENVIRONMENT=sandbox
STORAGE_TYPE=file
DATA_DIRECTORY=playground/data
```

### Production Environment (.env.production)
```env
# Azure Bot Service
BOT_ID=your-production-bot-id
BOT_PASSWORD=your-production-bot-password

# OpenAI Configuration  
OPENAI_API_KEY=your-openai-api-key

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=your-azure-storage-connection
STORAGE_TYPE=azure_table
```

## 📊 Monitoring & Analytics

### Sandbox Monitoring
- Access `/admin` endpoint for real-time dashboard
- View `playground/logs/` for detailed logs
- Daily reports via `python scripts/generate_report.py`

### Production Monitoring
- Azure Application Insights integration
- Azure Bot Analytics dashboard
- Custom monitoring via Azure Monitor

## 🚀 Scaling to Production

When ready to scale beyond sandbox limitations:

1. **Deploy Azure Infrastructure**:
   ```bash
   cd infra
   az deployment sub create --location eastus --template-file azure.bicep
   ```

2. **Migrate Sandbox Data**:
   ```bash
   python scripts/migrate_sandbox_to_azure.py
   ```

3. **Deploy to Azure App Service**:
   ```bash
   ./scripts/deploy_to_azure.ps1
   ```

## 📚 Documentation

- **[Day 1-7 Instructions](Day1_Detailed_Instructions.md)**: Complete development guide
- **[Deployment Guide](DEPLOYMENT.md)**: Detailed deployment options
- **[API Documentation](docs/api.md)**: Bot API reference
- **[Contributing](CONTRIBUTING.md)**: Development guidelines

## 🎯 Use Cases

### Sandbox Perfect For:
- ✅ Proof of concept demos
- ✅ Internal team training (< 50 users)
- ✅ Rapid prototyping and iteration
- ✅ Learning bot development
- ✅ Cost-conscious deployments

### Production Recommended For:
- ✅ Large scale deployments (> 50 users)
- ✅ External customer training
- ✅ Enterprise compliance requirements
- ✅ Automated daily scheduling
- ✅ Advanced analytics and reporting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)  
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)


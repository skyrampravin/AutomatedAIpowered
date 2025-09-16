# AutomatedAIpowered Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Core Functionality](#core-functionality)
3. [Technical Architecture](#technical-architecture)
4. [Key Features](#key-features)
5. [Project Structure](#project-structure)
6. [Development Environment](#development-environment)
7. [Implementation Plan](#implementation-plan)
8. [Sandbox Usage Model](#sandbox-usage-model)
9. [Next Steps](#next-steps)

---

## Project Overview

**AutomatedAIpowered** is an AI-driven learning platform designed as a Microsoft Teams application that delivers a **30-day course challenge**. The project aims to create an automated learning system where employees can enroll in courses and receive daily AI-generated multiple-choice questions (MCQs) to test their knowledge progressively.

### Project Goal
Create an application in your organization where co-employees can enroll in a 30-day course challenge that:
- Generates 10 AI-powered MCQs daily about course material
- Tracks wrong answers and re-asks them until mastered
- Integrates seamlessly with Microsoft Teams
- Provides adaptive learning based on individual progress

---

## Core Functionality

### Learning Workflow
1. **Employee Enrollment**: Co-workers can enroll in a 30-day course challenge
2. **Daily AI Questions**: Each day, the AI generates 10 MCQs about the course material
3. **Progress Tracking**: The system tracks correct and incorrect answers
4. **Adaptive Learning**: Wrong answers are stored and re-asked on subsequent days until mastered
5. **Course Completion**: The 30-day challenge continues until all material is mastered

### User Journey
```
Day 1: User enrolls → Receives 10 MCQs → Answers tracked
Day 2: Gets 10 new MCQs + any wrong answers from Day 1
Day 3: Gets 10 new MCQs + any remaining wrong answers
...
Day 30: Course completion when all questions mastered
```

---

## Technical Architecture

### Frontend/Interface
- **Microsoft Teams Integration**: Built as a Teams bot application
- **Teams App Manifest** (`appPackage/manifest.json`): Defines app configuration, bot permissions, and UI elements
- **Adaptive Cards**: Interactive UI for presenting MCQs with radio buttons and submit actions
- **Multi-scope Support**: Works in personal chats, group chats, and team channels

### Backend (Python-based)
**Core Components:**
- **`src/bot.py`**: Main bot logic and AI integration using Teams AI Library
- **`src/app.py`**: Web server handling Teams messaging endpoint (aiohttp-based)
- **`src/config.py`**: Configuration management for environment variables

**Key Technologies:**
- Microsoft Teams AI Library
- Bot Framework SDK v4
- Python 3.8-3.11 compatible
- Asynchronous web server (aiohttp)

### AI Integration
**OpenAI Integration:**
- Uses GPT models (configurable, default: gpt-3.5-turbo)
- API key-based authentication
- Customizable model parameters

**Prompt Management:**
- **`src/prompts/chat/skprompt.txt`**: AI prompt templates
- **`src/prompts/chat/config.json`**: AI model configuration
  - Temperature: 0.9 (creative responses)
  - Max tokens: 1000
  - Includes conversation history
  - Presence/frequency penalty settings

### Infrastructure (Azure-based)
**Infrastructure as Code:**
- **`infra/azure.bicep`**: Main Azure resource definitions
- **`infra/botRegistration/azurebot.bicep`**: Bot-specific resources

**Azure Resources:**
- App Service (Linux-based) for hosting the bot
- User-assigned Managed Identity for secure access
- Bot registration for Teams integration
- OpenAI API key management through secure parameters

**Environment Management:**
- Multiple environment configurations (dev, local, playground)
- Secure secret management
- Environment-specific deployments

---

## Key Features

### Adaptive Learning System
- **Individual Progress Tracking**: Each user's learning journey is tracked separately
- **Wrong Answer Queue**: Maintains incorrect answers for re-presentation
- **Mastery-based Progression**: Questions repeated until correctly answered
- **Personalized Learning Path**: Adapts to individual learning pace

### Teams Integration Features
- **Native Bot Experience**: Seamless integration within Teams interface
- **Multi-scope Support**: Personal, group chat, and team channel interactions
- **Command-based Interaction**: Predefined commands for easy navigation
- **Proactive Messaging**: Daily reminders and notifications
- **Rich UI**: Adaptive Cards for interactive question presentation

### AI-Powered Question Generation
- **Dynamic Content Creation**: AI generates contextually relevant MCQs
- **Course-specific Questions**: Tailored to specific learning objectives
- **Variety and Engagement**: Diverse question formats and difficulty levels
- **Continuous Learning**: AI adapts question style based on user responses

---

## Project Structure

```
AutomatedAIpowered/
├── appPackage/              # Teams app packaging
│   ├── manifest.json        # Teams app configuration
│   ├── color.png           # App icon (colored)
│   └── outline.png         # App icon (outline)
├── src/                    # Python source code
│   ├── app.py              # Web server entry point
│   ├── bot.py              # Bot logic and AI integration
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   └── prompts/
│       └── chat/
│           ├── config.json # AI model configuration
│           └── skprompt.txt# AI prompt templates
├── infra/                  # Infrastructure as Code
│   ├── azure.bicep         # Main Azure resources
│   ├── azure.parameters.json# Deployment parameters
│   └── botRegistration/
│       ├── azurebot.bicep  # Bot-specific resources
│       └── readme.md       # Bot registration guide
├── env/                    # Environment configurations
│   ├── .env.dev            # Development environment
│   ├── .env.local          # Local development
│   └── .env.playground     # Testing environment
├── devTools/               # Development utilities
│   └── teamsapptester      # Local Teams testing
├── .vscode/                # VS Code configuration
├── planning files/         # Project planning documents
│   ├── day1.txt - day7.txt # Daily implementation plans
│   ├── plan.txt            # Overall project plan
│   └── newplan.txt         # Revised project plan
└── m365agents.yml          # Microsoft 365 Agents Toolkit config
```

---

## Development Environment

### Prerequisites
- **Python 3.8-3.11**: Core runtime environment
- **Visual Studio Code**: Recommended IDE
- **Microsoft 365 Agents Toolkit**: Teams development framework
- **OpenAI Account**: For AI question generation
- **Microsoft 365 Developer Account**: For Teams app testing
- **Azure Subscription**: For cloud deployment

### Development Tools
- **Python Extension**: VS Code Python language support
- **Microsoft 365 Agents Toolkit Extension**: Teams app development
- **Teams App Tester**: Local testing utilities
- **Azure CLI**: Infrastructure deployment

### Configuration Setup
1. **Python Virtual Environment**: Isolated dependency management
2. **Environment Variables**: Secure credential storage
3. **OpenAI API Key**: AI service authentication
4. **Bot Registration**: Teams integration setup

---

## Implementation Plan

### Week 1: Foundation Setup
**Day 1: Project Setup & Azure Bot Registration**
- Review project materials and folder structure
- Register Azure Bot resource and obtain credentials
- Enable Microsoft Teams channel
- Update Teams app manifest with bot details
- Configure environment variables securely

**Day 2: Infrastructure & Environment Configuration**
- Review and update Azure Bicep templates
- Deploy Azure infrastructure resources
- Configure environment variables for all environments
- Test resource connectivity and access

**Day 3: Bot Backend & Enrollment Logic**
- Review existing bot code structure
- Implement user enrollment functionality
- Set up progress tracking and data storage
- Test enrollment flow in Teams

**Day 4: AI Question Generation & Daily Quiz Logic**
- Integrate AI question generation using OpenAI
- Implement daily quiz delivery logic
- Format questions as interactive Adaptive Cards
- Test question generation and delivery

**Day 5: Answer Evaluation & Progress Tracking**
- Implement answer evaluation and scoring
- Update progress tracking and wrong answer queue
- Test answer handling and feedback

**Day 6: Scheduling & Proactive Messaging**
- Set up daily scheduler for automated quiz delivery
- Implement proactive messaging for reminders
- Test automation and reminder functionality

**Day 7: Final Testing, Packaging & Documentation**
- Simulate full 30-day workflow
- Update documentation and setup guides
- Package Teams app for deployment
- Conduct final testing and bug fixes

---

## Next Steps

### Immediate Actions
1. **Complete Day 1 Setup**: Follow day1exec.txt for Azure bot registration
2. **Environment Configuration**: Set up all required environment variables
3. **Local Development**: Configure Python environment and dependencies
4. **Teams Integration**: Test basic bot functionality in Teams

### Custom Development Required
1. **Course Content Integration**: Define course materials and learning objectives
2. **Question Database**: Create or integrate existing question repositories
3. **User Management**: Implement enrollment and user state management
4. **Progress Analytics**: Add reporting and progress visualization
5. **Completion Certificates**: Generate completion certificates for 30-day challenge

### Optional Enhancements
1. **Dashboard Tab**: Create Teams tab for progress visualization
2. **Admin Panel**: Management interface for course content
3. **Multiple Courses**: Support for different course types
4. **Team Challenges**: Group-based learning competitions
5. **Integration APIs**: Connect with existing LMS or HR systems

### Production Considerations
1. **Scalability**: Design for organization-wide deployment
2. **Security**: Implement proper authentication and authorization
3. **Monitoring**: Add logging, metrics, and alerting
4. **Backup & Recovery**: Data protection and disaster recovery
5. **Compliance**: Ensure data privacy and regulatory compliance

---

## Technology Stack Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Microsoft Teams | User interface and interaction |
| Backend | Python + Teams AI Library | Bot logic and processing |
| AI Engine | OpenAI GPT Models | Question generation and NLP |
| Infrastructure | Azure (Bicep IaC) | Cloud hosting and services |
| Storage | Azure Storage/CosmosDB | User data and progress tracking |
| Development | VS Code + M365 Toolkit | Development environment |
| Deployment | Azure DevOps/GitHub Actions | CI/CD pipeline |

---

---

## Sandbox Usage Model

The project intentionally supports a sandbox-first development approach using a Microsoft 365 Developer tenant before introducing production infrastructure. This reduces organizational risk and accelerates iteration.

### Why Sandbox First
| Benefit | Impact |
|---------|--------|
| Isolation | No effect on production users or compliance posture |
| Rapid Iteration | Faster feedback cycles without change control overhead |
| Safe Experimentation | Freely test prompts, quiz flows, and proactive messaging |
| Early Validation | Validate pedagogical structure before infra investment |

### Environment Comparison
| Dimension | Sandbox (Playground) | Production |
|----------|----------------------|------------|
| Bot Identity | Developer Portal Bot ID | Separate production Bot ID |
| App Manifest | May suffix name `(Sandbox)` | Formal naming & versioning |
| Storage | File / in-memory | Azure Table / Cosmos DB |
| Scheduler | Manual / local / basic timer | Azure Functions / Logic Apps |
| Secrets | `.env.playground` (local only) | Key Vault / pipeline secrets |
| Logging | Console prints | Structured + App Insights |
| Proactive Auth | Open / minimal checks | Authenticated + throttled |
| AI Cost Controls | Low volume, cached sets | Scaled usage monitoring |
| Observability | Manual inspection | Metrics, dashboards, alerts |

### Recommended Sandbox Workflow
1. Follow `SANDBOX_QUICKSTART.md` for one-page bootstrap.
2. Deepen with `SANDBOX_SETUP.md` for phased hardening.
3. Use `SANDBOX_END_TO_END.md` to ensure coverage before migration.
4. Collect sample data snapshots (progress, wrong answers) to inform schema.
5. Produce a readiness summary: gaps in storage, security, observability.

### Migration Checklist (Sandbox → Production)
| Step | Action | Artifact |
|------|--------|----------|
| 1 | Create production Bot registration | Azure / Developer Portal |
| 2 | Add persistent storage (Table/Cosmos) & refactor storage layer | Storage module |
| 3 | Introduce Key Vault + secret references | Infra Bicep / pipeline |
| 4 | Enable Application Insights + basic dashboards | Monitoring config |
| 5 | Deploy Azure Function for scheduling | Function App |
| 6 | Harden proactive endpoint (auth + rate limiting) | API layer |
| 7 | Update manifest with production IDs & domains | `manifest.json` |
| 8 | Add CI/CD pipeline for packaging + deploy | GitHub Actions/Azure DevOps |
| 9 | Security review & compliance alignment | Review doc |
| 10 | Controlled pilot rollout & feedback loop | Pilot report |

### Sandbox Exit Criteria
- All core quiz flows stable for multiple test users
- Wrong-answer requeue logic validated across at least 3 cycles
- Proactive reminder tested manually (and optionally via timer)
- Data structure for progress & wrong answers documented for migration
- AI prompt baseline captured with sample outputs
- Packaging script produces repeatable artifact

### Risks if Skipping Sandbox Phase
- Unvetted prompt behaviors in production
- Inefficient question generation cost patterns
- Storage schema churn after real usage insight
- Undetected proactive messaging edge cases (missing conversation references)

Refer to: `SANDBOX_QUICKSTART.md`, `SANDBOX_SETUP.md`, and `SANDBOX_END_TO_END.md` for actionable steps.

---

*This document serves as a comprehensive guide for understanding and implementing the AutomatedAIpowered learning platform. For specific implementation details, refer to the daily execution plans (day1exec.txt through day7exec.txt) and the source code in the project repository.*
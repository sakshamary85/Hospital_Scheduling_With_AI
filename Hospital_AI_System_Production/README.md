# 🏥 Hospital AI System - Production Version

## 🎯 **System Overview**

This is the production-ready Hospital AI Appointment Scheduling System that integrates:
- **ML Model**: Pre-trained no-show prediction model
- **AI Agent**: Intelligent scheduling and risk assessment
- **Backend Integration**: Real-time database connectivity
- **API Services**: RESTful endpoints for hospital systems
- **Production Features**: Security, monitoring, and scalability

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hospital      │    │   AI Agent      │    │   ML Model      │
│   Backend       │◄──►│   Core          │◄──►│   (LightGBM)    │
│   Systems       │    │   System        │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Risk          │    │   Feature       │
│   Models        │    │   Assessment    │    │   Engineering   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 **Project Structure**

```
Hospital_AI_System_Production/
├── ai_agent_core/          # AI Agent core modules
├── backend_integration/     # Backend connectivity services
├── api_services/           # REST API endpoints
├── database_models/        # SQLAlchemy database models
├── production_config/      # Configuration management
├── testing_framework/      # Testing and validation
├── deployment_scripts/     # Production deployment
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 **Key Features**

### **1. ML Model Integration** 🤖
- **98 Features**: Complete feature set for no-show prediction
- **LightGBM Model**: Pre-trained model integration
- **Real-time Predictions**: Instant risk assessment
- **Feature Engineering**: Automatic data preparation

### **2. AI Agent Intelligence** 🧠
- **Risk Assessment**: Low/Medium/High risk categorization
- **Smart Scheduling**: ML-based slot optimization
- **Waitlist Management**: Priority-based queue system
- **Dynamic Decisions**: Real-time strategy adaptation

### **3. Backend Integration** 🔗
- **Database Models**: Comprehensive entity relationships
- **Real-time Updates**: Live slot availability
- **Patient Services**: Complete patient data management
- **Appointment Services**: End-to-end appointment handling

### **4. Production Ready** 🏭
- **Security**: JWT authentication, role-based access
- **Monitoring**: Comprehensive logging and metrics
- **Scalability**: Microservices architecture
- **API First**: RESTful endpoints for integration

## ⚙️ **Configuration**

### **Environment Variables**
Create a `.env` file in the root directory:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hospital_ai_db
POSTGRES_USER=hospital_user
POSTGRES_PASSWORD=your_password

# ML Model Configuration
MODEL_PATH=C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl

# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Security
JWT_SECRET_KEY=your-secret-key-here
```

### **Hospital Settings**
```python
# Working Hours: 9 AM - 6 PM
WORKING_HOURS_START = 9
WORKING_HOURS_END = 18
SLOT_DURATION_MINUTES = 30

# Risk Thresholds
LOW_RISK_THRESHOLD = 0.3      # 0-30%
MEDIUM_RISK_THRESHOLD = 0.6   # 31-60%
HIGH_RISK_THRESHOLD = 0.8     # 61-100%
```

## 🗄️ **Database Setup**

### **1. PostgreSQL Installation**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb hospital_ai_db

# Create user
sudo -u postgres createuser hospital_user
```

### **2. Database Initialization**
```bash
# Run database migrations
python -m alembic upgrade head

# Seed initial data
python scripts/seed_database.py
```

## 🚀 **Installation & Setup**

### **1. Clone Repository**
```bash
git clone <repository-url>
cd Hospital_AI_System_Production
```

### **2. Install Dependencies**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### **3. Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### **4. Database Setup**
```bash
# Initialize database
python scripts/init_database.py

# Run migrations
alembic upgrade head
```

### **5. Start Services**
```bash
# Start API server
uvicorn api_services.main:app --host 0.0.0.0 --port 8000

# Start background workers
celery -A ai_agent_core.worker worker --loglevel=info
```

## 📊 **API Endpoints**

### **Patient Management**
```
GET    /api/v1/patients/{patient_id}           # Get patient data
POST   /api/v1/patients                        # Create patient
PUT    /api/v1/patients/{patient_id}           # Update patient
DELETE /api/v1/patients/{patient_id}           # Delete patient
```

### **Appointment Scheduling**
```
POST   /api/v1/appointments/schedule           # Schedule appointment
GET    /api/v1/appointments/{appointment_id}   # Get appointment
PUT    /api/v1/appointments/{appointment_id}   # Update appointment
DELETE /api/v1/appointments/{appointment_id}   # Cancel appointment
```

### **AI Agent Operations**
```
POST   /api/v1/ai/assess-risk                 # Risk assessment
POST   /api/v1/ai/schedule-optimal            # Optimal scheduling
GET    /api/v1/ai/waitlist                    # Waitlist status
```

### **System Management**
```
GET    /api/v1/system/health                  # System health
GET    /api/v1/system/metrics                 # Performance metrics
GET    /api/v1/system/logs                    # System logs
```

## 🧪 **Testing**

### **1. Unit Tests**
```bash
# Run all tests
pytest

# Run specific module
pytest testing_framework/test_ai_agent.py

# Run with coverage
pytest --cov=ai_agent_core --cov-report=html
```

### **2. Integration Tests**
```bash
# Test API endpoints
pytest testing_framework/test_api_integration.py

# Test database operations
pytest testing_framework/test_database.py
```

### **3. Load Testing**
```bash
# Test system performance
python testing_framework/load_test.py

# Test concurrent appointments
python testing_framework/concurrent_test.py
```

## 📈 **Monitoring & Logging**

### **1. Application Logs**
```python
# Log files location
logs/hospital_ai.log      # General application logs
logs/error.log           # Error logs
logs/access.log          # API access logs
```

### **2. Performance Metrics**
```python
# Prometheus metrics
- appointment_requests_total
- ml_predictions_total
- risk_assessments_total
- slot_utilization_rate
- waitlist_size
```

### **3. Health Checks**
```python
# System health endpoints
GET /health              # Basic health check
GET /health/detailed     # Detailed system status
GET /health/database     # Database connectivity
GET /health/ml_model     # ML model status
```

## 🔒 **Security Features**

### **1. Authentication**
- **JWT Tokens**: Secure token-based authentication
- **Role-based Access**: Different permissions for different user types
- **Session Management**: Secure session handling

### **2. Data Protection**
- **Encryption**: Sensitive data encryption at rest
- **Audit Logging**: Complete audit trail for all operations
- **Input Validation**: Comprehensive input sanitization

### **3. API Security**
- **Rate Limiting**: Prevent API abuse
- **CORS Configuration**: Secure cross-origin requests
- **Request Validation**: Pydantic-based request validation

## 🚀 **Deployment**

### **1. Production Deployment**
```bash
# Build Docker image
docker build -t hospital-ai-system .

# Run with Docker Compose
docker-compose up -d

# Deploy to Kubernetes
kubectl apply -f deployment/
```

### **2. Environment Management**
```bash
# Production environment
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export DEBUG=False

# Development environment
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
export DEBUG=True
```

### **3. Scaling**
```bash
# Horizontal scaling
kubectl scale deployment hospital-ai-api --replicas=5

# Load balancing
kubectl apply -f ingress/load-balancer.yaml
```

## 📚 **Documentation**

### **1. API Documentation**
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

### **2. Code Documentation**
- **Docstrings**: Comprehensive function documentation
- **Type Hints**: Full type annotations
- **Examples**: Usage examples in docstrings

### **3. Architecture Documentation**
- **System Design**: High-level architecture overview
- **Data Flow**: End-to-end data processing
- **Integration Guide**: Backend system integration

## 🤝 **Contributing**

### **1. Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run code formatting
black .
flake8 .
mypy .
```

### **2. Code Standards**
- **PEP 8**: Python code style guide
- **Type Hints**: Full type annotations required
- **Documentation**: Comprehensive docstrings
- **Testing**: Minimum 90% test coverage

## 📞 **Support & Contact**

### **1. Technical Support**
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Documentation**: Comprehensive documentation available

### **2. Contact Information**
- **Email**: support@hospital-ai.com
- **Slack**: #hospital-ai-support
- **Phone**: +1-800-HOSPITAL-AI

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **ML Model**: Pre-trained LightGBM model for no-show prediction
- **AI Framework**: Custom AI Agent framework for hospital scheduling
- **Backend**: SQLAlchemy, FastAPI, and PostgreSQL integration
- **Production**: Docker, Kubernetes, and monitoring tools

---

**🏥 Hospital AI System - Making Healthcare Smarter, One Appointment at a Time! 🚀**

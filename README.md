# Hospital AI Appointment Scheduler

A Python-based AI Agent system that integrates with existing ML models to provide intelligent hospital appointment scheduling and optimization. The system reduces no-shows, optimizes doctor slot allocation, and manages high-risk patients through intelligent waitlist management.

## 🏥 Features

### Core AI Agent Capabilities
- **ML Model Integration**: Seamlessly integrates with your existing trained ML models
- **Intelligent Risk Assessment**: Categorizes patients into low/medium/high risk based on ML predictions
- **Dynamic Scheduling**: Optimizes appointment slots based on patient risk and preferences
- **Waitlist Management**: Priority-based waitlist with automatic slot filling
- **Real-time Optimization**: Continuously optimizes schedules for maximum efficiency

### Risk-Based Scheduling Strategies
- **Low Risk (≤30%)**: Standard scheduling with minimal intervention
- **Medium Risk (31-60%)**: Enhanced scheduling with buffer time and confirmation calls
- **High Risk (>60%)**: Intensive scheduling with extended buffers and frequent follow-ups

### Smart Slot Optimization
- **Doctor Availability Management**: Automatic schedule generation and capacity planning
- **Patient Preference Matching**: Finds optimal slots based on doctor, date, and time preferences
- **Buffer Time Management**: Automatically adds appropriate buffer time for high-risk patients
- **Conflict Resolution**: Intelligent handling of scheduling conflicts and rescheduling

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd hospital-ai-scheduler

# Install dependencies
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from hospital_ai_scheduler import AIAppointmentScheduler
from datetime import datetime

# Initialize the AI scheduler with your ML model
scheduler = AIAppointmentScheduler(
    model_path="path/to/your/trained_model.pkl",
    scaler_path="path/to/your/scaler.pkl"  # Optional
)

# Patient data for ML prediction
patient_data = {
    "age": 45,
    "gender": 1,
    "no_shows_history": 0,
    "sms_received": 1,
    # ... other features your model expects
}

# Appointment request
appointment_request = {
    "patient_id": "P001",
    "preferred_doctor": "DR001",
    "preferred_date": datetime.now() + timedelta(days=7),
    "preferred_time": "afternoon",
    "urgency_score": 2
}

# Schedule appointment using AI
result = scheduler.schedule_appointment(patient_data, appointment_request)
print(f"Appointment {result['action']}: {result}")
```

### 3. Run Tests

```bash
# Run the complete test suite
python test_ai_scheduler.py

# Run specific tests
python -m pytest tests/
```

## 🏗️ Architecture

### Core Modules

#### 1. **ML Integration** (`ml_integration.py`)
- Loads and manages your trained ML models
- Handles data preprocessing and feature engineering
- Provides standardized prediction interface
- **Full Output Support**: Returns prediction, no-show probability, and show probability
- **Your Model Format**: Handles the 3-part output (Prediction, No-show Prob, Show Prob)

#### 2. **Risk Assessor** (`risk_assessor.py`)
- Analyzes patient no-show risk based on ML predictions
- Determines appropriate scheduling strategies
- Calculates waitlist priority scores

#### 3. **Slot Optimizer** (`slot_optimizer.py`)
- Manages doctor availability and slot capacity
- Finds optimal appointment slots based on preferences
- Handles scheduling conflicts and rescheduling

#### 4. **Waitlist Manager** (`waitlist_manager.py`)
- Maintains priority-based patient waitlist
- Automatically fills available slots
- Tracks contact attempts and follow-up requirements

#### 5. **AI Agent** (`ai_agent.py`)
- Orchestrates all components
- Provides unified interface for appointment scheduling
- Handles system configuration and data export

## 📊 Data Flow

```
Patient Request → ML Model → Risk Assessment → Scheduling Strategy → Slot Optimization → Appointment Confirmation
                                    ↓
                              Waitlist Management (if needed)
```

## 🤖 ML Model Output Format

Your trained model provides 3 outputs that the AI Agent uses:

```python
# Example model output
{
    "prediction": "Show",           # Main prediction: "Show" or "No-show"
    "no_show_probability": 0.2618131,  # Probability of no-show
    "show_probability": 0.7381869      # Probability of show
}
```

The AI Agent uses the **no-show probability** for risk assessment and scheduling decisions, while the **prediction** provides a clear action recommendation.

## 🔧 Configuration

### Risk Thresholds
```python
# Customize risk assessment thresholds
custom_thresholds = {
    "low_threshold": 0.25,    # Default: 0.3
    "medium_threshold": 0.55,  # Default: 0.6
    "high_threshold": 0.75     # Default: 0.8
}

scheduler = AIAppointmentScheduler(
    model_path="model.pkl",
    risk_thresholds=custom_thresholds
)
```

### System Configuration
```python
# Update system configuration
scheduler.update_configuration({
    "auto_optimize_schedule": True,
    "enable_waitlist_auto_fill": True,
    "max_waitlist_size": 150,
    "contact_retry_attempts": 5
})
```

## 📈 Integration with Hospital Systems

### Backend API Integration
The system provides structured output that can be easily integrated with your existing hospital systems:

```python
# Get structured output for backend integration
result = scheduler.schedule_appointment(patient_data, appointment_request)

# Result contains all necessary information for:
# - Patient notifications
# - Doctor calendar updates
# - Resource allocation
# - Dashboard updates
```

### Data Export
```python
# Export schedule and waitlist data
json_data = scheduler.export_schedule_data("json")
csv_data = scheduler.export_schedule_data("csv")

# Export specific components
slot_stats = scheduler.slot_optimizer.get_slot_statistics()
waitlist_stats = scheduler.waitlist_manager.get_waitlist_statistics()
```

## 🧪 Testing and Validation

### Test Scripts
- **`test_ai_scheduler.py`**: Comprehensive test suite demonstrating all features
- **Mock ML Model**: Simulated predictions for testing without real models
- **Sample Data**: Realistic patient and appointment data for testing

### Running Tests
```bash
# Run all tests
python test_ai_scheduler.py

# Test specific modules
python -c "
from hospital_ai_scheduler.risk_assessor import RiskAssessor
assessor = RiskAssessor()
print(assessor.assess_risk(0.5))
"
```

## 📋 Requirements

### Core Dependencies
- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.21.0
- scikit-learn >= 1.1.0
- joblib >= 1.2.0

### Optional Dependencies
- matplotlib, seaborn (for visualization)
- fastapi, uvicorn (for web API)
- sqlalchemy (for database integration)
- pytest (for testing)

## 🔄 Workflow Examples

### Example 1: Low-Risk Patient
```python
# Patient with 20% no-show probability
patient_data = {"age": 65, "no_shows_history": 0, "sms_received": 1}
appointment_request = {"patient_id": "P001", "urgency_score": 1}

result = scheduler.schedule_appointment(patient_data, appointment_request)
# Result: Direct confirmation with standard scheduling
```

### Example 2: High-Risk Patient
```python
# Patient with 80% no-show probability
patient_data = {"age": 25, "no_shows_history": 3, "sms_received": 0}
appointment_request = {"patient_id": "P002", "urgency_score": 4}

result = scheduler.schedule_appointment(patient_data, appointment_request)
# Result: Waitlist placement with high priority and intensive follow-up
```

### Example 3: Slot Optimization
```python
# Add doctor schedules
scheduler.slot_optimizer.add_doctor_schedule(
    doctor_id="DR001",
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=30),
    working_hours=(9, 17),
    slot_duration=30
)

# Find optimal slot
optimal_slot = scheduler.slot_optimizer.find_optimal_slot(
    patient_id="P003",
    preferred_doctor="DR001",
    preferred_time="morning"
)
```

## 🚨 Error Handling

The system includes comprehensive error handling:

```python
try:
    result = scheduler.schedule_appointment(patient_data, appointment_request)
    if result["success"]:
        print(f"Appointment scheduled: {result['action']}")
    else:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"System error: {e}")
```

## 📊 Monitoring and Analytics

### System Status
```python
# Get comprehensive system status
status = scheduler.get_system_status()
print(f"ML Model: {status['ml_model']['model_type']}")
print(f"Slot Utilization: {status['slot_statistics']['utilization_rate']}%")
print(f"Waitlist Size: {status['waitlist_statistics']['total_patients']}")
```

### Performance Metrics
- **No-show Rate Reduction**: Target 20-30% decrease
- **Slot Utilization**: Target 85-90% efficiency
- **System Response Time**: <2 seconds for scheduling decisions
- **ML Model Accuracy**: Continuous monitoring and improvement

## 🔮 Future Enhancements

### Planned Features
- **Real-time ML Model Updates**: Continuous learning from appointment outcomes
- **Advanced Analytics Dashboard**: Comprehensive reporting and insights
- **Multi-hospital Support**: Scalable architecture for hospital networks
- **Mobile App Integration**: Patient-facing appointment management
- **Predictive Analytics**: Advanced forecasting and capacity planning

### Customization Options
- **Custom Risk Models**: Integration with hospital-specific risk factors
- **Specialty-specific Rules**: Different strategies for different medical specialties
- **Multi-language Support**: International hospital support
- **API Rate Limiting**: Enterprise-grade API management

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd hospital-ai-scheduler
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v

# Code formatting
black hospital_ai_scheduler/
flake8 hospital_ai_scheduler/
```

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Write unit tests for all new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
1. **ML Model Loading**: Ensure your model file path is correct and accessible
2. **Feature Mismatch**: Verify that patient data matches your model's expected features
3. **Memory Issues**: Large schedules may require additional memory allocation

### Getting Help
- Check the test scripts for usage examples
- Review the comprehensive docstrings in each module
- Open an issue for bugs or feature requests
- Contact the development team for enterprise support

## 🏆 Success Stories

### Expected Outcomes
- **20-30% reduction** in patient no-shows
- **85-90% slot utilization** efficiency
- **Improved patient satisfaction** through better scheduling
- **Reduced administrative overhead** through automation
- **Better resource allocation** and cost savings

---

**Ready to revolutionize your hospital's appointment scheduling?** 

Get started with the AI Agent today and experience the power of ML-driven healthcare optimization!

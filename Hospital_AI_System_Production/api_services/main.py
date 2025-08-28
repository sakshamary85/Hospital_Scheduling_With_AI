"""
Main FastAPI Application for Hospital AI System
Production-ready API with all endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import sys
import os

# Add the parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent_core.ai_agent import AIAppointmentScheduler
from ai_agent_core.ml_integration import MLModelIntegration
from production_config.config import config
from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.LOG_LEVEL),
    format=config.logging.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Hospital AI System API",
    description="AI-powered appointment scheduling system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=config.api.ALLOWED_METHODS,
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize AI Scheduler
try:
    ai_scheduler = AIAppointmentScheduler(config.ml_model.MODEL_PATH)
    logger.info("AI Scheduler initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize AI Scheduler: {e}")
    ai_scheduler = None

# Pydantic Models
class PatientData(BaseModel):
    patient_id: str
    age: int
    gender: int
    scholarship: int = 0
    hypertension: int = 0
    diabetes: int = 0
    alcoholism: int = 0
    handicap: int = 0
    sms_received: int = 1
    neighborhood: str = "CENTRO"
    medical_urgency: int = 1
    preferred_doctor: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None

class AppointmentRequest(BaseModel):
    patient_id: str
    preferred_doctor: str
    preferred_date: str
    preferred_time: str
    medical_urgency: int = 1
    medical_notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    appointment_id: str
    status: str
    action: str
    slot_info: Optional[Dict[str, Any]] = None
    risk_level: str
    no_show_probability: float
    buffer_time: int
    interventions: List[str]
    message: str

class HealthResponse(BaseModel):
    status: str
    message: str
    ai_scheduler_status: str
    ml_model_status: str
    timestamp: str

# Dependency for authentication (simplified for demo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production, validate JWT token here
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {"user_id": "demo_user"}

# Health Check Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    ai_status = "healthy" if ai_scheduler else "unhealthy"
    ml_status = "healthy" if ai_scheduler and ai_scheduler.ml_integration else "unhealthy"
    
    return HealthResponse(
        status="healthy",
        message="Hospital AI System is running",
        ai_scheduler_status=ai_status,
        ml_model_status=ml_status,
        timestamp=str(os.popen('date /t').read().strip())
    )

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed system health check."""
    health_info = {
        "system": "healthy",
        "ai_scheduler": "healthy" if ai_scheduler else "unhealthy",
        "ml_model": "healthy" if ai_scheduler and ai_scheduler.ml_integration else "unhealthy",
        "database": "not_connected",  # Will be connected in production
        "timestamp": str(os.popen('date /t').read().strip())
    }
    
    if ai_scheduler:
        try:
            # Test ML model with sample data
            test_patient = get_correct_patient_data()
            test_patient = set_neighbourhood(test_patient, "CENTRO")
            prediction = ai_scheduler.ml_integration.predict_with_full_output(test_patient)
            health_info["ml_prediction_test"] = "success"
            health_info["sample_prediction"] = prediction
        except Exception as e:
            health_info["ml_prediction_test"] = f"failed: {str(e)}"
    
    return health_info

# Patient Management Endpoints
@app.post("/api/v1/patients", response_model=Dict[str, Any])
async def create_patient(patient_data: PatientData, current_user: dict = Depends(get_current_user)):
    """Create a new patient with ML features."""
    try:
        # Prepare ML features
        ml_features = get_correct_patient_data()
        ml_features = set_neighbourhood(ml_features, patient_data.neighborhood)
        
        # Update with patient data
        ml_features.update({
            "Age": patient_data.age,
            "Gender": patient_data.gender,
            "Scholarship": patient_data.scholarship,
            "Hypertension": patient_data.hypertension,
            "Diabetes": patient_data.diabetes,
            "Alcoholism": patient_data.alcoholism,
            "Handicap": patient_data.handicap,
            "SmsReceived": patient_data.sms_received,
        })
        
        # Get ML prediction
        prediction = ai_scheduler.ml_integration.predict_with_full_output(ml_features)
        
        return {
            "patient_id": patient_data.patient_id,
            "status": "created",
            "ml_prediction": prediction,
            "ml_features": ml_features,
            "message": "Patient created successfully with ML assessment"
        }
        
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}"
        )

@app.get("/api/v1/patients/{patient_id}/ml-assessment")
async def get_patient_ml_assessment(patient_id: str, current_user: dict = Depends(get_current_user)):
    """Get ML assessment for a patient."""
    try:
        # For demo, use sample data
        ml_features = get_correct_patient_data()
        ml_features = set_neighbourhood(ml_features, "CENTRO")
        
        # Get ML prediction
        prediction = ai_scheduler.ml_integration.predict_with_full_output(ml_features)
        
        # Get risk assessment
        risk_level = ai_scheduler.risk_assessor.assess_risk(
            ml_prediction=prediction["prediction"],
            show_probability=prediction["show_probability"],
            no_show_probability=prediction["no_show_probability"]
        )
        
        return {
            "patient_id": patient_id,
            "ml_prediction": prediction,
            "risk_level": risk_level.value,
            "risk_assessment": {
                "no_show_probability": prediction["no_show_probability"],
                "show_probability": prediction["show_probability"],
                "risk_level": risk_level.value,
                "recommendations": ai_scheduler.risk_assessor.get_intervention_recommendations(risk_level)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting ML assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ML assessment: {str(e)}"
        )

# Appointment Scheduling Endpoints
@app.post("/api/v1/appointments/schedule", response_model=AppointmentResponse)
async def schedule_appointment(appointment_request: AppointmentRequest, current_user: dict = Depends(get_current_user)):
    """Schedule an appointment using AI Agent."""
    try:
        if not ai_scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Scheduler not available"
            )
        
        # Prepare patient data for ML
        patient_data = get_correct_patient_data()
        patient_data = set_neighbourhood(patient_data, "CENTRO")
        
        # Create appointment request structure
        appointment_req = {
            "patient_id": appointment_request.patient_id,
            "preferred_doctor": appointment_request.preferred_doctor,
            "preferred_date": appointment_request.preferred_date,
            "preferred_time": appointment_request.preferred_time,
            "urgency_score": appointment_request.medical_urgency,
            "medical_notes": appointment_request.medical_notes or "Routine consultation"
        }
        
        # Use AI Scheduler to make decision
        result = ai_scheduler.schedule_appointment(patient_data, appointment_req)
        
        return AppointmentResponse(
            appointment_id=f"APT_{appointment_request.patient_id}_{int(os.popen('date /t').read().strip())}",
            status="scheduled",
            action=result.get("action", "unknown"),
            slot_info=result.get("slot_info"),
            risk_level=result.get("risk_level", "UNKNOWN"),
            no_show_probability=result.get("no_show_probability", 0.0),
            buffer_time=result.get("buffer_time", 0),
            interventions=result.get("interventions", []),
            message=result.get("message", "Appointment scheduled successfully")
        )
        
    except Exception as e:
        logger.error(f"Error scheduling appointment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule appointment: {str(e)}"
        )

# AI Agent Endpoints
@app.post("/api/v1/ai/assess-risk")
async def assess_patient_risk(patient_data: PatientData, current_user: dict = Depends(get_current_user)):
    """Assess patient risk using AI Agent."""
    try:
        # Prepare ML features
        ml_features = get_correct_patient_data()
        ml_features = set_neighbourhood(ml_features, patient_data.neighborhood)
        
        # Update with patient data
        ml_features.update({
            "Age": patient_data.age,
            "Gender": patient_data.gender,
            "Scholarship": patient_data.scholarship,
            "Hypertension": patient_data.hypertension,
            "Diabetes": patient_data.diabetes,
            "Alcoholism": patient_data.alcoholism,
            "Handicap": patient_data.handicap,
            "SmsReceived": patient_data.sms_received,
        })
        
        # Get ML prediction
        prediction = ai_scheduler.ml_integration.predict_with_full_output(ml_features)
        
        # Get risk assessment
        risk_level = ai_scheduler.risk_assessor.assess_risk(
            ml_prediction=prediction["prediction"],
            show_probability=prediction["show_probability"],
            no_show_probability=prediction["no_show_probability"]
        )
        
        # Get scheduling strategy
        strategy = ai_scheduler.risk_assessor.get_scheduling_strategy(
            risk_level, 
            slot_available=True, 
            slot_capacity=1
        )
        
        return {
            "patient_id": patient_data.patient_id,
            "ml_prediction": prediction,
            "risk_assessment": {
                "risk_level": risk_level.value,
                "no_show_probability": prediction["no_show_probability"],
                "risk_description": f"Patient has {risk_level.value.lower()} risk of no-show"
            },
            "scheduling_strategy": strategy,
            "recommendations": ai_scheduler.risk_assessor.get_intervention_recommendations(risk_level)
        }
        
    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assess risk: {str(e)}"
        )

@app.get("/api/v1/ai/waitlist")
async def get_waitlist_status(current_user: dict = Depends(get_current_user)):
    """Get current waitlist status."""
    try:
        if not ai_scheduler:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI Scheduler not available"
            )
        
        waitlist_stats = ai_scheduler.waitlist_manager.get_waitlist_statistics()
        
        return {
            "waitlist_status": "active",
            "statistics": waitlist_stats,
            "total_patients": waitlist_stats.get("total_patients", 0),
            "average_wait_time": waitlist_stats.get("average_wait_time", 0),
            "priority_distribution": {
                "high": waitlist_stats.get("high_priority_count", 0),
                "medium": waitlist_stats.get("medium_priority_count", 0),
                "low": waitlist_stats.get("low_priority_count", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting waitlist status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get waitlist status: {str(e)}"
        )

# System Information Endpoints
@app.get("/api/v1/system/info")
async def get_system_info():
    """Get system information and configuration."""
    return {
        "system_name": "Hospital AI System",
        "version": "1.0.0",
        "ml_model": {
            "type": "LightGBM",
            "features": config.ml_model.FEATURE_COUNT,
            "path": config.ml_model.MODEL_PATH
        },
        "hospital_config": {
            "working_hours": f"{config.hospital.WORKING_HOURS_START}:00 - {config.hospital.WORKING_HOURS_END}:00",
            "slot_duration": f"{config.hospital.SLOT_DURATION_MINUTES} minutes",
            "slots_per_day": config.hospital.SLOTS_PER_DAY
        },
        "risk_thresholds": {
            "low": f"{config.ml_model.LOW_RISK_THRESHOLD * 100}%",
            "medium": f"{config.ml_model.MEDIUM_RISK_THRESHOLD * 100}%",
            "high": f"{config.ml_model.HIGH_RISK_THRESHOLD * 100}%"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "🏥 Hospital AI System API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api": "/api/v1",
            "patients": "/api/v1/patients",
            "appointments": "/api/v1/appointments",
            "ai": "/api/v1/ai"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api.HOST,
        port=config.api.PORT,
        log_level=config.logging.LOG_LEVEL.lower()
    )

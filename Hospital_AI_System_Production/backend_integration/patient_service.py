"""
Patient Service for Backend Integration
Handles patient data retrieval and ML feature preparation
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from database_models.models import (
    Patient, Doctor, Appointment, PatientMedicalHistory, 
    TimeSlot, DoctorSchedule, GenderEnum, RiskLevelEnum
)

logger = logging.getLogger(__name__)


class PatientService:
    """Service for patient-related operations."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_patient_data(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete patient data for ML model input.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Dictionary with patient data and ML features
        """
        try:
            # Get patient basic information
            patient = self.db.query(Patient).filter(
                Patient.patient_id == patient_id
            ).first()
            
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                return None
            
            # Get patient medical history
            medical_history = self.db.query(PatientMedicalHistory).filter(
                PatientMedicalHistory.patient_id == patient.id
            ).first()
            
            # Get recent appointments for statistics
            recent_appointments = self.db.query(Appointment).filter(
                Appointment.patient_id == patient.id
            ).order_by(Appointment.created_at.desc()).limit(10).all()
            
            # Calculate ML features
            ml_features = self._prepare_ml_features(
                patient, medical_history, recent_appointments
            )
            
            logger.info(f"Patient data retrieved successfully: {patient_id}")
            return ml_features
            
        except Exception as e:
            logger.error(f"Error retrieving patient data: {e}")
            raise
    
    def _prepare_ml_features(self, 
                            patient: Patient, 
                            medical_history: PatientMedicalHistory,
                            recent_appointments: List[Appointment]) -> Dict[str, Any]:
        """
        Prepare ML model input features from patient data.
        
        Args:
            patient: Patient entity
            medical_history: Patient medical history
            recent_appointments: Recent appointments
            
        Returns:
            Dictionary with 98 ML features
        """
        # Basic features (17)
        features = {
            "Gender": patient.gender.value,
            "Age": patient.age or 0,
            "Scholarship": 1 if patient.scholarship else 0,
            "Hypertension": 1 if patient.hypertension else 0,
            "Diabetes": 1 if patient.diabetes else 0,
            "Alcoholism": 1 if patient.alcoholism else 0,
            "Handicap": 1 if patient.handicap else 0,
            "SmsReceived": 1 if patient.sms_enabled else 0,
        }
        
        # Historical features
        if medical_history:
            features.update({
                "NoShowRate": medical_history.no_show_rate or 0.0,
                "LastShowStatus": 1 if medical_history.last_show_status else 0,
                "AppointmentCount": medical_history.appointment_count or 0,
                "LastAppointmentDays": medical_history.last_appointment_days or 0,
            })
        else:
            features.update({
                "NoShowRate": 0.0,
                "LastShowStatus": 1,
                "AppointmentCount": 0,
                "LastAppointmentDays": 0,
            })
        
        # Neighborhood features (81) - one-hot encoded
        neighborhood_features = self._get_neighborhood_features(patient.neighborhood)
        features.update(neighborhood_features)
        
        # Appointment-specific features (will be filled by appointment service)
        features.update({
            "LeadDays": 0,  # Will be calculated
            "ScheduledDayOfWeek": 0,  # Will be calculated
            "ScheduledDayDay": 0,  # Will be calculated
            "AppointmentDayDay": 0,  # Will be calculated
            "AppointmentDayOfWeek": 0,  # Will be calculated
        })
        
        return features
    
    def _get_neighborhood_features(self, neighborhood: str) -> Dict[str, int]:
        """
        Get one-hot encoded neighborhood features.
        
        Args:
            neighborhood: Patient's neighborhood
            
        Returns:
            Dictionary with 81 neighborhood features
        """
        # All possible neighborhoods
        all_neighborhoods = [
            "AEROPORTO", "ANDORINHAS", "ANTNIO_HONRIO", "ARIOVALDO_FAVALESSA",
            "BARRO_VERMELHO", "BELA_VISTA", "BENTO_FERREIRA", "BOA_VISTA",
            "BONFIM", "CARATORA", "CENTRO", "COMDUSA", "CONQUISTA",
            "CONSOLAO", "CRUZAMENTO", "DA_PENHA", "DE_LOURDES",
            "DO_CABRAL", "DO_MOSCOSO", "DO_QUADRO", "ENSEADA_DO_SU",
            "ESTRELINHA", "FONTE_GRANDE", "FORTE_SO_JOO", "FRADINHOS",
            "GOIABEIRAS", "GRANDE_VITRIA", "GURIGICA", "HORTO",
            "ILHA_DAS_CAIEIRAS", "ILHA_DE_SANTA_MARIA", "ILHA_DO_BOI",
            "ILHA_DO_FRADE", "ILHA_DO_PRNCIPE", "ILHAS_OCENICAS_DE_TRINDADE",
            "INHANGUET", "ITARAR", "JABOUR", "JARDIM_CAMBURI",
            "JARDIM_DA_PENHA", "JESUS_DE_NAZARETH", "JOANA_DARC", "JUCUTUQUARA",
            "MARIA_ORTIZ", "MARUPE", "MATA_DA_PRAIA", "MONTE_BELO",
            "MORADA_DE_CAMBURI", "MRIO_CYPRESTE", "NAZARETH", "NOVA_PALESTINA",
            "PARQUE_INDUSTRIAL", "PARQUE_MOSCOSO", "PIEDADE", "PONTAL_DE_CAMBURI",
            "PRAIA_DO_CANTO", "PRAIA_DO_SU", "REDENO", "REPBLICA",
            "RESISTNCIA", "ROMO", "SANTA_CECLIA", "SANTA_CLARA",
            "SANTA_HELENA", "SANTA_LUZA", "SANTA_LCIA", "SANTA_MARTHA",
            "SANTA_TEREZA", "SANTO_ANDR", "SANTO_ANTNIO", "SANTOS_DUMONT",
            "SANTOS_REIS", "SEGURANA_DO_LAR", "SOLON_BORGES", "SO_BENEDITO",
            "SO_CRISTVO", "SO_JOS", "SO_PEDRO", "TABUAZEIRO",
            "UNIVERSITRIO", "VILA_RUBIM"
        ]
        
        # Initialize all neighborhoods to 0
        features = {f"Neighbourhood_{n}": 0 for n in all_neighborhoods}
        
        # Set patient's neighborhood to 1
        if neighborhood:
            neighborhood_key = f"Neighbourhood_{neighborhood.upper()}"
            if neighborhood_key in features:
                features[neighborhood_key] = 1
        
        return features
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Get patient's appointment history.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            List of appointment dictionaries
        """
        try:
            appointments = self.db.query(Appointment).filter(
                Appointment.patient_id == patient_id
            ).order_by(Appointment.appointment_date.desc()).all()
            
            return [
                {
                    "appointment_id": apt.appointment_id,
                    "appointment_date": apt.appointment_date,
                    "status": apt.status.value,
                    "doctor_id": apt.doctor_id,
                    "no_show_probability": apt.no_show_probability,
                    "risk_level": apt.risk_level.value if apt.risk_level else None,
                }
                for apt in appointments
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving patient appointments: {e}")
            raise
    
    def update_patient_medical_history(self, 
                                     patient_id: str, 
                                     appointment_status: str,
                                     no_show: bool) -> bool:
        """
        Update patient's medical history after appointment.
        
        Args:
            patient_id: Patient identifier
            appointment_status: Appointment status
            no_show: Whether patient showed up
            
        Returns:
            True if updated successfully
        """
        try:
            # Get or create medical history
            medical_history = self.db.query(PatientMedicalHistory).filter(
                PatientMedicalHistory.patient_id == patient_id
            ).first()
            
            if not medical_history:
                # Create new medical history
                patient = self.db.query(Patient).filter(
                    Patient.patient_id == patient_id
                ).first()
                
                if not patient:
                    return False
                
                medical_history = PatientMedicalHistory(
                    patient_id=patient.id,
                    no_show_rate=0.0,
                    last_show_status=True,
                    appointment_count=0,
                    last_appointment_days=0
                )
                self.db.add(medical_history)
            
            # Update statistics
            medical_history.appointment_count += 1
            medical_history.last_show_status = not no_show
            medical_history.last_appointment_days = 0
            
            # Calculate no-show rate
            total_appointments = medical_history.appointment_count
            if no_show:
                no_show_count = self.db.query(Appointment).filter(
                    and_(
                        Appointment.patient_id == patient_id,
                        Appointment.status == "NO_SHOW"
                    )
                ).count()
                medical_history.no_show_rate = no_show_count / total_appointments
            
            self.db.commit()
            logger.info(f"Patient medical history updated: {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating patient medical history: {e}")
            self.db.rollback()
            return False
    
    def get_patient_statistics(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient statistics for dashboard.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Dictionary with patient statistics
        """
        try:
            # Get patient
            patient = self.db.query(Patient).filter(
                Patient.patient_id == patient_id
            ).first()
            
            if not patient:
                return {}
            
            # Get appointment statistics
            total_appointments = self.db.query(Appointment).filter(
                Appointment.patient_id == patient.id
            ).count()
            
            completed_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.patient_id == patient.id,
                    Appointment.status == "COMPLETED"
                )
            ).count()
            
            no_show_appointments = self.db.query(Appointment).filter(
                and_(
                    Appointment.patient_id == patient.id,
                    Appointment.status == "NO_SHOW"
                )
            ).count()
            
            # Calculate percentages
            completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
            no_show_rate = (no_show_appointments / total_appointments * 100) if total_appointments > 0 else 0
            
            return {
                "patient_id": patient_id,
                "total_appointments": total_appointments,
                "completed_appointments": completed_appointments,
                "no_show_appointments": no_show_appointments,
                "completion_rate": round(completion_rate, 2),
                "no_show_rate": round(no_show_rate, 2),
                "last_appointment": self._get_last_appointment_date(patient.id),
                "next_appointment": self._get_next_appointment_date(patient.id),
            }
            
        except Exception as e:
            logger.error(f"Error retrieving patient statistics: {e}")
            return {}
    
    def _get_last_appointment_date(self, patient_id: int) -> Optional[str]:
        """Get last appointment date."""
        last_apt = self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(Appointment.appointment_date.desc()).first()
        
        return last_apt.appointment_date.isoformat() if last_apt else None
    
    def _get_next_appointment_date(self, patient_id: int) -> Optional[str]:
        """Get next appointment date."""
        next_apt = self.db.query(Appointment).filter(
            and_(
                Appointment.patient_id == patient_id,
                Appointment.appointment_date >= datetime.now(),
                Appointment.status.in_(["SCHEDULED", "CONFIRMED"])
            )
        ).order_by(Appointment.appointment_date.asc()).first()
        
        return next_apt.appointment_date.isoformat() if next_apt else None

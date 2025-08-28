"""
AI Appointment Scheduler - Main Module

Main AI Agent that orchestrates ML model integration, risk assessment,
slot optimization, and waitlist management for hospital appointments.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import json

from .ml_integration import MLModelIntegration
from .risk_assessor import RiskAssessor, RiskLevel
from .slot_optimizer import SlotOptimizer, DoctorSlot
from .waitlist_manager import WaitlistManager

logger = logging.getLogger(__name__)


class AIAppointmentScheduler:
    """
    Main AI Agent for hospital appointment scheduling.
    
    This class orchestrates:
    - ML model inference for no-show prediction
    - Risk assessment and scheduling strategy determination
    - Slot optimization and appointment scheduling
    - Waitlist management for high-risk patients
    - Integration with hospital backend systems
    """
    
    def __init__(self, 
                 model_path: str,
                 scaler_path: Optional[str] = None,
                 risk_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize the AI Appointment Scheduler.
        
        Args:
            model_path: Path to the trained ML model
            scaler_path: Path to the fitted scaler (optional)
            risk_thresholds: Custom risk thresholds (optional)
        """
        # Initialize components
        self.ml_integration = MLModelIntegration(model_path, scaler_path)
        self.risk_assessor = RiskAssessor(**risk_thresholds) if risk_thresholds else RiskAssessor()
        self.slot_optimizer = SlotOptimizer()
        self.waitlist_manager = WaitlistManager()
        
        # Configuration
        self.config = {
            "auto_optimize_schedule": True,
            "enable_waitlist_auto_fill": True,
            "max_waitlist_size": 100,
            "contact_retry_attempts": 3
        }
        
        logger.info("AI Appointment Scheduler initialized successfully")
    
    def schedule_appointment(self, 
                           patient_data: Dict[str, Any],
                           appointment_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to schedule an appointment using AI-driven decision making.
        
        Args:
            patient_data: Patient information and features for ML model
            appointment_request: Appointment preferences and constraints
            
        Returns:
            Dictionary containing scheduling decision and details
        """
        try:
            # Step 1: Get ML prediction
            no_show_probability = self.ml_integration.predict_no_show_probability(patient_data)
            
            # Step 1.5: Get full ML prediction output for detailed analysis
            full_prediction = self.ml_integration.predict_with_full_output(patient_data)
            
            # Step 2: Assess risk level
            risk_level = self.risk_assessor.assess_risk(no_show_probability)
            
            # Step 3: Check slot availability
            slot_available, optimal_slot = self._check_slot_availability(appointment_request)
            
            # Step 4: Determine scheduling strategy
            strategy = self.risk_assessor.get_scheduling_strategy(
                risk_level, slot_available, 
                optimal_slot.get_available_capacity() if optimal_slot else 0
            )
            
            # Step 5: Execute scheduling decision
            result = self._execute_scheduling_decision(
                patient_data, appointment_request, strategy, optimal_slot, no_show_probability
            )
            
            # Step 5.5: Add ML prediction details to result
            result.update({
                "ml_prediction": full_prediction["prediction"],
                "no_show_probability": full_prediction["no_show_probability"],
                "show_probability": full_prediction["show_probability"],
                "risk_level": risk_level.value
            })
            
            # Step 6: Update waitlist if needed
            if result["action"] == "waitlist":
                self._add_to_waitlist(patient_data, appointment_request, no_show_probability)
            
            # Step 7: Optimize schedule if enabled
            if self.config["auto_optimize_schedule"]:
                self.slot_optimizer.optimize_schedule()
            
            return result
            
        except Exception as e:
            logger.error(f"Appointment scheduling failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "error",
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_slot_availability(self, appointment_request: Dict[str, Any]) -> Tuple[bool, Optional[DoctorSlot]]:
        """Check if requested slot is available and find optimal alternatives."""
        preferred_doctor = appointment_request.get("preferred_doctor")
        preferred_date = appointment_request.get("preferred_date")
        preferred_time = appointment_request.get("preferred_time")
        
        # Check if preferred slot is available
        if preferred_doctor and preferred_date:
            available_slots = self.slot_optimizer.get_doctor_availability(
                preferred_doctor, preferred_date
            )
            if available_slots:
                return True, available_slots[0]
        
        # Find optimal alternative slot
        optimal_slot = self.slot_optimizer.find_optimal_slot(
            patient_id=appointment_request.get("patient_id", "unknown"),
            preferred_doctor=preferred_doctor,
            preferred_date=preferred_date,
            preferred_time=preferred_time
        )
        
        return False, optimal_slot
    
    def _execute_scheduling_decision(self, 
                                   patient_data: Dict[str, Any],
                                   appointment_request: Dict[str, Any],
                                   strategy: Dict[str, Any],
                                   optimal_slot: Optional[DoctorSlot],
                                   no_show_probability: float) -> Dict[str, Any]:
        """Execute the determined scheduling strategy."""
        patient_id = appointment_request.get("patient_id", "unknown")
        action = strategy["action"]
        
        result = {
            "success": True,
            "patient_id": patient_id,
            "action": action,
            "risk_level": strategy["risk_level"],
            "no_show_probability": no_show_probability,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }
        
        if action == "confirm":
            # Direct confirmation
            if optimal_slot:
                success = self.slot_optimizer.schedule_appointment(
                    patient_id, optimal_slot, strategy["buffer_time"]
                )
                if success:
                    result.update({
                        "slot_assigned": True,
                        "doctor_id": optimal_slot.doctor_id,
                        "start_time": optimal_slot.start_time.isoformat(),
                        "end_time": optimal_slot.end_time.isoformat(),
                        "buffer_time": strategy["buffer_time"]
                    })
                else:
                    result["success"] = False
                    result["error"] = "Failed to schedule appointment"
            else:
                result["success"] = False
                result["error"] = "No suitable slot available"
        
        elif action == "confirm_with_buffer":
            # Confirmation with buffer time
            if optimal_slot:
                success = self.slot_optimizer.schedule_appointment(
                    patient_id, optimal_slot, strategy["buffer_time"]
                )
                if success:
                    result.update({
                        "slot_assigned": True,
                        "doctor_id": optimal_slot.doctor_id,
                        "start_time": optimal_slot.start_time.isoformat(),
                        "end_time": optimal_slot.end_time.isoformat(),
                        "buffer_time": strategy["buffer_time"],
                        "requires_confirmation": strategy["requires_confirmation"]
                    })
                else:
                    result["success"] = False
                    result["error"] = "Failed to schedule appointment"
            else:
                result["success"] = False
                result["error"] = "No suitable slot available"
        
        elif action == "reschedule":
            # Reschedule to optimal time
            if optimal_slot:
                success = self.slot_optimizer.schedule_appointment(
                    patient_id, optimal_slot, strategy["buffer_time"]
                )
                if success:
                    result.update({
                        "slot_assigned": True,
                        "doctor_id": optimal_slot.doctor_id,
                        "start_time": optimal_slot.start_time.isoformat(),
                        "end_time": optimal_slot.end_time.isoformat(),
                        "rescheduled": True,
                        "original_preferences": {
                            "doctor": appointment_request.get("preferred_doctor"),
                            "date": appointment_request.get("preferred_date"),
                            "time": appointment_request.get("preferred_time")
                        }
                    })
                else:
                    result["success"] = False
                    result["error"] = "Failed to reschedule appointment"
            else:
                result["success"] = False
                result["error"] = "No alternative slot available"
        
        elif action == "waitlist":
            # Add to waitlist
            result.update({
                "slot_assigned": False,
                "waitlist_priority": strategy["waitlist_priority"],
                "estimated_wait_time": self._estimate_wait_time(strategy["waitlist_priority"])
            })
        
        else:
            result["success"] = False
            result["error"] = f"Unknown action: {action}"
        
        return result
    
    def _add_to_waitlist(self, 
                         patient_data: Dict[str, Any],
                         appointment_request: Dict[str, Any],
                         no_show_probability: float):
        """Add patient to waitlist with appropriate priority."""
        urgency_score = appointment_request.get("urgency_score", 1)
        preferred_doctor = appointment_request.get("preferred_doctor")
        preferred_date = appointment_request.get("preferred_date")
        medical_notes = appointment_request.get("medical_notes", "")
        
        self.waitlist_manager.add_patient(
            patient_id=appointment_request.get("patient_id", "unknown"),
            no_show_probability=no_show_probability,
            urgency_score=urgency_score,
            preferred_doctor=preferred_doctor,
            preferred_date=preferred_date,
            medical_notes=medical_notes
        )
    
    def _estimate_wait_time(self, priority_score: int) -> str:
        """Estimate wait time based on priority score."""
        if priority_score >= 8:
            return "1-2 days"
        elif priority_score >= 6:
            return "3-5 days"
        elif priority_score >= 4:
            return "1-2 weeks"
        else:
            return "2-4 weeks"
    
    def process_waitlist_fill(self) -> Dict[str, Any]:
        """Process waitlist to fill available slots automatically."""
        if not self.config["enable_waitlist_auto_fill"]:
            return {"success": False, "message": "Auto-fill disabled"}
        
        filled_slots = 0
        patients_contacted = 0
        
        # Get available slots
        for doctor_id, slots in self.slot_optimizer.doctor_slots.items():
            for slot in slots:
                if slot.is_available():
                    # Find optimal patient for this slot
                    optimal_patient = self.waitlist_manager.find_optimal_patient_for_slot(
                        slot, doctor_id, slot.start_time
                    )
                    
                    if optimal_patient:
                        # Schedule the patient
                        success = self.slot_optimizer.schedule_appointment(
                            optimal_patient.patient_id, slot
                        )
                        
                        if success:
                            # Remove from waitlist
                            self.waitlist_manager.remove_patient(optimal_patient.patient_id)
                            filled_slots += 1
                            
                            logger.info(f"Auto-filled slot for patient {optimal_patient.patient_id}")
        
        return {
            "success": True,
            "filled_slots": filled_slots,
            "patients_contacted": patients_contacted,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and statistics."""
        return {
            "ml_model": self.ml_integration.get_model_info(),
            "slot_statistics": self.slot_optimizer.get_slot_statistics(),
            "waitlist_statistics": self.waitlist_manager.get_waitlist_statistics(),
            "risk_thresholds": {
                "low": self.risk_assessor.low_threshold,
                "medium": self.risk_assessor.medium_threshold,
                "high": self.risk_assessor.high_threshold
            },
            "configuration": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """Update system configuration."""
        try:
            for key, value in new_config.items():
                if key in self.config:
                    self.config[key] = value
            
            logger.info(f"Configuration updated: {new_config}")
            return True
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return False
    
    def export_schedule_data(self, format_type: str = "json") -> str:
        """Export current schedule and waitlist data."""
        try:
            schedule_data = self.slot_optimizer.export_schedule(format_type)
            waitlist_data = self.waitlist_manager.export_waitlist(format_type)
            
            if format_type == "json":
                # Combine into single JSON
                combined_data = {
                    "schedule": json.loads(schedule_data),
                    "waitlist": json.loads(waitlist_data),
                    "export_timestamp": datetime.now().isoformat()
                }
                return json.dumps(combined_data, indent=2)
            else:
                # Return as separate CSV sections
                return f"=== SCHEDULE ===\n{schedule_data}\n\n=== WAITLIST ===\n{waitlist_data}"
                
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            return f"Export failed: {str(e)}"
    
    def handle_appointment_cancellation(self, patient_id: str) -> Dict[str, Any]:
        """Handle appointment cancellation and potential waitlist fill."""
        try:
            # Cancel the appointment
            success = self.slot_optimizer.cancel_appointment(patient_id)
            
            if success:
                # Try to fill the slot with waitlist patient
                slot_info = self._find_cancelled_slot_info(patient_id)
                if slot_info and self.config["enable_waitlist_auto_fill"]:
                    self._attempt_waitlist_fill_for_slot(slot_info)
                
                return {
                    "success": True,
                    "action": "cancelled",
                    "patient_id": patient_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Patient not found in schedule",
                    "patient_id": patient_id
                }
                
        except Exception as e:
            logger.error(f"Appointment cancellation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "patient_id": patient_id
            }
    
    def _find_cancelled_slot_info(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Find information about the slot that was cancelled."""
        # This would need to be implemented based on how you track cancelled slots
        # For now, return None
        return None
    
    def _attempt_waitlist_fill_for_slot(self, slot_info: Dict[str, Any]):
        """Attempt to fill a specific slot with a waitlist patient."""
        # Implementation would depend on slot_info structure
        pass
    
    def get_patient_recommendations(self, patient_id: str) -> Dict[str, Any]:
        """Get personalized recommendations for a patient."""
        try:
            # Get patient's current status
            if patient_id in self.slot_optimizer.slot_assignments:
                # Patient has confirmed appointment
                slot = self.slot_optimizer.slot_assignments[patient_id]
                return {
                    "status": "confirmed",
                    "appointment_time": slot.start_time.isoformat(),
                    "doctor_id": slot.doctor_id,
                    "recommendations": [
                        "Arrive 15 minutes early",
                        "Bring photo ID and insurance card",
                        "Complete pre-appointment forms online"
                    ]
                }
            elif patient_id in self.waitlist_manager.patient_records:
                # Patient is on waitlist
                entry = self.waitlist_manager.patient_records[patient_id]
                return {
                    "status": "waitlist",
                    "priority_score": entry.priority_score,
                    "estimated_wait_time": self._estimate_wait_time(entry.priority_score),
                    "recommendations": [
                        "Respond promptly to contact attempts",
                        "Consider alternative appointment times",
                        "Update contact information if needed"
                    ]
                }
            else:
                return {
                    "status": "not_found",
                    "recommendations": [
                        "Contact hospital to schedule appointment",
                        "Provide complete medical history",
                        "Specify preferred appointment times"
                    ]
                }
                
        except Exception as e:
            logger.error(f"Failed to get patient recommendations: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

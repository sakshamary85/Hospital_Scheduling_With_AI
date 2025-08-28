"""
Slot Optimization Module

Manages doctor availability and optimizes appointment scheduling
based on ML predictions and patient risk levels.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import logging
from .risk_assessor import RiskLevel

logger = logging.getLogger(__name__)


class DoctorSlot:
    """Represents a doctor's time slot with capacity and patient information."""
    
    def __init__(self, 
                 doctor_id: str,
                 start_time: datetime,
                 end_time: datetime,
                 max_capacity: int = 1,
                 slot_type: str = "consultation"):
        self.doctor_id = doctor_id
        self.start_time = start_time
        self.end_time = end_time
        self.max_capacity = max_capacity
        self.current_capacity = 0
        self.slot_type = slot_type
        self.patients = []
        self.buffer_time = 0
        
    def add_patient(self, patient_id: str, buffer_time: int = 0):
        """Add a patient to this slot."""
        if self.current_capacity < self.max_capacity:
            self.patients.append(patient_id)
            self.current_capacity += 1
            self.buffer_time = max(self.buffer_time, buffer_time)
            return True
        return False
    
    def remove_patient(self, patient_id: str):
        """Remove a patient from this slot."""
        if patient_id in self.patients:
            self.patients.remove(patient_id)
            self.current_capacity -= 1
            return True
        return False
    
    def is_available(self) -> bool:
        """Check if slot has available capacity."""
        return self.current_capacity < self.max_capacity
    
    def get_available_capacity(self) -> int:
        """Get remaining capacity."""
        return self.max_capacity - self.current_capacity
    
    def get_duration_minutes(self) -> int:
        """Get slot duration in minutes."""
        return int((self.end_time - self.start_time).total_seconds() / 60)


class SlotOptimizer:
    """
    Optimizes doctor slot allocation and appointment scheduling.
    
    This class:
    - Manages doctor availability and slot capacity
    - Finds optimal slots based on patient risk and preferences
    - Optimizes slot utilization and reduces conflicts
    """
    
    def __init__(self):
        """Initialize slot optimizer."""
        self.doctor_slots = {}  # doctor_id -> list of slots
        self.slot_assignments = {}  # patient_id -> slot_id
        self.waitlist = []
        
        logger.info("Slot optimizer initialized")
    
    def add_doctor_schedule(self, 
                           doctor_id: str,
                           start_date: datetime,
                           end_date: datetime,
                           working_hours: Tuple[int, int] = (9, 17),
                           slot_duration: int = 30,
                           max_capacity: int = 1):
        """
        Add doctor's working schedule.
        
        Args:
            doctor_id: Unique identifier for the doctor
            start_date: Start date for schedule
            end_date: End date for schedule
            working_hours: Tuple of (start_hour, end_hour) in 24h format
            slot_duration: Duration of each slot in minutes
            max_capacity: Maximum patients per slot
        """
        if doctor_id not in self.doctor_slots:
            self.doctor_slots[doctor_id] = []
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:
                start_time = current_date.replace(
                    hour=working_hours[0], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
                end_time = current_date.replace(
                    hour=working_hours[1], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
                
                # Create slots
                current_slot_start = start_time
                while current_slot_start < end_time:
                    current_slot_end = current_slot_start + timedelta(minutes=slot_duration)
                    slot = DoctorSlot(
                        doctor_id=doctor_id,
                        start_time=current_slot_start,
                        end_time=current_slot_end,
                        max_capacity=max_capacity
                    )
                    self.doctor_slots[doctor_id].append(slot)
                    current_slot_start = current_slot_end
            
            current_date += timedelta(days=1)
        
        logger.info(f"Added schedule for doctor {doctor_id}: "
                   f"{len(self.doctor_slots[doctor_id])} slots")
    
    def find_optimal_slot(self, 
                          patient_id: str,
                          preferred_doctor: Optional[str] = None,
                          preferred_date: Optional[datetime] = None,
                          preferred_time: Optional[str] = None,
                          risk_level: RiskLevel = RiskLevel.LOW,
                          urgency_score: int = 1) -> Optional[DoctorSlot]:
        """
        Find optimal slot for a patient based on preferences and risk level.
        
        Args:
            patient_id: Patient identifier
            preferred_doctor: Preferred doctor ID
            preferred_date: Preferred date
            preferred_time: Preferred time (e.g., "morning", "afternoon")
            risk_level: Patient's risk level
            urgency_score: Medical urgency (1-5)
            
        Returns:
            Optimal DoctorSlot or None if no suitable slot found
        """
        available_slots = []
        
        # Collect all available slots
        for doctor_id, slots in self.doctor_slots.items():
            if preferred_doctor and doctor_id != preferred_doctor:
                continue
                
            for slot in slots:
                if slot.is_available():
                    score = self._calculate_slot_score(
                        slot, preferred_date, preferred_time, risk_level, urgency_score
                    )
                    available_slots.append((slot, score))
        
        if not available_slots:
            return None
        
        # Sort by score (higher is better) and return best slot
        available_slots.sort(key=lambda x: x[1], reverse=True)
        return available_slots[0][0]
    
    def _calculate_slot_score(self, 
                             slot: DoctorSlot,
                             preferred_date: Optional[datetime],
                             preferred_time: Optional[str],
                             risk_level: RiskLevel,
                             urgency_score: int) -> float:
        """Calculate score for a slot based on patient preferences and risk."""
        score = 0.0
        
        # Date preference (closer to preferred date = higher score)
        if preferred_date:
            days_diff = abs((slot.start_time.date() - preferred_date.date()).days)
            score += max(0, 10 - days_diff)  # Max 10 points for same day
        
        # Time preference
        if preferred_time:
            hour = slot.start_time.hour
            if preferred_time == "morning" and 9 <= hour <= 12:
                score += 5
            elif preferred_time == "afternoon" and 13 <= hour <= 17:
                score += 5
            elif preferred_time == "evening" and 18 <= hour <= 20:
                score += 5
        
        # Risk-based scoring
        if risk_level == RiskLevel.HIGH:
            # High-risk patients prefer slots with more buffer time
            score += slot.buffer_time * 0.1
        elif risk_level == RiskLevel.MEDIUM:
            # Medium-risk patients prefer slots with some buffer
            score += slot.buffer_time * 0.05
        
        # Urgency scoring
        score += urgency_score * 2
        
        # Capacity preference (prefer slots with more available capacity)
        score += slot.get_available_capacity() * 0.5
        
        return score
    
    def schedule_appointment(self, 
                           patient_id: str,
                           slot: DoctorSlot,
                           buffer_time: int = 0) -> bool:
        """
        Schedule an appointment for a patient in a specific slot.
        
        Args:
            patient_id: Patient identifier
            slot: DoctorSlot to schedule in
            buffer_time: Additional buffer time needed
            
        Returns:
            True if successful, False otherwise
        """
        if slot.add_patient(patient_id, buffer_time):
            self.slot_assignments[patient_id] = slot
            logger.info(f"Scheduled patient {patient_id} in slot "
                       f"{slot.start_time} with doctor {slot.doctor_id}")
            return True
        return False
    
    def reschedule_appointment(self, 
                             patient_id: str,
                             new_slot: DoctorSlot,
                             buffer_time: int = 0) -> bool:
        """
        Reschedule an existing appointment.
        
        Args:
            patient_id: Patient identifier
            new_slot: New slot to schedule in
            buffer_time: Additional buffer time needed
            
        Returns:
            True if successful, False otherwise
        """
        # Remove from old slot
        if patient_id in self.slot_assignments:
            old_slot = self.slot_assignments[patient_id]
            old_slot.remove_patient(patient_id)
        
        # Schedule in new slot
        return self.schedule_appointment(patient_id, new_slot, buffer_time)
    
    def cancel_appointment(self, patient_id: str) -> bool:
        """
        Cancel an existing appointment.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            True if successful, False otherwise
        """
        if patient_id in self.slot_assignments:
            slot = self.slot_assignments[patient_id]
            slot.remove_patient(patient_id)
            del self.slot_assignments[patient_id]
            logger.info(f"Cancelled appointment for patient {patient_id}")
            return True
        return False
    
    def get_doctor_availability(self, 
                               doctor_id: str,
                               date: datetime) -> List[DoctorSlot]:
        """Get available slots for a specific doctor on a specific date."""
        if doctor_id not in self.doctor_slots:
            return []
        
        target_date = date.date()
        available_slots = []
        
        for slot in self.doctor_slots[doctor_id]:
            if slot.start_time.date() == target_date and slot.is_available():
                available_slots.append(slot)
        
        return available_slots
    
    def get_slot_statistics(self) -> Dict[str, Any]:
        """Get statistics about slot utilization."""
        total_slots = 0
        occupied_slots = 0
        total_capacity = 0
        used_capacity = 0
        
        for doctor_id, slots in self.doctor_slots.items():
            for slot in slots:
                total_slots += 1
                total_capacity += slot.max_capacity
                used_capacity += slot.current_capacity
                if slot.current_capacity > 0:
                    occupied_slots += 1
        
        utilization_rate = (used_capacity / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "total_slots": total_slots,
            "occupied_slots": occupied_slots,
            "total_capacity": total_capacity,
            "used_capacity": used_capacity,
            "utilization_rate": round(utilization_rate, 2),
            "available_capacity": total_capacity - used_capacity
        }
    
    def optimize_schedule(self) -> Dict[str, Any]:
        """
        Optimize the current schedule for better efficiency.
        
        Returns:
            Dictionary with optimization results
        """
        optimization_results = {
            "slots_optimized": 0,
            "capacity_improvement": 0,
            "conflicts_resolved": 0
        }
        
        # Simple optimization: try to consolidate low-utilization slots
        for doctor_id, slots in self.doctor_slots.items():
            for i, slot in enumerate(slots):
                if slot.current_capacity == 0 and i > 0:
                    # Check if we can merge with previous slot
                    prev_slot = slots[i-1]
                    if (prev_slot.end_time == slot.start_time and 
                        prev_slot.current_capacity < prev_slot.max_capacity):
                        # Merge slots
                        prev_slot.end_time = slot.end_time
                        prev_slot.max_capacity = min(prev_slot.max_capacity + 1, 3)
                        optimization_results["slots_optimized"] += 1
        
        logger.info(f"Schedule optimization completed: {optimization_results}")
        return optimization_results
    
    def export_schedule(self, format_type: str = "json") -> str:
        """
        Export the current schedule in specified format.
        
        Args:
            format_type: Export format ("json", "csv")
            
        Returns:
            Exported schedule data
        """
        schedule_data = {
            "doctor_slots": {},
            "patient_assignments": {},
            "statistics": self.get_slot_statistics()
        }
        
        # Export doctor slots
        for doctor_id, slots in self.doctor_slots.items():
            schedule_data["doctor_slots"][doctor_id] = []
            for slot in slots:
                slot_data = {
                    "start_time": slot.start_time.isoformat(),
                    "end_time": slot.end_time.isoformat(),
                    "current_capacity": slot.current_capacity,
                    "max_capacity": slot.max_capacity,
                    "patients": slot.patients,
                    "buffer_time": slot.buffer_time
                }
                schedule_data["doctor_slots"][doctor_id].append(slot_data)
        
        # Export patient assignments
        for patient_id, slot in self.slot_assignments.items():
            schedule_data["patient_assignments"][patient_id] = {
                "doctor_id": slot.doctor_id,
                "start_time": slot.start_time.isoformat(),
                "end_time": slot.end_time.isoformat()
            }
        
        if format_type == "csv":
            # Convert to CSV format
            return self._convert_to_csv(schedule_data)
        else:
            # Return as JSON string
            import json
            return json.dumps(schedule_data, indent=2)
    
    def _convert_to_csv(self, schedule_data: Dict[str, Any]) -> str:
        """Convert schedule data to CSV format."""
        import io
        
        output = io.StringIO()
        
        # Write header
        output.write("Patient ID,Doctor ID,Start Time,End Time,Status\n")
        
        # Write patient assignments
        for patient_id, assignment in schedule_data["patient_assignments"].items():
            output.write(f"{patient_id},{assignment['doctor_id']},"
                        f"{assignment['start_time']},{assignment['end_time']},"
                        f"Confirmed\n")
        
        return output.getvalue()

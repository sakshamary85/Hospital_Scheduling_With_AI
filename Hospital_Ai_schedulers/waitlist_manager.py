"""
Waitlist Management Module

Manages high-risk patients and priority-based scheduling when slots
become available, integrating with ML predictions and risk assessment.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import heapq
import logging
from .risk_assessor import RiskLevel, RiskAssessor

logger = logging.getLogger(__name__)


class WaitlistEntry:
    """Represents a patient on the waitlist with priority scoring."""
    
    def __init__(self, 
                 patient_id: str,
                 no_show_probability: float,
                 urgency_score: int,
                 entry_date: datetime,
                 preferred_doctor: Optional[str] = None,
                 preferred_date: Optional[datetime] = None,
                 medical_notes: str = ""):
        self.patient_id = patient_id
        self.no_show_probability = no_show_probability
        self.urgency_score = urgency_score
        self.entry_date = entry_date
        self.preferred_doctor = preferred_doctor
        self.preferred_date = preferred_date
        self.medical_notes = medical_notes
        self.waiting_days = 0
        self.last_contact_date = entry_date
        self.contact_attempts = 0
        self.priority_score = 0
        
        # Calculate initial priority score
        self._calculate_priority_score()
    
    def _calculate_priority_score(self):
        """Calculate priority score based on risk, urgency, and waiting time."""
        # Base priority from risk level (higher risk = higher priority for intervention)
        risk_assessor = RiskAssessor()
        risk_level = risk_assessor.assess_risk(self.no_show_probability)
        
        risk_priority = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 5
        }
        
        base_priority = risk_priority[risk_level]
        
        # Adjust for urgency (1-5 scale)
        urgency_multiplier = self.urgency_score / 5.0
        
        # Adjust for waiting time (diminishing returns after 7 days)
        waiting_bonus = min(self.waiting_days, 7) * 0.5
        
        # Risk-based adjustment (high-risk patients get priority for intervention)
        if risk_level == RiskLevel.HIGH:
            risk_bonus = 2.0
        elif risk_level == RiskLevel.MEDIUM:
            risk_bonus = 1.0
        else:
            risk_bonus = 0.0
        
        self.priority_score = int(base_priority * urgency_multiplier + waiting_bonus + risk_bonus)
        self.priority_score = max(1, min(self.priority_score, 10))  # Clamp between 1-10
    
    def update_waiting_time(self):
        """Update waiting time and recalculate priority score."""
        self.waiting_days = (datetime.now() - self.entry_date).days
        self._calculate_priority_score()
    
    def record_contact_attempt(self):
        """Record a contact attempt."""
        self.last_contact_date = datetime.now()
        self.contact_attempts += 1
    
    def __lt__(self, other):
        """Comparison for priority queue (higher priority first)."""
        return self.priority_score > other.priority_score
    
    def __eq__(self, other):
        """Equality comparison."""
        return self.priority_score == other.priority_score
    
    def __repr__(self):
        return (f"WaitlistEntry(patient_id={self.patient_id}, "
                f"priority={self.priority_score}, waiting_days={self.waiting_days})")


class WaitlistManager:
    """
    Manages patient waitlist with priority-based scheduling.
    
    This class:
    - Maintains priority queue of waitlisted patients
    - Automatically updates priorities based on waiting time
    - Suggests optimal patients when slots become available
    - Tracks contact attempts and follow-up requirements
    """
    
    def __init__(self):
        """Initialize waitlist manager."""
        self.waitlist = []  # Priority queue
        self.patient_records = {}  # patient_id -> WaitlistEntry
        self.contact_schedule = {}  # patient_id -> next_contact_date
        
        logger.info("Waitlist manager initialized")
    
    def add_patient(self, 
                    patient_id: str,
                    no_show_probability: float,
                    urgency_score: int,
                    preferred_doctor: Optional[str] = None,
                    preferred_date: Optional[datetime] = None,
                    medical_notes: str = "") -> bool:
        """
        Add a patient to the waitlist.
        
        Args:
            patient_id: Patient identifier
            no_show_probability: ML model prediction (0.0 to 1.0)
            urgency_score: Medical urgency (1-5)
            preferred_doctor: Preferred doctor ID
            preferred_date: Preferred appointment date
            medical_notes: Additional medical information
            
        Returns:
            True if successfully added, False otherwise
        """
        if patient_id in self.patient_records:
            logger.warning(f"Patient {patient_id} already in waitlist")
            return False
        
        # Create waitlist entry
        entry = WaitlistEntry(
            patient_id=patient_id,
            no_show_probability=no_show_probability,
            urgency_score=urgency_score,
            entry_date=datetime.now(),
            preferred_doctor=preferred_doctor,
            preferred_date=preferred_date,
            medical_notes=medical_notes
        )
        
        # Add to records and priority queue
        self.patient_records[patient_id] = entry
        heapq.heappush(self.waitlist, entry)
        
        # Schedule initial contact
        self._schedule_contact(patient_id, days_delay=1)
        
        logger.info(f"Added patient {patient_id} to waitlist with priority {entry.priority_score}")
        return True
    
    def remove_patient(self, patient_id: str) -> bool:
        """
        Remove a patient from the waitlist.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            True if successfully removed, False otherwise
        """
        if patient_id not in self.patient_records:
            return False
        
        # Remove from records
        entry = self.patient_records.pop(patient_id)
        
        # Remove from priority queue (reconstruct without this patient)
        self.waitlist = [p for p in self.waitlist if p.patient_id != patient_id]
        heapq.heapify(self.waitlist)
        
        # Remove from contact schedule
        self.contact_schedule.pop(patient_id, None)
        
        logger.info(f"Removed patient {patient_id} from waitlist")
        return True
    
    def get_top_patients(self, count: int = 5) -> List[WaitlistEntry]:
        """
        Get top priority patients from waitlist.
        
        Args:
            count: Number of top patients to return
            
        Returns:
            List of top priority WaitlistEntry objects
        """
        # Update all waiting times first
        self._update_all_waiting_times()
        
        # Return top patients (they're already sorted by priority)
        return self.waitlist[:count]
    
    def find_optimal_patient_for_slot(self, 
                                     available_slot: Any,
                                     doctor_id: str,
                                     slot_date: datetime) -> Optional[WaitlistEntry]:
        """
        Find the best patient for an available slot.
        
        Args:
            available_slot: Available slot information
            doctor_id: Doctor ID for the slot
            slot_date: Date of the available slot
            
        Returns:
            Optimal WaitlistEntry or None if no suitable patient
        """
        if not self.waitlist:
            return None
        
        # Update all waiting times
        self._update_all_waiting_times()
        
        # Filter patients by preferences and constraints
        suitable_patients = []
        
        for entry in self.waitlist:
            # Check doctor preference
            if entry.preferred_doctor and entry.preferred_doctor != doctor_id:
                continue
            
            # Check date preference (within reasonable range)
            if entry.preferred_date:
                days_diff = abs((slot_date.date() - entry.preferred_date.date()).days)
                if days_diff > 7:  # More than a week difference
                    continue
            
            # Calculate slot-specific score
            slot_score = self._calculate_slot_match_score(entry, available_slot, slot_date)
            suitable_patients.append((entry, slot_score))
        
        if not suitable_patients:
            return None
        
        # Return patient with highest slot match score
        suitable_patients.sort(key=lambda x: x[1], reverse=True)
        return suitable_patients[0][0]
    
    def _calculate_slot_match_score(self, 
                                   entry: WaitlistEntry,
                                   available_slot: Any,
                                   slot_date: datetime) -> float:
        """Calculate how well a patient matches an available slot."""
        score = 0.0
        
        # Base priority score
        score += entry.priority_score * 2
        
        # Date preference matching
        if entry.preferred_date:
            days_diff = abs((slot_date.date() - entry.preferred_date.date()).days)
            score += max(0, 10 - days_diff)  # Closer dates get higher scores
        
        # Time preference (if available)
        if hasattr(available_slot, 'start_time'):
            hour = available_slot.start_time.hour
            # Morning preference (9-12)
            if 9 <= hour <= 12:
                score += 3
            # Afternoon preference (13-17)
            elif 13 <= hour <= 17:
                score += 3
            # Evening preference (18-20)
            elif 18 <= hour <= 20:
                score += 3
        
        # Risk-based scoring (high-risk patients get priority for intervention)
        risk_assessor = RiskAssessor()
        risk_level = risk_assessor.assess_risk(entry.no_show_probability)
        if risk_level == RiskLevel.HIGH:
            score += 5
        elif risk_level == RiskLevel.MEDIUM:
            score += 3
        
        return score
    
    def update_patient_priority(self, 
                               patient_id: str,
                               new_no_show_probability: Optional[float] = None,
                               new_urgency_score: Optional[int] = None) -> bool:
        """
        Update patient's priority factors and recalculate priority score.
        
        Args:
            patient_id: Patient identifier
            new_no_show_probability: Updated ML prediction
            new_urgency_score: Updated urgency score
            
        Returns:
            True if successfully updated, False otherwise
        """
        if patient_id not in self.patient_records:
            return False
        
        entry = self.patient_records[patient_id]
        
        # Update values
        if new_no_show_probability is not None:
            entry.no_show_probability = new_no_show_probability
        
        if new_urgency_score is not None:
            entry.urgency_score = new_urgency_score
        
        # Recalculate priority
        entry._calculate_priority_score()
        
        # Rebuild priority queue
        heapq.heapify(self.waitlist)
        
        logger.info(f"Updated priority for patient {patient_id}: {entry.priority_score}")
        return True
    
    def get_contact_schedule(self) -> Dict[str, datetime]:
        """
        Get patients who need to be contacted.
        
        Returns:
            Dictionary of patient_id -> next_contact_date
        """
        current_time = datetime.now()
        due_contacts = {}
        
        for patient_id, next_contact in self.contact_schedule.items():
            if current_time >= next_contact:
                due_contacts[patient_id] = next_contact
        
        return due_contacts
    
    def record_contact_attempt(self, patient_id: str, success: bool = False) -> bool:
        """
        Record a contact attempt for a patient.
        
        Args:
            patient_id: Patient identifier
            success: Whether contact was successful
            
        Returns:
            True if successfully recorded, False otherwise
        """
        if patient_id not in self.patient_records:
            return False
        
        entry = self.patient_records[patient_id]
        entry.record_contact_attempt()
        
        if success:
            # Schedule next contact based on risk level
            risk_assessor = RiskAssessor()
            risk_level = risk_assessor.assess_risk(entry.no_show_probability)
            
            if risk_level == RiskLevel.HIGH:
                next_contact_days = 1  # Daily follow-up for high-risk
            elif risk_level == RiskLevel.MEDIUM:
                next_contact_days = 3  # Every 3 days for medium-risk
            else:
                next_contact_days = 7  # Weekly for low-risk
            
            self._schedule_contact(patient_id, days_delay=next_contact_days)
        else:
            # Retry sooner for failed contacts
            self._schedule_contact(patient_id, days_delay=1)
        
        logger.info(f"Recorded contact attempt for patient {patient_id}, success: {success}")
        return True
    
    def _schedule_contact(self, patient_id: str, days_delay: int):
        """Schedule next contact for a patient."""
        next_contact = datetime.now() + timedelta(days=days_delay)
        self.contact_schedule[patient_id] = next_contact
    
    def _update_all_waiting_times(self):
        """Update waiting times for all patients and rebuild priority queue."""
        for entry in self.waitlist:
            entry.update_waiting_time()
        
        # Rebuild priority queue after updating scores
        heapq.heapify(self.waitlist)
    
    def get_waitlist_statistics(self) -> Dict[str, Any]:
        """Get comprehensive waitlist statistics."""
        if not self.waitlist:
            return {
                "total_patients": 0,
                "average_waiting_time": 0,
                "risk_distribution": {},
                "urgency_distribution": {},
                "priority_distribution": {}
            }
        
        # Calculate statistics
        total_patients = len(self.waitlist)
        waiting_times = [entry.waiting_days for entry in self.waitlist]
        avg_waiting_time = sum(waiting_times) / len(waiting_times)
        
        # Risk distribution
        risk_assessor = RiskAssessor()
        risk_counts = {"low": 0, "medium": 0, "high": 0}
        for entry in self.waitlist:
            risk_level = risk_assessor.assess_risk(entry.no_show_probability)
            risk_counts[risk_level.value] += 1
        
        # Urgency distribution
        urgency_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for entry in self.waitlist:
            urgency_counts[entry.urgency_score] += 1
        
        # Priority distribution
        priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
        for entry in self.waitlist:
            priority_counts[entry.priority_score] += 1
        
        return {
            "total_patients": total_patients,
            "average_waiting_time": round(avg_waiting_time, 1),
            "risk_distribution": risk_counts,
            "urgency_distribution": urgency_counts,
            "priority_distribution": priority_counts,
            "max_waiting_time": max(waiting_times),
            "min_waiting_time": min(waiting_times)
        }
    
    def export_waitlist(self, format_type: str = "json") -> str:
        """
        Export waitlist data in specified format.
        
        Args:
            format_type: Export format ("json", "csv")
            
        Returns:
            Exported waitlist data
        """
        export_data = {
            "waitlist": [],
            "statistics": self.get_waitlist_statistics(),
            "export_timestamp": datetime.now().isoformat()
        }
        
        # Export waitlist entries
        for entry in self.waitlist:
            entry_data = {
                "patient_id": entry.patient_id,
                "no_show_probability": entry.no_show_probability,
                "urgency_score": entry.urgency_score,
                "entry_date": entry.entry_date.isoformat(),
                "waiting_days": entry.waiting_days,
                "priority_score": entry.priority_score,
                "preferred_doctor": entry.preferred_doctor,
                "preferred_date": entry.preferred_date.isoformat() if entry.preferred_date else None,
                "medical_notes": entry.medical_notes,
                "contact_attempts": entry.contact_attempts,
                "last_contact_date": entry.last_contact_date.isoformat()
            }
            export_data["waitlist"].append(entry_data)
        
        if format_type == "csv":
            return self._convert_to_csv(export_data)
        else:
            import json
            return json.dumps(export_data, indent=2)
    
    def _convert_to_csv(self, export_data: Dict[str, Any]) -> str:
        """Convert export data to CSV format."""
        import io
        
        output = io.StringIO()
        
        # Write header
        output.write("Patient ID,No-Show Probability,Urgency Score,Entry Date,"
                    "Waiting Days,Priority Score,Preferred Doctor,Preferred Date,"
                    "Contact Attempts,Last Contact\n")
        
        # Write waitlist entries
        for entry in export_data["waitlist"]:
            output.write(f"{entry['patient_id']},{entry['no_show_probability']:.3f},"
                        f"{entry['urgency_score']},{entry['entry_date']},"
                        f"{entry['waiting_days']},{entry['priority_score']},"
                        f"{entry['preferred_doctor'] or 'Any'},"
                        f"{entry['preferred_date'] or 'Any'},"
                        f"{entry['contact_attempts']},{entry['last_contact_date']}\n")
        
        return output.getvalue()

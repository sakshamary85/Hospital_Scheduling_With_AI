"""
Risk Assessment Module

Analyzes patient no-show risk based on ML predictions and determines
appropriate scheduling strategies and interventions.
"""

from typing import Dict, Any, Tuple, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for patient no-show probability."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskAssessor:
    """
    Assesses patient no-show risk and determines scheduling strategies.
    
    This class:
    - Categorizes patients into risk levels based on ML predictions
    - Determines appropriate scheduling strategies for each risk level
    - Suggests interventions to reduce no-show probability
    """
    
    def __init__(self, 
                 low_threshold: float = 0.3,
                 medium_threshold: float = 0.6,
                 high_threshold: float = 0.8):
        """
        Initialize risk assessor with configurable thresholds.
        
        Args:
            low_threshold: Maximum probability for low risk (default: 0.3)
            medium_threshold: Maximum probability for medium risk (default: 0.6)
            high_threshold: Maximum probability for high risk (default: 0.8)
        """
        self.low_threshold = low_threshold
        self.medium_threshold = medium_threshold
        self.high_threshold = high_threshold
        
        logger.info(f"Risk assessor initialized with thresholds: "
                   f"Low: {low_threshold}, Medium: {medium_threshold}, High: {high_threshold}")
    
    def assess_risk(self, no_show_probability: float) -> RiskLevel:
        """
        Assess patient risk level based on no-show probability.
        
        Args:
            no_show_probability: ML model prediction (0.0 to 1.0)
            
        Returns:
            RiskLevel enum value
        """
        if no_show_probability <= self.low_threshold:
            return RiskLevel.LOW
        elif no_show_probability <= self.medium_threshold:
            return RiskLevel.MEDIUM
        elif no_show_probability <= self.high_threshold:
            return RiskLevel.HIGH
        else:
            return RiskLevel.HIGH  # Very high risk
    
    def get_scheduling_strategy(self, 
                              risk_level: RiskLevel,
                              slot_available: bool = True,
                              slot_capacity: int = 1) -> Dict[str, Any]:
        """
        Determine scheduling strategy based on risk level and slot availability.
        
        Args:
            risk_level: Patient's assessed risk level
            slot_available: Whether the requested slot is available
            slot_capacity: Current capacity of the requested slot
            
        Returns:
            Dictionary containing scheduling strategy and recommendations
        """
        strategy = {
            "risk_level": risk_level.value,
            "action": None,
            "buffer_time": 0,
            "requires_confirmation": False,
            "waitlist_priority": 0,
            "interventions": [],
            "notes": ""
        }
        
        if risk_level == RiskLevel.LOW:
            strategy.update(self._low_risk_strategy(slot_available, slot_capacity))
        elif risk_level == RiskLevel.MEDIUM:
            strategy.update(self._medium_risk_strategy(slot_available, slot_capacity))
        elif risk_level == RiskLevel.HIGH:
            strategy.update(self._high_risk_strategy(slot_available, slot_capacity))
        
        return strategy
    
    def _low_risk_strategy(self, slot_available: bool, slot_capacity: int) -> Dict[str, Any]:
        """Strategy for low-risk patients."""
        if slot_available and slot_capacity > 0:
            return {
                "action": "confirm",
                "buffer_time": 0,
                "requires_confirmation": False,
                "waitlist_priority": 0,
                "interventions": ["standard_reminder"],
                "notes": "Low risk patient - standard scheduling"
            }
        else:
            return {
                "action": "reschedule",
                "buffer_time": 0,
                "requires_confirmation": False,
                "waitlist_priority": 1,
                "interventions": ["standard_reminder"],
                "notes": "Low risk patient - reschedule to available slot"
            }
    
    def _medium_risk_strategy(self, slot_available: bool, slot_capacity: int) -> Dict[str, Any]:
        """Strategy for medium-risk patients."""
        if slot_available and slot_capacity > 0:
            return {
                "action": "confirm_with_buffer",
                "buffer_time": 15,  # 15 minutes buffer
                "requires_confirmation": True,
                "waitlist_priority": 2,
                "interventions": ["enhanced_reminder", "confirmation_call"],
                "notes": "Medium risk patient - confirm with buffer time and follow-up"
            }
        else:
            return {
                "action": "reschedule_optimal",
                "buffer_time": 0,
                "requires_confirmation": True,
                "waitlist_priority": 3,
                "interventions": ["enhanced_reminder", "confirmation_call"],
                "notes": "Medium risk patient - find optimal slot with confirmation"
            }
    
    def _high_risk_strategy(self, slot_available: bool, slot_capacity: int) -> Dict[str, Any]:
        """Strategy for high-risk patients."""
        if slot_available and slot_capacity > 0:
            return {
                "action": "confirm_with_extended_buffer",
                "buffer_time": 30,  # 30 minutes buffer
                "requires_confirmation": True,
                "waitlist_priority": 4,
                "interventions": ["urgent_reminder", "confirmation_call", "alternative_times"],
                "notes": "High risk patient - extended buffer and intensive follow-up"
            }
        else:
            return {
                "action": "waitlist_high_priority",
                "buffer_time": 0,
                "requires_confirmation": True,
                "waitlist_priority": 5,
                "interventions": ["urgent_reminder", "confirmation_call", "alternative_times"],
                "notes": "High risk patient - high priority waitlist placement"
            }
    
    def get_intervention_recommendations(self, risk_level: RiskLevel) -> List[str]:
        """
        Get recommended interventions for a given risk level.
        
        Args:
            risk_level: Patient's risk level
            
        Returns:
            List of recommended interventions
        """
        interventions = {
            RiskLevel.LOW: [
                "Standard SMS reminder 24h before appointment",
                "Email confirmation",
                "App notification"
            ],
            RiskLevel.MEDIUM: [
                "Enhanced SMS reminder 48h and 24h before",
                "Confirmation call 24h before appointment",
                "Email with appointment details",
                "App notification with reminder"
            ],
            RiskLevel.HIGH: [
                "Urgent SMS reminder 72h, 48h, and 24h before",
                "Confirmation call 48h and 24h before",
                "Personalized email with appointment importance",
                "App notification with multiple reminders",
                "Alternative appointment time suggestions",
                "Follow-up call after appointment"
            ]
        }
        
        return interventions.get(risk_level, [])
    
    def calculate_waitlist_priority(self, 
                                  no_show_probability: float,
                                  urgency_score: int = 1,
                                  waiting_time: int = 0) -> int:
        """
        Calculate waitlist priority score.
        
        Args:
            no_show_probability: ML prediction (0.0 to 1.0)
            urgency_score: Medical urgency (1-5, 5 being most urgent)
            waiting_time: Days patient has been waiting
            
        Returns:
            Priority score (higher = higher priority)
        """
        # Base priority from risk level
        risk_priority = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 3,
            RiskLevel.HIGH: 5
        }
        
        risk_level = self.assess_risk(no_show_probability)
        base_priority = risk_priority[risk_level]
        
        # Adjust for urgency
        urgency_multiplier = urgency_score / 5.0
        
        # Adjust for waiting time (diminishing returns after 7 days)
        waiting_bonus = min(waiting_time, 7) * 0.5
        
        priority_score = int(base_priority * urgency_multiplier + waiting_bonus)
        
        return max(1, min(priority_score, 10))  # Clamp between 1-10
    
    def get_risk_summary(self, no_show_probability: float) -> Dict[str, Any]:
        """
        Get comprehensive risk assessment summary.
        
        Args:
            no_show_probability: ML model prediction
            
        Returns:
            Dictionary with complete risk assessment
        """
        risk_level = self.assess_risk(no_show_probability)
        
        return {
            "no_show_probability": no_show_probability,
            "risk_level": risk_level.value,
            "risk_description": self._get_risk_description(risk_level),
            "scheduling_recommendation": self._get_scheduling_recommendation(risk_level),
            "interventions": self.get_intervention_recommendations(risk_level),
            "monitoring_frequency": self._get_monitoring_frequency(risk_level)
        }
    
    def _get_risk_description(self, risk_level: RiskLevel) -> str:
        """Get human-readable risk description."""
        descriptions = {
            RiskLevel.LOW: "Patient shows low likelihood of missing appointment",
            RiskLevel.MEDIUM: "Patient shows moderate risk of missing appointment",
            RiskLevel.HIGH: "Patient shows high risk of missing appointment"
        }
        return descriptions.get(risk_level, "Risk level not determined")
    
    def _get_scheduling_recommendation(self, risk_level: RiskLevel) -> str:
        """Get scheduling recommendation."""
        recommendations = {
            RiskLevel.LOW: "Standard scheduling with minimal intervention",
            RiskLevel.MEDIUM: "Schedule with buffer time and confirmation calls",
            RiskLevel.HIGH: "High-priority scheduling with intensive follow-up"
        }
        return recommendations.get(risk_level, "Recommendation not available")
    
    def _get_monitoring_frequency(self, risk_level: RiskLevel) -> str:
        """Get recommended monitoring frequency."""
        frequencies = {
            RiskLevel.LOW: "Standard monitoring (24h before appointment)",
            RiskLevel.MEDIUM: "Enhanced monitoring (48h and 24h before appointment)",
            RiskLevel.HIGH: "Intensive monitoring (72h, 48h, and 24h before appointment)"
        }
        return frequencies.get(risk_level, "Monitoring frequency not determined")

"""
Hospital AI Appointment Scheduler

A Python module that integrates with existing ML models to provide
intelligent appointment scheduling and optimization for hospitals.
"""

__version__ = "1.0.0"
__author__ = "Hospital AI Team"

from .ai_agent import AIAppointmentScheduler
from .slot_optimizer import SlotOptimizer
from .risk_assessor import RiskAssessor
from .waitlist_manager import WaitlistManager

__all__ = [
    "AIAppointmentScheduler",
    "SlotOptimizer", 
    "RiskAssessor",
    "WaitlistManager"
]

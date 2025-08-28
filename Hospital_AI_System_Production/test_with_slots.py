#!/usr/bin/env python3
"""
Test AI Agent with Available Slots
Demonstrates confirm action for low risk patients
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_with_available_slots():
    """Test AI Agent when slots are available."""
    print("🧪 Testing AI Agent with Available Slots...")
    
    try:
        from ai_agent_core.ai_agent import AIAppointmentScheduler
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        # Initialize scheduler
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        scheduler = AIAppointmentScheduler(model_path)
        
        # Add available slots for testing
        from datetime import datetime, timedelta
        
        # Create test slots
        test_date = datetime.now() + timedelta(days=1)
        start_time = test_date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(minutes=30)
        
        # Add doctor schedule
        scheduler.slot_optimizer.add_doctor_schedule(
            doctor_id="DR001",
            start_date=test_date,
            end_date=test_date + timedelta(days=1),
            working_hours=(9, 17),
            slot_duration=30,
            max_capacity=1
        )
        
        print("✅ Added test slots for DR001")
        
        # Test patient data
        test_patient = get_correct_patient_data()
        test_patient = set_neighbourhood(test_patient, "CENTRO")
        
        # Test appointment request
        appointment_request = {
            "patient_id": "TEST001",
            "preferred_doctor": "DR001",
            "preferred_date": test_date.strftime("%Y-%m-%d"),
            "preferred_time": "09:00",
            "urgency_score": 2,
            "medical_notes": "Test consultation"
        }
        
        # Run AI scheduling
        result = scheduler.schedule_appointment(test_patient, appointment_request)
        
        print("\n📊 RESULTS WITH AVAILABLE SLOTS:")
        print(f"   Action: {result.get('action', 'N/A')}")
        print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
        no_show_prob = result.get('no_show_probability', 'N/A')
        if isinstance(no_show_prob, (int, float)):
            print(f"   No-show Probability: {no_show_prob:.3f}")
        else:
            print(f"   No-show Probability: {no_show_prob}")
        print(f"   Slot Assigned: {result.get('slot_assigned', 'N/A')}")
        print(f"   Doctor ID: {result.get('doctor_id', 'N/A')}")
        print(f"   Start Time: {result.get('start_time', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        return False

if __name__ == "__main__":
    test_with_available_slots()

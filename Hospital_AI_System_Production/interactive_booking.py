#!/usr/bin/env python3
"""
Interactive Hospital Appointment Booking System
User can manually input details and see AI processing in real-time
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_user_input():
    """Get patient and appointment details from user."""
    print("🏥 INTERACTIVE HOSPITAL APPOINTMENT BOOKING")
    print("=" * 60)
    print("Please provide the following details:")
    print()
    
    # Patient Details
    print("📋 PATIENT DETAILS:")
    print("-" * 30)
    
    age = int(input("Age: "))
    gender = input("Gender (M/F): ").upper()
    gender_code = 1 if gender == 'M' else 0
    
    print("\nMedical Conditions (Y/N):")
    scholarship = input("Scholarship: ").upper() == 'Y'
    hypertension = input("Hypertension: ").upper() == 'Y'
    diabetes = input("Diabetes: ").upper() == 'Y'
    alcoholism = input("Alcoholism: ").upper() == 'Y'
    handicap = input("Handicap: ").upper() == 'Y'
    
    sms_received = input("SMS Received (Y/N): ").upper() == 'Y'
    lead_days = int(input("Days until appointment: "))
    
    print("\nAppointment History:")
    no_show_rate = float(input("No-show rate (0.0-1.0): "))
    last_show_status = input("Last appointment attended (Y/N): ").upper() == 'Y'
    appointment_count = int(input("Total previous appointments: "))
    last_appointment_days = int(input("Days since last appointment: "))
    
    print("\nNeighborhood (enter number):")
    print("1. CENTRO")
    print("2. JARDIM_CAMBURI") 
    print("3. SANTA_TEREZA")
    print("4. BOA_VISTA")
    neighborhood_choice = int(input("Choose neighborhood (1-4): "))
    
    neighborhoods = ["CENTRO", "JARDIM_CAMBURI", "SANTA_TEREZA", "BOA_VISTA"]
    neighborhood = neighborhoods[neighborhood_choice - 1]
    
    # Appointment Request
    print("\n📅 APPOINTMENT REQUEST:")
    print("-" * 30)
    
    patient_id = input("Patient ID: ")
    preferred_doctor = input("Preferred Doctor: ")
    
    print("\nPreferred Date:")
    year = int(input("Year (2025): "))
    month = int(input("Month (1-12): "))
    day = int(input("Day (1-31): "))
    
    print("\nPreferred Time:")
    print("Available hours: 9, 10, 11, 12, 13, 14, 15, 16, 17")
    hour = int(input("Hour: "))
    print("Available minutes: 0, 30")
    minute = int(input("Minute: "))
    
    # Create preferred time string - no validation, no default
    preferred_time = f"{hour:02d}:{minute:02d}"
    print(f"✅ Your Preferred Time: {preferred_time}")
    
    urgency_score = int(input("Urgency Score (1-5): "))
    medical_notes = input("Medical Notes: ")
    
    # Available Slots
    print("\n📊 AVAILABLE SLOTS:")
    print("-" * 30)
    print("Enter available slots (Y/N for each time):")
    print(f"⚠️  Make sure {preferred_time} is marked correctly!")
    
    available_slots = {}
    for h in range(9, 18):
        for m in [0, 30]:
            time_str = f"{h:02d}:{m:02d}"
            if time_str == preferred_time:
                print(f"{time_str}: [YOUR PREFERRED TIME]")
                available = input(f"Available (Y/N): ").upper() == 'Y'
            else:
                available = input(f"{time_str}: ").upper() == 'Y'
            available_slots[time_str] = available
    
    return {
        "patient_data": {
            "age": age,
            "gender": gender_code,
            "scholarship": scholarship,
            "hypertension": hypertension,
            "diabetes": diabetes,
            "alcoholism": alcoholism,
            "handicap": handicap,
            "sms_received": sms_received,
            "lead_days": lead_days,
            "no_show_rate": no_show_rate,
            "last_show_status": last_show_status,
            "appointment_count": appointment_count,
            "last_appointment_days": last_appointment_days,
            "neighborhood": neighborhood
        },
        "appointment_request": {
            "patient_id": patient_id,
            "preferred_doctor": preferred_doctor,
            "preferred_date": f"{year}-{month:02d}-{day:02d}",
            "preferred_time": preferred_time,
            "urgency_score": urgency_score,
            "medical_notes": medical_notes
        },
        "available_slots": available_slots
    }

def make_ai_decision(risk_level, slot_available, preferred_time):
    """Make AI decision based on risk level and slot availability."""
    print(f"\n🎯 AI DECISION LOGIC:")
    print("-" * 30)
    print(f"   Risk Level: {risk_level.value}")
    print(f"   Preferred Time: {preferred_time}")
    print(f"   Slot Available: {'✅ YES' if slot_available else '❌ NO'}")
    
    if slot_available:
        if risk_level.value == "low":
            action = "confirm"
            success = True
            buffer_time = 0
            print(f"   Decision: Low risk + Slot available = CONFIRM")
        elif risk_level.value == "medium":
            action = "confirm_with_buffer"
            success = True
            buffer_time = 15
            print(f"   Decision: Medium risk + Slot available = CONFIRM with 15 min buffer")
        elif risk_level.value == "high":
            action = "confirm_with_extended_buffer"
            success = True
            buffer_time = 30
            print(f"   Decision: High risk + Slot available = CONFIRM with 30 min buffer")
        else:
            action = "confirm"
            success = True
            buffer_time = 0
            print(f"   Decision: Unknown risk + Slot available = CONFIRM")
    else:
        if risk_level.value == "low":
            action = "waitlist_standard"
            success = False
            buffer_time = 0
            print(f"   Decision: Low risk + No slot = Standard waitlist")
        elif risk_level.value == "medium":
            action = "waitlist_priority"
            success = False
            buffer_time = 0
            print(f"   Decision: Medium risk + No slot = Priority waitlist")
        elif risk_level.value == "high":
            action = "waitlist_urgent"
            success = False
            buffer_time = 0
            print(f"   Decision: High risk + No slot = Urgent waitlist")
        else:
            action = "waitlist_standard"
            success = False
            buffer_time = 0
            print(f"   Decision: Unknown risk + No slot = Standard waitlist")
    
    return {
        "action": action,
        "success": success,
        "buffer_time": buffer_time
    }

def process_ai_decision(user_data):
    """Process AI decision with user data."""
    try:
        from ai_agent_core.ai_agent import AIAppointmentScheduler
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        print("\n🤖 AI SYSTEM PROCESSING...")
        print("=" * 60)
        
        # Initialize AI Scheduler
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        scheduler = AIAppointmentScheduler(model_path)
        
        print("✅ AI Scheduler initialized")
        
        # Prepare patient data
        patient_data = get_correct_patient_data()
        patient_data = set_neighbourhood(patient_data, user_data["patient_data"]["neighborhood"])
        
        # Update with user input
        patient_data.update({
            "Age": user_data["patient_data"]["age"],
            "Gender": user_data["patient_data"]["gender"],
            "Scholarship": user_data["patient_data"]["scholarship"],
            "Hypertension": user_data["patient_data"]["hypertension"],
            "Diabetes": user_data["patient_data"]["diabetes"],
            "Alcoholism": user_data["patient_data"]["alcoholism"],
            "Handicap": user_data["patient_data"]["handicap"],
            "SmsReceived": user_data["patient_data"]["sms_received"],
            "LeadDays": user_data["patient_data"]["lead_days"],
            "NoShowRate": user_data["patient_data"]["no_show_rate"],
            "LastShowStatus": user_data["patient_data"]["last_show_status"],
            "AppointmentCount": user_data["patient_data"]["appointment_count"],
            "LastAppointmentDays": user_data["patient_data"]["last_appointment_days"]
        })
        
        print("✅ Patient data prepared (98 features)")
        
        # Get ML prediction
        print("\n🧠 ML MODEL ANALYSIS:")
        print("-" * 30)
        prediction = scheduler.ml_integration.predict_with_full_output(patient_data)
        
        print(f"   Prediction: {prediction['prediction']}")
        print(f"   Show Probability: {prediction['show_probability']:.3f} ({prediction['show_probability']*100:.1f}%)")
        print(f"   No-show Probability: {prediction['no_show_probability']:.3f} ({prediction['no_show_probability']*100:.1f}%)")
        
        # Risk assessment
        print("\n⚠️  RISK ASSESSMENT:")
        print("-" * 30)
        risk_level = scheduler.risk_assessor.assess_risk(
            ml_prediction=prediction["prediction"],
            show_probability=prediction["show_probability"],
            no_show_probability=prediction["no_show_probability"]
        )
        
        print(f"   Risk Level: {risk_level.value}")
        
        # Check slot availability
        preferred_time = user_data["appointment_request"]["preferred_time"]
        slot_available = user_data["available_slots"].get(preferred_time, False)
        
        print(f"\n📅 SLOT AVAILABILITY:")
        print("-" * 30)
        print(f"   Your Preferred Time: {preferred_time}")
        print(f"   Available: {'✅ YES' if slot_available else '❌ NO'}")
        
        if not slot_available:
            print(f"\n   ⚠️  {preferred_time} is NOT available!")
            print("   Alternative Available Slots:")
            for time, available in user_data["available_slots"].items():
                if available:
                    print(f"   - {time}")
        else:
            print(f"   ✅ {preferred_time} is available for booking!")
        
        # Make AI decision using our custom logic
        ai_decision = make_ai_decision(risk_level, slot_available, preferred_time)
        
        # Get interventions
        interventions = scheduler.risk_assessor.get_intervention_recommendations(risk_level)
        
        print(f"\n🎯 AI DECISION RESULT:")
        print("-" * 30)
        print(f"   Action: {ai_decision['action']}")
        print(f"   Success: {ai_decision['success']}")
        print(f"   Buffer Time: {ai_decision['buffer_time']} minutes")
        print(f"   Interventions: {', '.join(interventions[:3])}")
        
        # Final summary
        print("\n📊 FINAL SUMMARY:")
        print("=" * 60)
        print(f"Patient: {user_data['appointment_request']['patient_id']}")
        print(f"Doctor: {user_data['appointment_request']['preferred_doctor']}")
        print(f"Date: {user_data['appointment_request']['preferred_date']}")
        print(f"Your Preferred Time: {user_data['appointment_request']['preferred_time']}")
        print(f"Slot Available: {'✅ YES' if slot_available else '❌ NO'}")
        print(f"ML Prediction: {prediction['prediction']}")
        print(f"Risk Level: {risk_level.value}")
        print(f"AI Action: {ai_decision['action']}")
        
        # Show final result
        if slot_available and ai_decision['success']:
            print(f"Final Result: ✅ APPOINTMENT CONFIRMED at {preferred_time}")
            if ai_decision['buffer_time'] > 0:
                print(f"   Buffer Time: {ai_decision['buffer_time']} minutes")
        elif slot_available and not ai_decision['success']:
            print(f"Final Result: ⚠️  Slot available but AI decision failed")
        else:
            print(f"Final Result: ❌ SLOT NOT AVAILABLE - {preferred_time}")
            print(f"   AI suggests: {ai_decision['action']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main interactive function."""
    print("🏥 HOSPITAL AI SYSTEM - INTERACTIVE BOOKING")
    print("=" * 60)
    print("This system allows you to manually input patient details")
    print("and see real-time AI processing for appointment scheduling.")
    print()
    
    try:
        # Get user input
        user_data = get_user_input()
        
        # Process AI decision
        success = process_ai_decision(user_data)
        
        if success:
            print("\n🎉 PROCESSING COMPLETED!")
            print("You can now see how the AI system works with your input.")
        else:
            print("\n❌ PROCESSING FAILED!")
            print("Please check the error and try again.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Process cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

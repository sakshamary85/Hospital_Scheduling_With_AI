#!/usr/bin/env python3
"""
Hospital AI System - Production Demo
Shows different AI decisions for different patient scenarios
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_ai_agent():
    """Demo AI Agent with different scenarios."""
    print("🤖 AI AGENT DEMONSTRATION")
    print("=" * 50)
    
    try:
        from ai_agent_core.ai_agent import AIAppointmentScheduler
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        # Initialize scheduler
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        scheduler = AIAppointmentScheduler(model_path)
        
        # Add available slots for testing
        test_date = datetime.now() + timedelta(days=1)
        scheduler.slot_optimizer.add_doctor_schedule(
            doctor_id="DR001",
            start_date=test_date,
            end_date=test_date + timedelta(days=1),
            working_hours=(9, 17),
            slot_duration=30,
            max_capacity=1
        )
        
        print("✅ AI Scheduler initialized with available slots")
        
        # Create different patient scenarios
        scenarios = [
            {
                "name": "Low Risk Patient",
                "age": 25,
                "gender": 0,  # Female
                "neighborhood": "CENTRO",
                "medical_history": "Healthy, good attendance",
                "expected_risk": "low",
                "expected_action": "confirm"
            },
            {
                "name": "Medium Risk Patient", 
                "age": 65,
                "gender": 1,  # Male
                "neighborhood": "SANTA_TEREZA",
                "medical_history": "Elderly, some health issues",
                "expected_risk": "medium",
                "expected_action": "confirm_with_buffer"
            },
            {
                "name": "High Risk Patient",
                "age": 75,
                "gender": 1,  # Male
                "neighborhood": "JARDIM_CAMBURI",
                "medical_history": "Chronic conditions, poor attendance",
                "expected_risk": "high",
                "expected_action": "confirm_with_extended_buffer"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['name']}")
            print("-" * 40)
            
            # Prepare patient data
            patient_data = get_correct_patient_data()
            patient_data = set_neighbourhood(patient_data, scenario["neighborhood"])
            patient_data.update({
                "Age": scenario["age"],
                "Gender": scenario["gender"],
                "NoShowRate": 0.1 if scenario["expected_risk"] == "low" else 0.5 if scenario["expected_risk"] == "medium" else 0.8,
                "LastShowStatus": 1 if scenario["expected_risk"] == "low" else 0 if scenario["expected_risk"] == "high" else 1,
                "AppointmentCount": 1 if scenario["expected_risk"] == "low" else 5 if scenario["expected_risk"] == "high" else 3
            })
            
            # Get ML prediction
            prediction = scheduler.ml_integration.predict_with_full_output(patient_data)
            
            # Get risk assessment
            risk_level = scheduler.risk_assessor.assess_risk(
                ml_prediction=prediction["prediction"],
                show_probability=prediction["show_probability"],
                no_show_probability=prediction["no_show_probability"]
            )
            
            # Get scheduling strategy
            strategy = scheduler.risk_assessor.get_scheduling_strategy(
                risk_level, 
                slot_available=True, 
                slot_capacity=1
            )
            
            print(f"   Age: {scenario['age']} | Gender: {'Male' if scenario['gender'] else 'Female'}")
            print(f"   Neighborhood: {scenario['neighborhood']}")
            print(f"   Medical History: {scenario['medical_history']}")
            print(f"   ML Prediction: {prediction['prediction']}")
            print(f"   Show Probability: {prediction['show_probability']:.3f}")
            print(f"   No-show Probability: {prediction['no_show_probability']:.3f}")
            print(f"   Risk Level: {risk_level.value}")
            print(f"   AI Action: {strategy['action']}")
            print(f"   Buffer Time: {strategy['buffer_time']} minutes")
            print(f"   Requires Confirmation: {strategy['requires_confirmation']}")
            
            # Get interventions
            interventions = scheduler.risk_assessor.get_intervention_recommendations(risk_level)
            print(f"   Interventions: {', '.join(interventions[:2])}")
            
            # Show expected vs actual
            print(f"   Expected Risk: {scenario['expected_risk']}")
            print(f"   Expected Action: {scenario['expected_action']}")
            
        return True
        
    except Exception as e:
        print(f"❌ AI Agent Demo Failed: {e}")
        return False

def demo_ml_model():
    """Demo ML Model capabilities."""
    print("\n\n🧠 ML MODEL DEMONSTRATION")
    print("=" * 50)
    
    try:
        from ai_agent_core.ml_integration import MLModelIntegration
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        # Initialize ML Integration
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        ml_integration = MLModelIntegration(model_path)
        
        print("✅ ML Model loaded successfully")
        print(f"📊 Model expects 98 features")
        
        # Test different neighborhoods
        neighborhoods = ["CENTRO", "JARDIM_CAMBURI", "SANTA_TEREZA", "BOA_VISTA"]
        
        for neighborhood in neighborhoods:
            print(f"\n🏘️  Testing Neighborhood: {neighborhood}")
            
            # Get patient data
            patient_data = get_correct_patient_data()
            patient_data = set_neighbourhood(patient_data, neighborhood)
            
            # Get prediction
            prediction = ml_integration.predict_with_full_output(patient_data)
            
            print(f"   Prediction: {prediction['prediction']}")
            print(f"   No-show Probability: {prediction['no_show_probability']:.3f}")
            print(f"   Show Probability: {prediction['show_probability']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML Model Demo Failed: {e}")
        return False

def demo_risk_assessment():
    """Demo Risk Assessment capabilities."""
    print("\n\n⚠️  RISK ASSESSMENT DEMONSTRATION")
    print("=" * 50)
    
    try:
        from ai_agent_core.risk_assessor import RiskAssessor
        
        risk_assessor = RiskAssessor()
        print("✅ Risk Assessor initialized")
        
        # Test different probability scenarios
        test_scenarios = [
            {"show_prob": 0.9, "no_show_prob": 0.1, "prediction": "Show"},
            {"show_prob": 0.6, "no_show_prob": 0.4, "prediction": "Show"},
            {"show_prob": 0.4, "no_show_prob": 0.6, "prediction": "Show"},
            {"show_prob": 0.2, "no_show_prob": 0.8, "prediction": "No-show"},
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📊 Scenario {i}:")
            print(f"   Show Probability: {scenario['show_prob']:.1f} ({scenario['show_prob']*100:.0f}%)")
            print(f"   No-show Probability: {scenario['no_show_prob']:.1f} ({scenario['no_show_prob']*100:.0f}%)")
            print(f"   ML Prediction: {scenario['prediction']}")
            
            risk_level = risk_assessor.assess_risk(
                ml_prediction=scenario['prediction'],
                show_probability=scenario['show_prob'],
                no_show_probability=scenario['no_show_prob']
            )
            
            strategy = risk_assessor.get_scheduling_strategy(risk_level, slot_available=True, slot_capacity=1)
            
            print(f"   Risk Level: {risk_level.value}")
            print(f"   AI Action: {strategy['action']}")
            print(f"   Buffer Time: {strategy['buffer_time']} minutes")
            
            interventions = risk_assessor.get_intervention_recommendations(risk_level)
            print(f"   Interventions: {', '.join(interventions[:2])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Risk Assessment Demo Failed: {e}")
        return False

def demo_scheduling_workflow():
    """Demo complete scheduling workflow."""
    print("\n\n📅 SCHEDULING WORKFLOW DEMONSTRATION")
    print("=" * 50)
    
    try:
        from ai_agent_core.ai_agent import AIAppointmentScheduler
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        # Initialize scheduler
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        scheduler = AIAppointmentScheduler(model_path)
        
        print("✅ AI Scheduler initialized")
        
        # Test patient data
        test_patient = get_correct_patient_data()
        test_patient = set_neighbourhood(test_patient, "CENTRO")
        
        # Test appointment request
        appointment_request = {
            "patient_id": "DEMO001",
            "preferred_doctor": "DR_SMITH",
            "preferred_date": "2024-01-25",
            "preferred_time": "10:00",
            "urgency_score": 3,
            "medical_notes": "Routine consultation"
        }
        
        print(f"\n📋 Appointment Request:")
        print(f"   Patient: {appointment_request['patient_id']}")
        print(f"   Doctor: {appointment_request['preferred_doctor']}")
        print(f"   Date: {appointment_request['preferred_date']}")
        print(f"   Time: {appointment_request['preferred_time']}")
        print(f"   Urgency: {appointment_request['urgency_score']}/5")
        
        # Run AI scheduling
        result = scheduler.schedule_appointment(test_patient, appointment_request)
        
        print(f"\n🤖 AI Decision:")
        print(f"   Action: {result.get('action', 'N/A')}")
        print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"   No-show Probability: {result.get('no_show_probability', 'N/A'):.3f}")
        print(f"   Buffer Time: {result.get('buffer_time', 'N/A')} minutes")
        print(f"   Success: {result.get('success', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduling Workflow Demo Failed: {e}")
        return False

def main():
    """Main demo function."""
    print("🏥 HOSPITAL AI SYSTEM - PRODUCTION DEMO")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run demos
    demos = [
        ("AI Agent", demo_ai_agent),
        ("ML Model", demo_ml_model),
        ("Risk Assessment", demo_risk_assessment),
        ("Scheduling Workflow", demo_scheduling_workflow)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        try:
            result = demo_func()
            results.append((demo_name, result))
        except Exception as e:
            print(f"❌ {demo_name} Demo Crashed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{demo_name:25} : {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total Demos: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL DEMOS PASSED! System is working perfectly!")
        print("\n🚀 Next Steps:")
        print("1. Run tests: python test_core_system.py")
        print("2. Start API: python -m uvicorn api_services.main:app --host 127.0.0.1 --port 8080")
        print("3. Access API: http://localhost:8080")
        print("4. View docs: http://localhost:8080/docs")
    else:
        print(f"\n⚠️  {total - passed} demo(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

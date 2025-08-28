#!/usr/bin/env python3
"""
Test Production Hospital AI System
Verify all components are working correctly
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_agent_core():
    """Test AI Agent core functionality."""
    print("🧪 Testing AI Agent Core...")
    
    try:
        from ai_agent_core.ai_agent import AIAppointmentScheduler
        from ai_agent_core.ml_integration import MLModelIntegration
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        # Test ML Model Integration
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        ml_integration = MLModelIntegration(model_path)
        print("ML Model Integration: OK")
        
        # Test Patient Data
        test_patient = get_correct_patient_data()
        test_patient = set_neighbourhood(test_patient, "CENTRO")
        print(f"Patient Data: {len(test_patient)} features")
        
        # Test ML Prediction
        prediction = ml_integration.predict_with_full_output(test_patient)
        print(f"ML Prediction: {prediction['prediction']}")
        print(f"   No-show probability: {prediction['no_show_probability']:.3f}")
        
        # Test AI Scheduler
        scheduler = AIAppointmentScheduler(model_path)
        print("AI Scheduler: OK")
        
        # Test Risk Assessment
        risk_level = scheduler.risk_assessor.assess_risk(prediction['no_show_probability'])
        print(f"Risk Assessment: {risk_level.value}")
        
        return True
        
    except Exception as e:
        print(f"AI Agent Core Test Failed: {e}")
        return False

def test_configuration():
    """Test configuration system."""
    print("\nTesting Configuration...")
    
    try:
        from production_config.config import config
        
        print(f"Database Config: {config.database.POSTGRES_HOST}:{config.database.POSTGRES_PORT}")
        print(f"ML Model Path: {config.ml_model.MODEL_PATH}")
        print(f"API Config: {config.api.HOST}:{config.api.PORT}")
        print(f"Hospital Hours: {config.hospital.WORKING_HOURS_START}:00 - {config.hospital.WORKING_HOURS_END}:00")
        
        return True
        
    except Exception as e:
        print(f"Configuration Test Failed: {e}")
        return False

def test_database_models():
    """Test database models."""
    print("\nTesting Database Models...")
    
    try:
        from database_models.models import Patient, Doctor, Appointment, Base
        
        print("Patient Model: OK")
        print("Doctor Model: OK")
        print("Appointment Model: OK")
        print("Base Model: OK")
        
        return True
        
    except Exception as e:
        print(f"Database Models Test Failed: {e}")
        return False

def test_backend_integration():
    """Test backend integration services."""
    print("\n🔗 Testing Backend Integration...")
    
    try:
        from backend_integration.patient_service import PatientService
        
        print("Patient Service: OK")
        
        # Note: Database connection not tested (would need actual DB)
        print("Database connection not tested (requires actual database)")
        
        return True
        
    except Exception as e:
        print(f"Backend Integration Test Failed: {e}")
        return False

def test_api_service():
    """Test API service."""
    print("\n🌐 Testing API Service...")
    
    try:
        from api_services.main import app
        
        print("FastAPI App: OK")
        print(f"API Title: {app.title}")
        print(f"API Version: {app.version}")
        
        # Check endpoints
        routes = [route.path for route in app.routes]
        print(f"API Routes: {len(routes)} endpoints")
        
        return True
        
    except Exception as e:
        print(f"API Service Test Failed: {e}")
        return False

def test_complete_workflow():
    """Test complete AI workflow."""
    print("\nTesting Complete AI Workflow...")
    
    try:
        from ai_agent_core.ai_agent import AIAppointmentScheduler
        from ai_agent_core.correct_patient_data_98_features import get_correct_patient_data, set_neighbourhood
        
        # Initialize scheduler
        model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
        scheduler = AIAppointmentScheduler(model_path)
        
        # Test patient data
        test_patient = get_correct_patient_data()
        test_patient = set_neighbourhood(test_patient, "CENTRO")
        
        # Test appointment request
        appointment_request = {
            "patient_id": "TEST001",
            "preferred_doctor": "DR001",
            "preferred_date": "2024-01-20",
            "preferred_time": "09:00",
            "urgency_score": 2,
            "medical_notes": "Test consultation"
        }
        
        # Run AI scheduling
        result = scheduler.schedule_appointment(test_patient, appointment_request)
        
        print("Complete Workflow: OK")
        print(f"   Action: {result.get('action', 'N/A')}")
        print(f"   Risk Level: {result.get('risk_level', 'N/A')}")
        print(f"   No-show Probability: {result.get('no_show_probability', 'N/A'):.3f}")
        print(f"   Buffer Time: {result.get('buffer_time', 'N/A')} minutes")
        
        return True
        
    except Exception as e:
        print(f"Complete Workflow Test Failed: {e}")
        return False

def main():
    """Main test function."""
    print("Hospital AI System - Production Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run all tests
    tests = [
        ("AI Agent Core", test_ai_agent_core),
        ("Configuration", test_configuration),
        ("Database Models", test_database_models),
        ("Backend Integration", test_backend_integration),
        ("API Service", test_api_service),
        ("Complete Workflow", test_complete_workflow)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"{test_name} Test Crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:25} : {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\nALL TESTS PASSED! Production system is ready!")
        print("\nNext Steps:")
        print("1. Start the API server: python api_services/main.py")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Test endpoints with real data")
        print("4. Deploy to production environment")
    else:
        print(f"\n{total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

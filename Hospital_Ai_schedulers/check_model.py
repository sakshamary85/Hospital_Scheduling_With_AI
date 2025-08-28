#!/usr/bin/env python3
import pickle

try:
    # Load the model
    model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
    print(f"Loading model from: {model_path}")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"Model loaded successfully!")
    print(f"Model type: {type(model)}")
    
    # Check features
    if hasattr(model, 'feature_names_in_'):
        features = model.feature_names_in_
        print(f"Model expects {len(features)} features:")
        for i, feature in enumerate(features):
            print(f"  {i+1:2d}. {feature}")
    elif hasattr(model, 'n_features_in_'):
        print(f"Model expects {model.n_features_in_} features (names not available)")
    else:
        print("Could not determine feature count")
    
    # Check classes
    if hasattr(model, 'classes_'):
        print(f"Model classes: {model.classes_}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

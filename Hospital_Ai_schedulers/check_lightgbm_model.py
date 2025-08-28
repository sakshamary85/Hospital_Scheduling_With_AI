#!/usr/bin/env python3
import pickle
import lightgbm as lgb

try:
    # Load the model
    model_path = r"C:\Users\saksh\OneDrive\Desktop\No-show_Hospital\Medical-Appointment-No-shows-prediction\model_save\no_show_model.pkl"
    print(f"Loading LightGBM model from: {model_path}")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    print(f"Model loaded successfully!")
    print(f"Model type: {type(model)}")
    
    # LightGBM specific checks
    if hasattr(model, 'feature_name'):
        features = model.feature_name()
        print(f"\nModel expects {len(features)} features:")
        for i, feature in enumerate(features):
            print(f"  {i+1:2d}. {feature}")
    else:
        print("\nNo feature names found in model")
    
    # Check model info
    if hasattr(model, 'num_feature'):
        print(f"Number of features: {model.num_feature()}")
    
    if hasattr(model, 'num_class'):
        print(f"Number of classes: {model.num_class()}")
    
    # Try to get feature importance
    if hasattr(model, 'feature_importance'):
        print(f"Feature importance available: Yes")
    
    # Check if we can make a prediction with dummy data
    print(f"\nTesting with dummy data...")
    
    # Create dummy data with 98 features (as error suggested)
    dummy_data = [[0.0] * 98]  # 98 features, all 0
    
    try:
        prediction = model.predict(dummy_data)
        print(f"✅ Prediction successful with 98 features!")
        print(f"Prediction shape: {prediction.shape}")
        print(f"Prediction type: {type(prediction)}")
        
        if len(prediction) > 0:
            print(f"Sample prediction: {prediction[0]}")
            
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        
        # Try with different number of features
        for num_features in [17, 50, 75, 100]:
            try:
                dummy_data = [[0.0] * num_features]
                prediction = model.predict(dummy_data)
                print(f"✅ Prediction successful with {num_features} features!")
                break
            except:
                continue
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

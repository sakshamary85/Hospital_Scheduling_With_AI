"""
ML Model Integration Module

Handles loading and inference from the existing trained ML model
for patient no-show prediction.
"""

import pickle
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLModelIntegration:
    """
    Integrates with existing trained ML model for no-show prediction.
    
    This class handles:
    - Loading the trained model from Jupyter notebook
    - Preprocessing patient data for inference
    - Making predictions and returning probabilities
    """
    
    def __init__(self, model_path: str, scaler_path: Optional[str] = None):
        """
        Initialize ML model integration.
        
        Args:
            model_path: Path to the trained ML model file (.pkl, .joblib, etc.)
            scaler_path: Path to the fitted scaler if data needs normalization
        """
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path) if scaler_path else None
        self.model = None
        self.scaler = None
        self.feature_names = None
        
        self._load_model()
        self._load_scaler()
    
    def _load_model(self):
        """Load the trained ML model from file."""
        try:
            if self.model_path.suffix == '.joblib':
                self.model = joblib.load(self.model_path)
            else:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
            
            logger.info(f"Successfully loaded ML model from {self.model_path}")
            
            # Try to extract feature names if available
            if hasattr(self.model, 'feature_names_in_'):
                self.feature_names = self.model.feature_names_in_
            elif hasattr(self.model, 'feature_names'):
                self.feature_names = self.feature_names
                
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            raise
    
    def _load_scaler(self):
        """Load the fitted scaler if provided."""
        if self.scaler_path and self.scaler_path.exists():
            try:
                if self.scaler_path.suffix == '.joblib':
                    self.scaler = joblib.load(self.scaler_path)
                else:
                    with open(self.scaler_path, 'rb') as f:
                        self.scaler = joblib.load(f)
                logger.info(f"Successfully loaded scaler from {self.scaler_path}")
            except Exception as e:
                logger.warning(f"Failed to load scaler: {e}")
    
    def preprocess_patient_data(self, patient_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocess patient data for ML model inference.
        
        Args:
            patient_data: Dictionary containing patient and appointment features
            
        Returns:
            Preprocessed DataFrame ready for model inference
        """
        # Convert to DataFrame
        df = pd.DataFrame([patient_data])
        
        # Handle missing values
        df = df.fillna(0)
        
        # Ensure all required features are present
        if self.feature_names is not None:
            missing_features = set(self.feature_names) - set(df.columns)
            if missing_features:
                for feature in missing_features:
                    df[feature] = 0
            # Reorder columns to match model expectations
            df = df[self.feature_names]
        
        # Apply scaling if scaler is available
        if self.scaler is not None:
            df = pd.DataFrame(
                self.scaler.transform(df),
                columns=df.columns,
                index=df.index
            )
        
        return df
    
    def predict_no_show_probability(self, patient_data: Dict[str, Any]) -> float:
        """
        Predict the probability of patient no-show.
        
        Args:
            patient_data: Dictionary containing patient and appointment features
            
        Returns:
            Probability of no-show (0.0 to 1.0)
        """
        try:
            # Preprocess data
            processed_data = self.preprocess_patient_data(patient_data)
            
            # Make prediction
            if hasattr(self.model, 'predict_proba'):
                # Get probability of positive class (no-show)
                proba = self.model.predict_proba(processed_data)
                # Assuming positive class is at index 1 (no-show)
                no_show_prob = proba[0][1] if proba.shape[1] > 1 else proba[0][0]
            else:
                # If model doesn't have predict_proba, use predict
                prediction = self.model.predict(processed_data)
                no_show_prob = float(prediction[0])
            
            logger.info(f"Predicted no-show probability: {no_show_prob:.3f}")
            return float(no_show_prob)
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_with_full_output(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get complete model prediction output including prediction and probabilities.
        
        Args:
            patient_data: Dictionary containing patient and appointment features
            
        Returns:
            Dictionary with prediction, no-show probability, and show probability
        """
        try:
            # Preprocess data
            processed_data = self.preprocess_patient_data(patient_data)
            
            # Get prediction
            prediction = self.model.predict(processed_data)
            prediction_label = prediction[0]
            
            # Get probabilities
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(processed_data)
                if proba.shape[1] == 2:
                    # Binary classification: [no-show, show]
                    no_show_prob = float(proba[0][0])
                    show_prob = float(proba[0][1])
                else:
                    # Single probability output
                    no_show_prob = float(proba[0][0])
                    show_prob = 1.0 - no_show_prob
            else:
                # Fallback if no predict_proba
                no_show_prob = float(prediction[0])
                show_prob = 1.0 - no_show_prob
            
            # Convert prediction to readable format
            if isinstance(prediction_label, (int, float)):
                prediction_text = "No-show" if prediction_label == 1 else "Show"
            else:
                prediction_text = str(prediction_label)
            
            result = {
                "prediction": prediction_text,
                "no_show_probability": no_show_prob,
                "show_probability": show_prob
            }
            
            logger.info(f"Full prediction output: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Full prediction failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        info = {
            "model_path": str(self.model_path),
            "model_type": type(self.model).__name__,
            "scaler_loaded": self.scaler is not None,
            "feature_names": self.feature_names.tolist() if self.feature_names is not None else None
        }
        
        # Add model-specific information
        if hasattr(self.model, 'n_features_in_'):
            info["n_features"] = self.model.n_features_in_
        if hasattr(self.model, 'classes_'):
            info["classes"] = self.model.classes_.tolist()
            
        return info


# Example usage and testing
if __name__ == "__main__":
    # Example patient data structure
    sample_patient = {
        "age": 45,
        "gender": 1,  # 1 for male, 0 for female
        "appointment_day": 15,  # day of month
        "appointment_month": 6,  # month
        "appointment_year": 2024,
        "appointment_hour": 14,  # 24-hour format
        "waiting_time": 30,  # minutes
        "previous_appointments": 2,
        "no_shows_history": 1,
        "scheduled_day": 10,  # days before appointment
        "neighborhood": "Downtown",
        "scholarship": 0,  # 1 if has scholarship, 0 otherwise
        "hypertension": 0,
        "diabetes": 0,
        "alcoholism": 0,
        "handicap": 0,
        "sms_received": 1
    }
    
    # Note: Replace with actual model path
    # ml_integration = MLModelIntegration("path/to/your/model.pkl")
    # prob = ml_integration.predict_no_show_probability(sample_patient)
    # print(f"No-show probability: {prob:.3f}")

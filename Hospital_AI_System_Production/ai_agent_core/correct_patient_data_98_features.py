#!/usr/bin/env python3
"""
Correct Patient Data Structure for Your LightGBM Model

This file contains the exact 98 features your model expects.
Use this structure in your test scripts.
"""

def get_correct_patient_data():
    """Get patient data with all 98 features the model expects."""
    return {
        # Basic patient features (17 features)
        "Gender": 1,
        "Age": 35,
        "Scholarship": 0,
        "Hypertension": 0,
        "Diabetes": 0,
        "Alcoholism": 0,
        "Handicap": 0,
        "SmsReceived": 1,
        "LeadDays": 5,
        "ScheduledDayOfWeek": 2,
        "ScheduledDayDay": 15,
        "AppointmentDayDay": 16,
        "AppointmentDayOfWeek": 3,
        "NoShowRate": 0.0,
        "LastShowStatus": 1,
        "AppointmentCount": 3,
        "LastAppointmentDays": 10,
        
        # Neighborhood features (81 one-hot encoded features)
        "Neighbourhood_AEROPORTO": 0,
        "Neighbourhood_ANDORINHAS": 0,
        "Neighbourhood_ANTNIO_HONRIO": 0,
        "Neighbourhood_ARIOVALDO_FAVALESSA": 0,
        "Neighbourhood_BARRO_VERMELHO": 0,
        "Neighbourhood_BELA_VISTA": 0,
        "Neighbourhood_BENTO_FERREIRA": 0,
        "Neighbourhood_BOA_VISTA": 0,
        "Neighbourhood_BONFIM": 0,
        "Neighbourhood_CARATORA": 0,
        "Neighbourhood_CENTRO": 0,
        "Neighbourhood_COMDUSA": 0,
        "Neighbourhood_CONQUISTA": 0,
        "Neighbourhood_CONSOLAO": 0,
        "Neighbourhood_CRUZAMENTO": 0,
        "Neighbourhood_DA_PENHA": 0,
        "Neighbourhood_DE_LOURDES": 0,
        "Neighbourhood_DO_CABRAL": 0,
        "Neighbourhood_DO_MOSCOSO": 0,
        "Neighbourhood_DO_QUADRO": 0,
        "Neighbourhood_ENSEADA_DO_SU": 0,
        "Neighbourhood_ESTRELINHA": 0,
        "Neighbourhood_FONTE_GRANDE": 0,
        "Neighbourhood_FORTE_SO_JOO": 0,
        "Neighbourhood_FRADINHOS": 0,
        "Neighbourhood_GOIABEIRAS": 0,
        "Neighbourhood_GRANDE_VITRIA": 0,
        "Neighbourhood_GURIGICA": 0,
        "Neighbourhood_HORTO": 0,
        "Neighbourhood_ILHA_DAS_CAIEIRAS": 0,
        "Neighbourhood_ILHA_DE_SANTA_MARIA": 0,
        "Neighbourhood_ILHA_DO_BOI": 0,
        "Neighbourhood_ILHA_DO_FRADE": 0,
        "Neighbourhood_ILHA_DO_PRNCIPE": 0,
        "Neighbourhood_ILHAS_OCENICAS_DE_TRINDADE": 0,
        "Neighbourhood_INHANGUET": 0,
        "Neighbourhood_ITARAR": 0,
        "Neighbourhood_JABOUR": 0,
        "Neighbourhood_JARDIM_CAMBURI": 0,
        "Neighbourhood_JARDIM_DA_PENHA": 0,
        "Neighbourhood_JESUS_DE_NAZARETH": 0,
        "Neighbourhood_JOANA_DARC": 0,
        "Neighbourhood_JUCUTUQUARA": 0,
        "Neighbourhood_MARIA_ORTIZ": 0,
        "Neighbourhood_MARUPE": 0,
        "Neighbourhood_MATA_DA_PRAIA": 0,
        "Neighbourhood_MONTE_BELO": 0,
        "Neighbourhood_MORADA_DE_CAMBURI": 0,
        "Neighbourhood_MRIO_CYPRESTE": 0,
        "Neighbourhood_NAZARETH": 0,
        "Neighbourhood_NOVA_PALESTINA": 0,
        "Neighbourhood_PARQUE_INDUSTRIAL": 0,
        "Neighbourhood_PARQUE_MOSCOSO": 0,
        "Neighbourhood_PIEDADE": 0,
        "Neighbourhood_PONTAL_DE_CAMBURI": 0,
        "Neighbourhood_PRAIA_DO_CANTO": 0,
        "Neighbourhood_PRAIA_DO_SU": 0,
        "Neighbourhood_REDENO": 0,
        "Neighbourhood_REPBLICA": 0,
        "Neighbourhood_RESISTNCIA": 0,
        "Neighbourhood_ROMO": 0,
        "Neighbourhood_SANTA_CECLIA": 0,
        "Neighbourhood_SANTA_CLARA": 0,
        "Neighbourhood_SANTA_HELENA": 0,
        "Neighbourhood_SANTA_LUZA": 0,
        "Neighbourhood_SANTA_LCIA": 0,
        "Neighbourhood_SANTA_MARTHA": 0,
        "Neighbourhood_SANTA_TEREZA": 0,
        "Neighbourhood_SANTO_ANDR": 0,
        "Neighbourhood_SANTO_ANTNIO": 0,
        "Neighbourhood_SANTOS_DUMONT": 0,
        "Neighbourhood_SANTOS_REIS": 0,
        "Neighbourhood_SEGURANA_DO_LAR": 0,
        "Neighbourhood_SOLON_BORGES": 0,
        "Neighbourhood_SO_BENEDITO": 0,
        "Neighbourhood_SO_CRISTVO": 0,
        "Neighbourhood_SO_JOS": 0,
        "Neighbourhood_SO_PEDRO": 0,
        "Neighbourhood_TABUAZEIRO": 0,
        "Neighbourhood_UNIVERSITRIO": 0,
        "Neighbourhood_VILA_RUBIM": 0
    }

def set_neighbourhood(patient_data, neighbourhood_name):
    """
    Set a specific neighborhood for the patient.
    
    Args:
        patient_data: Patient data dictionary
        neighbourhood_name: Name of the neighborhood (e.g., "CENTRO", "JARDIM_CAMBURI")
    
    Returns:
        Updated patient data with the specified neighborhood set to 1
    """
    # Reset all neighborhoods to 0
    for key in patient_data.keys():
        if key.startswith("Neighbourhood_"):
            patient_data[key] = 0
    
    # Set the specified neighborhood to 1
    neighbourhood_key = f"Neighbourhood_{neighbourhood_name}"
    if neighbourhood_key in patient_data:
        patient_data[neighbourhood_key] = 1
        print(f"✅ Set neighborhood to: {neighbourhood_name}")
    else:
        print(f"❌ Neighborhood '{neighbourhood_name}' not found")
    
    return patient_data

# Example usage
if __name__ == "__main__":
    print("🏥 Correct Patient Data Structure for Your LightGBM Model")
    print("=" * 70)
    
    # Get the correct structure
    patient_data = get_correct_patient_data()
    
    print(f"📊 Total features: {len(patient_data)}")
    print(f"🔍 Basic features: 17")
    print(f"🏘️  Neighborhood features: 81")
    
    # Show basic features
    print(f"\n📋 Basic Patient Features:")
    basic_features = [k for k in patient_data.keys() if not k.startswith("Neighbourhood_")]
    for feature in basic_features:
        print(f"   {feature}: {patient_data[feature]}")
    
    # Show neighborhood features (first 10)
    print(f"\n🏘️  Neighborhood Features (showing first 10):")
    neighbourhood_features = [k for k in patient_data.keys() if k.startswith("Neighbourhood_")]
    for i, feature in enumerate(neighbourhood_features[:10]):
        print(f"   {feature}: {patient_data[feature]}")
    print(f"   ... and {len(neighbourhood_features) - 10} more")
    
    # Example: Set a specific neighborhood
    print(f"\n🎯 Example: Setting neighborhood to CENTRO")
    patient_data = set_neighbourhood(patient_data, "CENTRO")
    
    print(f"\n✅ Your patient data is now ready with all 98 features!")
    print(f"💡 Use this structure in your test scripts.")

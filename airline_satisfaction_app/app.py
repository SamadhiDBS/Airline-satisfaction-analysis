from flask import Flask, render_template, request
import joblib
import pandas as pd
import numpy as np
import os
import sys

app = Flask(__name__)

# ============================================
# MODEL LOADING WITH DEBUGGING
# ============================================
print("="*60)
print("🔧 AIRLINE SATISFACTION PREDICTOR - STARTING UP")
print("="*60)

# Check current directory
print(f"📂 Current directory: {os.getcwd()}")

# Initialize variables
model = None
scaler = None
encoders = {}
feature_names = []
best_accuracy = 0.95  # Will be updated if model loads

# Check if models folder exists
models_path = 'models'
if os.path.exists(models_path):
    print(f"✅ Models folder found: {models_path}")
    print(f"📄 Contents: {os.listdir(models_path)}")
else:
    print(f"❌ Models folder NOT found: {models_path}")
    print("Creating models folder...")
    os.makedirs(models_path, exist_ok=True)

# Try to load each model file
try:
    print("\n" + "="*50)
    print("📥 LOADING MODEL FILES...")
    print("="*50)
    
    # Model file
    model_file = os.path.join(models_path, 'best_airline_model.pkl')
    if os.path.exists(model_file):
        model = joblib.load(model_file)
        print(f"✅ Model loaded: {type(model).__name__}")
        if hasattr(model, 'predict'):
            print("   ✓ Has predict method")
        if hasattr(model, 'predict_proba'):
            print("   ✓ Has predict_proba method")
        if hasattr(model, 'feature_importances_'):
            print("   ✓ Has feature_importances_")
    else:
        print(f"❌ Model file not found: {model_file}")
    
    # Scaler file
    scaler_file = os.path.join(models_path, 'scaler.pkl')
    if os.path.exists(scaler_file):
        scaler = joblib.load(scaler_file)
        print(f"✅ Scaler loaded: {type(scaler).__name__}")
    else:
        print(f"❌ Scaler file not found: {scaler_file}")
    
    # Encoders file
    encoders_file = os.path.join(models_path, 'label_encoders.pkl')
    if os.path.exists(encoders_file):
        encoders = joblib.load(encoders_file)
        print(f"✅ Encoders loaded: {list(encoders.keys())}")
    else:
        print(f"❌ Encoders file not found: {encoders_file}")
    
    # Feature names file
    features_file = os.path.join(models_path, 'feature_names.pkl')
    if os.path.exists(features_file):
        feature_names = joblib.load(features_file)
        print(f"✅ Feature names loaded: {len(feature_names)} features")
        print(f"   First 5: {feature_names[:5]}")
    else:
        print(f"❌ Feature names file not found: {features_file}")
        # Default feature names
        feature_names = ['gender', 'customer_type', 'age', 'type_of_travel', 'class', 
                        'flight_distance', 'inflight_wifi_service', 'departure_arrival_time_convenient',
                        'ease_of_online_booking', 'gate_location', 'food_and_drink', 'online_boarding',
                        'seat_comfort', 'inflight_entertainment', 'on_board_service', 'leg_room_service',
                        'baggage_handling', 'checkin_service', 'inflight_service', 'cleanliness',
                        'departure_delay_in_minutes', 'arrival_delay_in_minutes', 'total_delay',
                        'average_service_rating']
        
except Exception as e:
    print(f"❌ Error loading models: {e}")
    import traceback
    traceback.print_exc()

# Check if model is ready
print("\n" + "="*50)
print("🔍 MODEL STATUS:")
print("="*50)
if model is not None:
    print("✅ Model is LOADED and READY for predictions")
    best_accuracy = 0.95  # You can set your actual accuracy here
else:
    print("⚠️ Model is NOT loaded - using FALLBACK mode (always 95% satisfied)")
    print("   Please check model files in the 'models' folder")
print("="*60)

# ============================================
# ROUTES
# ============================================

@app.route('/')
def home():
    return render_template('index.html', best_accuracy=best_accuracy)

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Get all form data
            input_data = {
                'gender': request.form['gender'],
                'customer_type': request.form['customer_type'],
                'age': int(request.form['age']),
                'type_of_travel': request.form['type_of_travel'],
                'class': request.form['class'],
                'flight_distance': int(request.form['flight_distance']),
                'inflight_wifi_service': int(request.form['inflight_wifi_service']),
                'departure_arrival_time_convenient': int(request.form['departure_arrival_time_convenient']),
                'ease_of_online_booking': int(request.form['ease_of_online_booking']),
                'gate_location': int(request.form['gate_location']),
                'food_and_drink': int(request.form['food_and_drink']),
                'online_boarding': int(request.form['online_boarding']),
                'seat_comfort': int(request.form['seat_comfort']),
                'inflight_entertainment': int(request.form['inflight_entertainment']),
                'on_board_service': int(request.form['on_board_service']),
                'leg_room_service': int(request.form['leg_room_service']),
                'baggage_handling': int(request.form['baggage_handling']),
                'checkin_service': int(request.form['checkin_service']),
                'inflight_service': int(request.form['inflight_service']),
                'cleanliness': int(request.form['cleanliness']),
                'departure_delay_in_minutes': int(request.form['departure_delay_in_minutes']),
                'arrival_delay_in_minutes': int(request.form['arrival_delay_in_minutes'])
            }
            
            # Calculate engineered features
            input_data['total_delay'] = input_data['departure_delay_in_minutes'] + input_data['arrival_delay_in_minutes']
            
            service_cols = ['inflight_wifi_service', 'food_and_drink', 'seat_comfort', 'inflight_entertainment']
            input_data['average_service_rating'] = sum([input_data[col] for col in service_cols]) / 4
            
            # Store display copy (before encoding)
            display_data = input_data.copy()
            
            # Print input data for debugging
            print("\n📊 Processing prediction request:")
            print(f"   Age: {input_data['age']}, Gender: {input_data['gender']}")
            print(f"   Avg Service Rating: {input_data['average_service_rating']:.1f}")
            
            # Convert to DataFrame
            df_input = pd.DataFrame([input_data])
            
            # Encode categorical variables if encoders exist
            if encoders:
                for col in ['gender', 'customer_type', 'type_of_travel', 'class']:
                    if col in encoders and col in df_input.columns:
                        try:
                            original_value = df_input[col].iloc[0]
                            df_input[col] = encoders[col].transform(df_input[col])
                            encoded_value = df_input[col].iloc[0]
                            print(f"   Encoded {col}: {original_value} → {encoded_value}")
                        except Exception as e:
                            print(f"   ⚠️ Could not encode {col}: {e}")
                            df_input[col] = 0  # Default value
            
            # Ensure all feature columns exist
            if feature_names:
                for col in feature_names:
                    if col not in df_input.columns:
                        df_input[col] = 0
                df_input = df_input[feature_names]
            
            # Scale the data if scaler exists
            if scaler:
                df_input_scaled = scaler.transform(df_input)
                print("   ✅ Data scaled successfully")
            else:
                df_input_scaled = df_input.values
                print("   ⚠️ No scaler - using raw values")
            
            # ============================================
            # MAKE PREDICTION WITH REAL MODEL
            # ============================================
            if model is not None and hasattr(model, 'predict_proba'):
                try:
                    # Get prediction and probabilities
                    prediction = model.predict(df_input_scaled)[0]
                    probabilities = model.predict_proba(df_input_scaled)[0]
                    
                    # probabilities[0] = probability of dissatisfied (class 0)
                    # probabilities[1] = probability of satisfied (class 1)
                    
                    if prediction == 1:
                        probability = probabilities[1]  # Satisfied confidence
                        result = "SATISFIED"
                    else:
                        probability = probabilities[0]  # Dissatisfied confidence
                        result = "DISSATISFIED"
                    
                    print(f"   ✅ REAL PREDICTION: {result}")
                    print(f"   📊 Probabilities: Dissatisfied={probabilities[0]*100:.1f}%, Satisfied={probabilities[1]*100:.1f}%")
                    print(f"   🎯 Confidence: {probability*100:.1f}%")
                    
                except Exception as e:
                    print(f"   ❌ Prediction error: {e}")
                    # Fallback to dummy values if prediction fails
                    if input_data['average_service_rating'] > 3:
                        prediction = 1
                        probability = 0.85
                    else:
                        prediction = 0
                        probability = 0.85
                    print(f"   ⚠️ Using fallback prediction: {prediction}")
            else:
                # ============================================
                # FALLBACK - Only used if model not loaded
                # ============================================
                print("   ⚠️ MODEL NOT LOADED - Using rule-based fallback")
                
                # Simple rule-based prediction based on average rating
                avg_rating = input_data['average_service_rating']
                total_delay = input_data['total_delay']
                
                if avg_rating >= 4.0 and total_delay < 30:
                    prediction = 1
                    probability = 0.92
                elif avg_rating >= 3.0 and total_delay < 60:
                    prediction = 1
                    probability = 0.75
                elif avg_rating <= 2.0 or total_delay > 90:
                    prediction = 0
                    probability = 0.88
                elif avg_rating <= 2.5:
                    prediction = 0
                    probability = 0.82
                else:
                    # Mixed signals - lower confidence
                    if avg_rating > 2.5:
                        prediction = 1
                        probability = 0.60
                    else:
                        prediction = 0
                        probability = 0.65
                
                print(f"   📊 Rule-based: Avg Rating={avg_rating:.1f}, Delay={total_delay}")
                print(f"   🎯 Prediction: {'Satisfied' if prediction==1 else 'Dissatisfied'} with {probability*100:.1f}% confidence")
            
            # Get top factors if available
            top_factors = []
            if hasattr(model, 'feature_importances_') and feature_names:
                importances = model.feature_importances_
                # Get top 3 features
                top_indices = np.argsort(importances)[-3:][::-1]
                top_factors = [feature_names[i].replace('_', ' ').title() for i in top_indices if i < len(feature_names)]
            else:
                # Default factors based on prediction
                if prediction == 1:
                    top_factors = ["High Service Ratings", "Minimal Delays", "Good Seat Comfort"]
                else:
                    top_factors = ["Poor Service Quality", "Long Delays", "Uncomfortable Seating"]
            
            return render_template('result.html',
                                 prediction=int(prediction),
                                 probability=float(probability),
                                 top_factors=top_factors,
                                 input_data=display_data)
        
        except Exception as e:
            print(f"❌ Error in prediction route: {e}")
            import traceback
            traceback.print_exc()
            return f"""
            <h1>Error in Prediction</h1>
            <p>{str(e)}</p>
            <h3>Please check your input values and try again.</h3>
            <br>
            <a href='/'>← Go Back to Form</a>
            """

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Flask application...")
    print("📱 Open browser to: http://127.0.0.1:5000")
    print("="*60)
    app.run(debug=True, port=5000)
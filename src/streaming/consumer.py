import json
import requests
from google.cloud import pubsub_v1

# Your project ID
PROJECT_ID = "ecommerce-analytics-462115"
SUBSCRIPTION_NAME = "orders-consumer"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

def callback(message):
    """Process streaming order with ML prediction"""
    try:
        order = json.loads(message.data.decode('utf-8'))
        print(f"📦 Received order: {order['InvoiceNo']} - {order['Quantity']} x £{order['UnitPrice']}")
        
        # Calculate actual revenue
        actual_revenue = float(order['Quantity']) * float(order['UnitPrice'])
        
        # Get ML prediction for this order
        prediction_data = {
            'quantity': order['Quantity'],
            'unit_price': order['UnitPrice'], 
            'hour': 14,  # Default values
            'day_of_week': 2
        }
        
        try:
            response = requests.post('http://localhost:5001/predict', json=prediction_data, timeout=5)
            if response.status_code == 200:
                predicted_revenue = response.json()['predicted_revenue']
                print(f"🤖 ML Prediction: £{predicted_revenue:.2f} | Actual: £{actual_revenue:.2f}")
                
                # Alert for high-value orders
                if actual_revenue > 100:
                    print(f"🚨 HIGH VALUE ORDER: £{actual_revenue:.2f}")
            else:
                print(f"⚠️ ML API Error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ ML API unavailable: {e}")
            print(f"💰 Order Revenue: £{actual_revenue:.2f}")
        
        message.ack()  # Acknowledge the message
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        message.ack()

def start_consuming():
    """Start listening for streaming orders"""
    print(f"🔥 Starting to consume orders from {PROJECT_ID}...")
    print(f"📡 Listening on: {subscription_path}")
    print("💡 Make sure ML API is running on http://localhost:5001")
    print("=" * 50)
    
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    
    try:
        streaming_pull_future.result()  # Keep listening
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        print("\n🛑 Consumer stopped")

if __name__ == "__main__":
    start_consuming()
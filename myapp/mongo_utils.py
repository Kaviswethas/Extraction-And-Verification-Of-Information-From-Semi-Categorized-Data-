from pymongo import MongoClient

def get_mongo_db():
    try:
        client = MongoClient('mongodb+srv://rac:drdo@cluster0.uc4rbyd.mongodb.net/')  # Make sure the URI is correct
        db = client['rac_drdo']  # Replace with your actual database name
        print("MongoDB connection successful.")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

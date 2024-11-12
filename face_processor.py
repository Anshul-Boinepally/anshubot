import face_recognition
import numpy as np
import json
import os
from PIL import Image
import firebase_admin
from firebase_admin import credentials, storage
from io import BytesIO

class FaceProcessor:
    def __init__(self):
        # Initialize Firebase
        cred_dict = json.loads(os.environ['FIREBASE_CREDENTIALS'])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'anshubot-b72c7'
        })
        
        # Initialize known faces
        self.known_faces = {
            'anshul': {
                'name': 'Anshul',
                'relationship': 'boyfriend',
                'encodings': []
            },
            'aarya': {
                'name': 'Aarya',
                'relationship': 'me',
                'encodings': []
            }
        }
        
    def add_reference_photo(self, image_path, person_key):
        """Add a reference photo for a person"""
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            # Get face encodings
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                self.known_faces[person_key]['encodings'].extend(face_encodings)
                return True
            return False
        except Exception as e:
            print(f"Error adding reference photo: {e}")
            return False

    def process_photo(self, image_data):
        try:
            # Convert image data to numpy array
            image = face_recognition.load_image_file(BytesIO(image_data))
            
            # Find faces in the image
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces = []
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Check against known faces
                matches = {}
                for person_key, person_data in self.known_faces.items():
                    if person_data['encodings']:
                        # Compare with all known encodings for this person
                        results = face_recognition.compare_faces(
                            person_data['encodings'], 
                            face_encoding,
                            tolerance=0.6
                        )
                        if any(results):
                            matches[person_key] = person_data
                
                top, right, bottom, left = face_location
                faces.append({
                    'rectangle': {
                        'top': top,
                        'right': right,
                        'bottom': bottom,
                        'left': left
                    },
                    'person': matches.get(next(iter(matches), None))
                })
            
            return faces
            
        except Exception as e:
            print(f"Error processing photo: {e}")
            return []

    def handle_query(self, query):
        query = query.lower()
        
        # Parse query to understand intent
        if "show" in query and "picture" in query:
            if "boyfriend and i" in query or "us" in query:
                return self._get_photos_of(['anshul', 'aarya'])
            elif "me" in query:
                return self._get_photos_of(['aarya'])
            elif "anshul" in query or "boyfriend" in query:
                return self._get_photos_of(['anshul'])
        
        return []
    
    def _get_photos_of(self, people_keys, limit=5):
        bucket = storage.bucket()
        photos = []
        
        # Get all photo metadata
        blobs = bucket.list_blobs(prefix='metadata/')
        
        for blob in blobs:
            metadata = json.loads(blob.download_as_string())
            
            # Check if all requested people are in the photo
            people_found = set()
            for face in metadata.get('faces', []):
                if face.get('person') and face['person']['name'].lower() in people_keys:
                    people_found.add(face['person']['name'].lower())
            
            if all(person in people_found for person in people_keys):
                photos.append(metadata)
                
                if len(photos) >= limit:
                    break
        
        return photos

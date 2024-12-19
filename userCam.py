from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
import os
import traceback
import cv2
app = Flask(__name__)
CORS(app)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
nose_cascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(__file__), 'haarcascade_mcs_nose.xml'))

@app.route('/video_frame', methods=['POST'])
def handle_video_frame():
    try:
        data = request.json
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame data provided'}), 400

        frame_data = data['frame']
        img_bytes = base64.b64decode(frame_data)
        img_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Failed to decode image'}), 500

        # Convert the frame to grayscale for face detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the frame
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5,flags=cv2.CASCADE_SCALE_IMAGE)
        noses = nose_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)
        if len(faces) > 0:
            first_face = faces[0]
        else:
            first_face = None

        if len(noses) > 0:
            first_nose = noses[0]
        else:
            first_nose = None

        if first_face is not None and first_nose is not None:
            x_face, y_face, w_face, h_face = first_face
            x1_face = x_face + w_face
            y1_face = y_face + h_face
            xmd_face = round(x_face + w_face / 2)

            x_nose, y_nose, w_nose, h_nose = first_nose
            xmd_nose, ymd_nose = x_nose + w_nose // 2, y_nose + h_nose // 2
            cv2.rectangle(frame, (x_face, y_face), (x_face + w_face, y_face + h_face), (255, 0, 0), 2)
            cv2.rectangle(frame, (x_nose, y_nose), (x_nose + w_nose, y_nose + h_nose), (0, 255, 0), 2)  
            distance = abs(xmd_face - xmd_nose)

            if distance > 2:
                print("NOOOOOOOOOOOO")
             
        ret, buffer = cv2.imencode('.jpg', frame, [
            cv2.IMWRITE_JPEG_QUALITY, 60,
            cv2.IMWRITE_JPEG_OPTIMIZE, 1
        ])
        
        if not ret:
            return jsonify({'error': 'Failed to encode processed frame'}), 500
            
        processed_frame = base64.b64encode(buffer).decode('utf-8')
        return jsonify({'processed_frame': f'data:image/jpeg;base64,{processed_frame}'})
            
    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('frames', exist_ok=True)  # Ensure the frames directory exists
    app.run(host='0.0.0.0', port=5000, debug=True)
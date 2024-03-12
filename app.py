from flask import Flask, render_template, request, flash, redirect
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from pymongo import MongoClient
import os

app = Flask(__name__)

# Load the saved model
model = load_model("my_models.h5")

# Define MongoDB connection URI
MONGODB_URI = "mongodb+srv://prasanga:cit340@cluster0.vioooj7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a MongoClient object
client = MongoClient(MONGODB_URI)

# Select the database and collection
db = client['Prasanga']
collection = db['data']
def download_image(file_id, destination_folder):
    # Query the database to retrieve the document containing the image data
    document = collection.find_one({"_id": bson.ObjectId(file_id)})

    if document:
        # Extract the image data
        image_data = document['image_data']

        # Specify the destination file path
        destination_file_path = os.path.join(destination_folder, document['filename'])

        # Save the image data to a file
        with open(destination_file_path, 'wb') as file:
            file.write(image_data)

        print("Image downloaded successfully:", destination_file_path)
    else:
        print("Document not found.")

# Usage example
download_image("<file_id>", "/uploads")
# Define a function to preprocess the image before feeding it to the model
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(32, 32))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalization
    img_array = img_array.reshape((1,) + img_array.shape)
    return img_array

# Ensure 'uploads' directory exists
UPLOADS_DIR = 'uploads'
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            # Save the uploaded file
            filename = file.filename
            file_path = os.path.join(UPLOADS_DIR, filename)
            file.save(file_path)
            # Preprocess the uploaded image
            processed_image = preprocess_image(file_path)
            # Perform prediction
            prediction = model.predict(processed_image)
            # Assuming binary classification with a threshold of 0.5
            if prediction[0][0] > 0.5:
                result = "Male"
            else:
                result = "Female"
            # Insert the filename and prediction result into MongoDB
            db_entry = {"filename": filename, "prediction": result}
            collection.insert_one(db_entry)
    return render_template('index.html', result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

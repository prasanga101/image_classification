from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

app = Flask(__name__)

# Load the saved model
model = load_model("my_models.h5")

# Define a function to preprocess the image before feeding it to the model
def preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(32, 32))
    img_array = image.img_to_array(img)
    img_array = img_array / 255.0  # Normalization
    img_array = img_array.reshape((1,) + img_array.shape)
    return img_array

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
            file_path = os.path.join('uploads', filename)
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
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)

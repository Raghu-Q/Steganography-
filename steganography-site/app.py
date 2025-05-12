from flask import Flask, render_template, request, send_file
from io import BytesIO
from PIL import Image

app = Flask(__name__)

def encode_image(img, msg):
    length = len(msg)
    if length > 255:
        print("Text too long! (don't exceed 255 characters)")
        return False
    if img.mode != 'RGB':
        img = img.convert('RGB')  # Convert to RGB if not already

    encoded = img.copy()
    width, height = img.size
    index = 0

    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            if row == 0 and col == 0:
                asc = length
            elif index < length:
                c = msg[index]
                asc = ord(c)
                index += 1
            else:
                asc = r
            encoded.putpixel((col, row), (asc, g, b))

    return encoded

def decode_image(img):
    width, height = img.size
    msg = ""
    length = 0
    index = 0

    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            if row == 0 and col == 0:
                length = r
            elif index < length:
                msg += chr(r)
                index += 1
            else:
                break

    return msg

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/encode', methods=['POST'])
def encode():
    img_file = request.files.get('img_file')
    msg = request.form.get('msg')

    if not img_file or not msg:
        return render_template('result.html', message="Please provide an image and a message.")

    try:
        original_image = Image.open(img_file)
        encoded_image = encode_image(original_image, msg)
        if encoded_image:
            img_buffer = BytesIO()
            encoded_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            return send_file(img_buffer, mimetype='image/png', as_attachment=True, download_name='encoded_image.png')
        else:
            return render_template('result.html', message="Failed to encode the message.")
    except Exception as e:
        return render_template('result.html', message=f"An error occurred: {str(e)}")

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        img_file = request.files.get('img_file')

        if not img_file:
            return render_template('result.html', message="Please provide an image.")

        try:
            encoded_image = Image.open(img_file)
            decoded_message = decode_image(encoded_image)
            return render_template('result.html', message=f"Decoded message: {decoded_message}")
        except Exception as e:
            return render_template('result.html', message=f"An error occurred: {str(e)}")
    return render_template('decode.html')

if __name__ == '__main__':
    app.run(debug=True)
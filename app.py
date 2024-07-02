from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import uuid
from moviepy.editor import VideoFileClip
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov'}

# Ensure the temporary upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            try:
                gif_path = convert_to_gif(file_path)
                return_value = send_file(gif_path, mimetype='image/gif', as_attachment=True, download_name='converted.gif')
                
                # Add a small delay before attempting to delete files
                time.sleep(1)
                
                # Use try-except blocks for file deletion
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting input file: {str(e)}")
                
                try:
                    os.remove(gif_path)
                except Exception as e:
                    print(f"Error deleting output file: {str(e)}")
                
                return return_value
            except Exception as e:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as delete_error:
                        print(f"Error deleting input file after conversion error: {str(delete_error)}")
                print(f"Detailed error: {str(e)}")  # This will print to your console
                return f'Error during conversion: {str(e)}'
        else:
            return 'Allowed file types are mp4, avi, mov'
    return render_template('upload.html')

def convert_to_gif(file_path):
    output_path = os.path.splitext(file_path)[0] + '.gif'
    
    clip = None
    try:
        clip = VideoFileClip(file_path).subclip(0, 5)
        clip.write_gif(output_path, fps=10, program='ffmpeg')
        return output_path
    except Exception as e:
        print(f"MoviePy error: {str(e)}")
        raise
    finally:
        if clip:
            clip.close()

if __name__ == '__main__':
    app.run(debug=True)
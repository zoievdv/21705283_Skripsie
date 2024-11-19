from flask import Flask, jsonify, send_from_directory
import subprocess
import os

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))

@app.route('/run-general-plot', methods=['POST'])
def run_scripts():
    try:
        # Define the full path to Python and general_plot.py
        python_executable = r'C:\Users\Zoie\AppData\Local\Programs\Python\Python311\python.exe'
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        general_plot_script = os.path.join(scripts_dir, 'general_plot.py')

        # Run general_plot.py
        app.logger.info("Starting general_plot.py...")
        result_general_plot = subprocess.run(
            [python_executable, general_plot_script],
            cwd=scripts_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        if result_general_plot.returncode != 0:
            error_message = result_general_plot.stderr.decode('utf-8')
            app.logger.error(f"General Plot Script Error: {error_message}")
            return jsonify({"status": "error", "message": error_message}), 500
        app.logger.info("general_plot.py completed successfully.")

        # # Run Emotion_graph.py
        # app.logger.info("Starting Emotion_graph.py...")
        # result_emotion_graph = subprocess.run(
        #     [python_executable, emotion_graph_script],
        #     cwd=scripts_dir,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     timeout=60
        # )
        # if result_emotion_graph.returncode != 0:
        #     error_message = result_emotion_graph.stderr.decode('utf-8')
        #     app.logger.error(f"Emotion Graph Script Error: {error_message}")
        #     return jsonify({"status": "error", "message": error_message}), 500
        # app.logger.info("Emotion_graph.py completed successfully.")

        # # Run Location_Dataframe.py
        # app.logger.info("Starting Location_Dataframe.py...")
        # result_location_dataframe = subprocess.run(
        #     [python_executable, location_dataframe_script],
        #     cwd=scripts_dir,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     timeout=60
        # )
        # if result_location_dataframe.returncode != 0:
        #     error_message = result_location_dataframe.stderr.decode('utf-8')
        #     app.logger.error(f"Location Dataframe Script Error: {error_message}")
        #     return jsonify({"status": "error", "message": error_message}), 500
        # app.logger.info("Location_Dataframe.py completed successfully.")

        # Only general_plot.py ran successfully
        return jsonify({"status": "success", "message": "general_plot.py ran successfully"}), 200

    except subprocess.TimeoutExpired as timeout_error:
        app.logger.error("Timeout Error: general_plot.py took too long")
        return jsonify({"status": "error", "message": "general_plot.py took too long"}), 500

    except FileNotFoundError as fnfe:
        error_message = f"File not found: {str(fnfe)}"
        app.logger.error(error_message)
        return jsonify({"status": "error", "message": error_message}), 500

    except Exception as e:
        error_message = f"Unexpected Error: {str(e)}"
        app.logger.error(error_message)
        return jsonify({"status": "error", "message": error_message}), 500


@app.route('/')
def serve_home():
    # Serve the home page
    return send_from_directory(app.static_folder, 'home_page.html')


@app.route('/<path:path>')
def serve_static(path):
    # Serve static files
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    # Start the Flask server
    app.run(debug=True, port=8000)

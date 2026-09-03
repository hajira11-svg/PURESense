from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PURESense Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 60px;
        }

        .box {
            width: 500px;
            margin: auto;
            padding: 30px;
            border: 1px solid #ccc;
            border-radius: 15px;
        }

        h1 {
            margin-bottom: 30px;
        }

        .reading {
            font-size: 20px;
            margin: 15px;
        }

        .status {
            margin-top: 25px;
            font-size: 24px;
            font-weight: bold;
        }
    </style>
</head>

<body>

<div class="box">

    <h1>PURESense</h1>
    <h3>Food Authenticity Screening System</h3>

    <div class="reading">
        Optical Sensor: --
    </div>

    <div class="reading">
        Electrical Sensor: --
    </div>

    <div class="reading">
        Temperature: -- °C
    </div>

    <div class="status">
        Status: Waiting for Sensor Data
    </div>

</div>

</body>
</html>
"""

@app.route("/")
def dashboard():
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(debug=True)
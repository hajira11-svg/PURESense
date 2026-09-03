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
            background: #f4f6f8;
            margin: 0;
            padding: 40px;
        }

        .container {
            max-width: 1000px;
            margin: auto;
        }

        h1 {
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 35px;
        }

        .cards {
            display: flex;
            gap: 20px;
            justify-content: center;
        }

        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            width: 250px;
            text-align: center;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        }

        .value {
            font-size: 32px;
            font-weight: bold;
            margin-top: 15px;
        }

        .result {
            background: white;
            margin-top: 35px;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        }

        .status {
            font-size: 32px;
            font-weight: bold;
            margin: 15px;
        }

        .confidence {
            font-size: 20px;
            color: #555;
        }

        .footer {
            text-align: center;
            margin-top: 35px;
            color: #777;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>PURESense</h1>

    <div class="subtitle">
        Portable AI-Powered Food Authenticity Screening System
    </div>

    <div class="cards">

        <div class="card">
            <h3>Optical Sensor</h3>
            <div class="value">0.73</div>
        </div>

        <div class="card">
            <h3>Electrical Sensor</h3>
            <div class="value">1.82</div>
        </div>

        <div class="card">
            <h3>Temperature</h3>
            <div class="value">24.6 °C</div>
        </div>

    </div>

    <div class="result">

        <h2>AI SCREENING RESULT</h2>

        <div class="status">
            REFERENCE-LIKE
        </div>

        <div class="confidence">
            Confidence: 94.2%
        </div>

    </div>

    <div class="footer">
        PURESense • Multisensor AI Food Screening
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
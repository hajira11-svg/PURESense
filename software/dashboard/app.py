from flask import Flask, render_template_string, jsonify, request
import os
import joblib
import numpy as np


# ============================================================
# PURESense Flask Dashboard
# ============================================================

app = Flask(__name__)


# ============================================================
# MODEL LOCATION
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "ai",
    "models",
    "puresense_model.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

model_package = None

if os.path.exists(MODEL_FILE):

    model_package = joblib.load(
        MODEL_FILE
    )

    print("PURESense AI model loaded.")

else:

    print(
        "WARNING: AI model not found."
    )

    print(
        "Run: python ai/training/train_model.py.txt"
    )


# ============================================================
# DEMO SENSOR DATA
# ============================================================

sensor_data = {

    "optical": 0.73,

    "electrical": 1.82,

    "temperature": 24.6
}


# ============================================================
# AI PREDICTION
# ============================================================

def predict_sample(
    optical,
    electrical,
    temperature
):

    if model_package is None:

        return {
            "result": "MODEL NOT TRAINED",
            "confidence": 0
        }


    model = model_package["model"]


    features = np.array([
        [
            optical,
            electrical,
            temperature
        ]
    ])


    prediction = model.predict(
        features
    )[0]


    probabilities = model.predict_proba(
        features
    )[0]


    confidence = float(
        np.max(probabilities) * 100
    )


    return {

        "result": str(
            prediction
        ),

        "confidence": round(
            confidence,
            1
        )
    }


# ============================================================
# DASHBOARD HTML
# ============================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>PURESense Dashboard</title>


<style>

* {
    box-sizing: border-box;
}


body {

    margin: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef2f7,
            #ffffff
        );

    color: #1f2937;
}


.header {

    padding: 30px;

    text-align: center;

    background: #111827;

    color: white;
}


.header h1 {

    margin: 0;

    font-size: 42px;
}


.header p {

    margin-top: 8px;

    font-size: 18px;

    color: #d1d5db;
}


.container {

    max-width: 1100px;

    margin: 35px auto;

    padding: 0 20px;
}


.section-title {

    margin-top: 30px;

    margin-bottom: 18px;

    font-size: 24px;
}


.cards {

    display: grid;

    grid-template-columns:
        repeat(
            3,
            1fr
        );

    gap: 20px;
}


.card {

    background: white;

    padding: 25px;

    border-radius: 18px;

    text-align: center;

    box-shadow:
        0 8px 25px
        rgba(
            0,
            0,
            0,
            0.08
        );
}


.card h3 {

    margin-top: 0;

    color: #4b5563;
}


.value {

    font-size: 34px;

    font-weight: bold;

    margin-top: 15px;
}


.unit {

    color: #6b7280;

    font-size: 14px;
}


.result-box {

    margin-top: 30px;

    padding: 35px;

    border-radius: 20px;

    text-align: center;

    background: white;

    box-shadow:
        0 8px 25px
        rgba(
            0,
            0,
            0,
            0.08
        );
}


.result {

    font-size: 34px;

    font-weight: bold;

    margin: 15px;
}


.confidence {

    font-size: 20px;

    color: #4b5563;
}


.info {

    margin-top: 25px;

    padding: 20px;

    background: #f9fafb;

    border-radius: 12px;

    line-height: 1.6;
}


.buttons {

    text-align: center;

    margin-top: 30px;
}


button {

    padding: 13px 25px;

    border: none;

    border-radius: 10px;

    background: #111827;

    color: white;

    font-size: 16px;

    cursor: pointer;
}


button:hover {

    opacity: 0.85;
}


.footer {

    text-align: center;

    margin: 40px;

    color: #6b7280;

    font-size: 14px;
}


@media(max-width: 700px) {

    .cards {

        grid-template-columns:
            1fr;
    }

    .header h1 {

        font-size: 32px;
    }

}

</style>

</head>


<body>


<div class="header">

    <h1>PURESense</h1>

    <p>
        Portable AI-Powered
        Food Authenticity Screening System
    </p>

</div>


<div class="container">


<h2 class="section-title">
    Sensor Measurements
</h2>


<div class="cards">


<div class="card">

    <h3>Optical Sensor</h3>

    <div
        class="value"
        id="optical"
    >
        {{ optical }}
    </div>

    <div class="unit">
        Optical response
    </div>

</div>


<div class="card">

    <h3>Electrical Sensor</h3>

    <div
        class="value"
        id="electrical"
    >
        {{ electrical }}
    </div>

    <div class="unit">
        Electrical response
    </div>

</div>


<div class="card">

    <h3>Temperature</h3>

    <div
        class="value"
        id="temperature"
    >
        {{ temperature }} °C
    </div>

    <div class="unit">
        Sample temperature
    </div>

</div>


</div>


<div class="result-box">

    <h2>
        AI SCREENING RESULT
    </h2>


    <div
        class="result"
        id="result"
    >

        {{ result }}

    </div>


    <div class="confidence">

        Confidence:
        <strong id="confidence">
            {{ confidence }}%
        </strong>

    </div>


    <div class="info">

        PURESense combines
        optical, electrical and
        thermal measurements
        using machine learning
        for rapid preliminary
        food authenticity screening.

    </div>

</div>


<div class="buttons">

    <button
        onclick="runPrediction()"
    >

        Run AI Screening

    </button>

</div>


<div class="footer">

    PURESense Prototype<br>

    Screening result is not a
    substitute for certified
    laboratory analysis.

</div>


</div>


<script>


async function runPrediction() {

    const response =
        await fetch(
            "/api/predict",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    optical:
                        parseFloat(
                            document
                            .getElementById(
                                "optical"
                            )
                            .innerText
                        ),

                    electrical:
                        parseFloat(
                            document
                            .getElementById(
                                "electrical"
                            )
                            .innerText
                        ),

                    temperature:
                        parseFloat(
                            document
                            .getElementById(
                                "temperature"
                            )
                            .innerText
                        )

                })

            }
        );


    const data =
        await response.json();


    document
        .getElementById(
            "result"
        )
        .innerText =
        data.result;


    document
        .getElementById(
            "confidence"
        )
        .innerText =
        data.confidence + "%";

}


</script>


</body>

</html>

"""


# ============================================================
# MAIN DASHBOARD ROUTE
# ============================================================

@app.route("/")
def dashboard():

    prediction = predict_sample(

        sensor_data["optical"],

        sensor_data["electrical"],

        sensor_data["temperature"]

    )


    return render_template_string(

        HTML,

        optical=sensor_data["optical"],

        electrical=sensor_data["electrical"],

        temperature=sensor_data["temperature"],

        result=prediction["result"],

        confidence=prediction["confidence"]

    )


# ============================================================
# AI API
# ============================================================

@app.route(
    "/api/predict",
    methods=["POST"]
)

def api_predict():

    data = request.get_json()


    optical = float(
        data.get(
            "optical",
            sensor_data["optical"]
        )
    )


    electrical = float(
        data.get(
            "electrical",
            sensor_data["electrical"]
        )
    )


    temperature = float(
        data.get(
            "temperature",
            sensor_data["temperature"]
        )
    )


    result = predict_sample(

        optical,

        electrical,

        temperature

    )


    return jsonify(result)


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
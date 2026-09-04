from flask import Flask, render_template_string, jsonify
import os
import joblib
import numpy as np


# ============================================================
# PURESense Dashboard
# Software Simulation Mode
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
# LOAD AI MODEL
# ============================================================

if not os.path.exists(MODEL_FILE):

    print()
    print("ERROR: AI model not found.")
    print()
    print(
        "Run this first:"
    )
    print(
        "python ai/training/train_model.py.txt"
    )

    model_package = None

else:

    model_package = joblib.load(
        MODEL_FILE
    )

    print(
        "PURESense AI model loaded successfully."
    )


# ============================================================
# DEMO SENSOR PROFILES
# ============================================================

SAMPLES = {

    "reference": {

        "optical": 0.76,

        "electrical": 1.48,

        "temperature": 25.1

    },


    "uncertain": {

        "optical": 0.55,

        "electrical": 2.10,

        "temperature": 27.0

    },


    "suspicious": {

        "optical": 0.31,

        "electrical": 3.05,

        "temperature": 29.1

    }

}


current_sample = SAMPLES["reference"].copy()


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_sample(
    optical,
    electrical,
    temperature
):

    if model_package is None:

        return {
            "result": "MODEL NOT AVAILABLE",
            "confidence": 0
        }


    model = model_package["model"]


    values = np.array([
        [
            optical,
            electrical,
            temperature
        ]
    ])


    prediction = model.predict(
        values
    )[0]


    probabilities = model.predict_proba(
        values
    )[0]


    confidence = (
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
# HTML
# ============================================================

HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>PURESense</title>


<style>

* {
    box-sizing: border-box;
}


body {

    margin: 0;

    font-family: Arial, sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef2f7,
            #ffffff
        );

    color: #172033;
}


.header {

    background: #111827;

    color: white;

    padding: 35px;

    text-align: center;
}


.header h1 {

    font-size: 44px;

    margin: 0;
}


.header p {

    margin: 10px 0 0;

    font-size: 18px;

    color: #d1d5db;
}


.container {

    max-width: 1100px;

    margin: 35px auto;

    padding: 0 20px;
}


.notice {

    background: #fff7ed;

    border: 1px solid #fed7aa;

    padding: 15px;

    border-radius: 12px;

    text-align: center;

    margin-bottom: 25px;

    color: #9a3412;
}


.section {

    margin-top: 25px;
}


.section h2 {

    margin-bottom: 18px;
}


.cards {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 20px;
}


.card {

    background: white;

    padding: 25px;

    border-radius: 18px;

    text-align: center;

    box-shadow:
        0 8px 25px
        rgba(0,0,0,0.08);
}


.card h3 {

    color: #6b7280;

    margin-top: 0;
}


.value {

    font-size: 36px;

    font-weight: bold;

    margin: 15px 0;
}


.result-box {

    margin-top: 30px;

    background: white;

    padding: 35px;

    border-radius: 20px;

    text-align: center;

    box-shadow:
        0 8px 25px
        rgba(0,0,0,0.08);
}


.result {

    font-size: 36px;

    font-weight: bold;

    margin: 20px;
}


.confidence {

    font-size: 21px;

    color: #4b5563;
}


.buttons {

    display: flex;

    justify-content: center;

    gap: 15px;

    flex-wrap: wrap;

    margin-top: 30px;
}


button {

    padding: 13px 25px;

    border: none;

    border-radius: 10px;

    background: #111827;

    color: white;

    font-size: 15px;

    cursor: pointer;
}


button:hover {

    opacity: 0.85;
}


.explanation {

    margin-top: 25px;

    background: #f9fafb;

    padding: 20px;

    border-radius: 12px;

    line-height: 1.6;
}


.footer {

    text-align: center;

    padding: 35px;

    color: #6b7280;

    font-size: 14px;
}


@media(max-width: 700px) {

    .cards {

        grid-template-columns: 1fr;

    }

}

</style>

</head>


<body>


<div class="header">

    <h1>PURESense</h1>

    <p>
        Portable AI-Powered
        Food Authenticity Screening
    </p>

</div>


<div class="container">


<div class="notice">

    SOFTWARE DEMONSTRATION MODE —
    Sensor readings are simulated for
    prototype demonstration.

</div>


<div class="section">

    <h2>Multisensor Measurements</h2>


    <div class="cards">


        <div class="card">

            <h3>Optical Sensor</h3>

            <div
                class="value"
                id="optical"
            >
                {{ optical }}
            </div>

            <div>
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

            <div>
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

            <div>
                Sample temperature
            </div>

        </div>


    </div>

</div>


<div class="result-box">

    <h2>AI SCREENING RESULT</h2>


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


    <div class="explanation">

        PURESense combines multiple
        sensing modalities and applies
        machine learning to identify
        patterns in the measured
        sample.

        <br><br>

        The software prototype provides
        preliminary screening categories:
        <strong>
            Reference-like,
            Uncertain,
            and Suspicious.
        </strong>

    </div>


</div>


<div class="buttons">

    <button onclick="loadSample('reference')">
        Reference Sample
    </button>


    <button onclick="loadSample('uncertain')">
        Uncertain Sample
    </button>


    <button onclick="loadSample('suspicious')">
        Suspicious Sample
    </button>

</div>


</div>


<div class="footer">

    PURESense Software Prototype

    <br><br>

    Screening output is not a substitute
    for certified laboratory analysis.

</div>


<script>


async function loadSample(type) {


    const response =
        await fetch(
            "/api/sample/" + type
        );


    const data =
        await response.json();


    document
        .getElementById("optical")
        .innerText =
        data.optical;


    document
        .getElementById("electrical")
        .innerText =
        data.electrical;


    document
        .getElementById("temperature")
        .innerText =
        data.temperature + " °C";


    document
        .getElementById("result")
        .innerText =
        data.result;


    document
        .getElementById("confidence")
        .innerText =
        data.confidence + "%";

}


</script>


</body>

</html>

"""


# ============================================================
# DASHBOARD ROUTE
# ============================================================

@app.route("/")
def dashboard():

    prediction = predict_sample(

        current_sample["optical"],

        current_sample["electrical"],

        current_sample["temperature"]

    )


    return render_template_string(

        HTML,

        optical=current_sample["optical"],

        electrical=current_sample["electrical"],

        temperature=current_sample["temperature"],

        result=prediction["result"],

        confidence=prediction["confidence"]

    )


# ============================================================
# SAMPLE API
# ============================================================

@app.route(
    "/api/sample/<sample_type>"
)
def sample(sample_type):

    global current_sample


    if sample_type not in SAMPLES:

        return jsonify({
            "error":
            "Unknown sample"
        }), 400


    current_sample = SAMPLES[
        sample_type
    ].copy()


    prediction = predict_sample(

        current_sample["optical"],

        current_sample["electrical"],

        current_sample["temperature"]

    )


    return jsonify({

        "optical":
            current_sample["optical"],

        "electrical":
            current_sample["electrical"],

        "temperature":
            current_sample["temperature"],

        "result":
            prediction["result"],

        "confidence":
            prediction["confidence"]

    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )
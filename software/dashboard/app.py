from flask import (
    Flask,
    render_template_string,
    jsonify,
    send_from_directory
)

import os
import csv
import json
from datetime import datetime

import joblib
import numpy as np


# ============================================================
# PURESense — FINAL HACKATHON DASHBOARD
# Software Simulation / Demonstration Mode
# ============================================================

app = Flask(__name__)


# ============================================================
# PROJECT PATHS
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

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

METRICS_FILE = os.path.join(
    RESULTS_DIR,
    "metrics.json"
)

HISTORY_FILE = os.path.join(
    RESULTS_DIR,
    "screening_history.csv"
)


# ============================================================
# LOAD AI MODEL
# ============================================================

model_package = None

if os.path.exists(MODEL_FILE):

    try:
        model_package = joblib.load(
            MODEL_FILE
        )

        print()
        print("=" * 60)
        print("PURESense AI model loaded successfully.")
        print("=" * 60)

    except Exception as error:

        print(
            "ERROR loading AI model:",
            error
        )

else:

    print()
    print("WARNING: AI model not found.")
    print("Run:")
    print("python ai/training/train_model.py.txt")
    print()


# ============================================================
# LOAD MODEL METRICS
# ============================================================

metrics = {
    "accuracy": 0,
    "precision_macro": 0,
    "recall_macro": 0,
    "f1_macro": 0,
    "samples": 0
}

if os.path.exists(METRICS_FILE):

    try:

        with open(
            METRICS_FILE,
            "r"
        ) as file:

            metrics = json.load(file)

    except Exception as error:

        print(
            "Could not load metrics:",
            error
        )


# ============================================================
# DEMONSTRATION SENSOR PROFILES
# ============================================================

SAMPLES = {

    "reference": {

        "name": "Reference Sample",

        "optical": 0.76,

        "electrical": 1.48,

        "temperature": 25.1
    },

    "uncertain": {

        "name": "Uncertain Sample",

        "optical": 0.55,

        "electrical": 2.10,

        "temperature": 27.0
    },

    "suspicious": {

        "name": "Suspicious Sample",

        "optical": 0.31,

        "electrical": 3.05,

        "temperature": 29.1
    }
}


# ============================================================
# CURRENT SAMPLE
# ============================================================

current_sample = SAMPLES[
    "reference"
].copy()


# ============================================================
# SCREENING HISTORY
# ============================================================

def save_history(
    sample_name,
    optical,
    electrical,
    temperature,
    result,
    confidence
):

    file_exists = os.path.exists(
        HISTORY_FILE
    )

    with open(
        HISTORY_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(
            file
        )

        if not file_exists:

            writer.writerow([
                "timestamp",
                "sample",
                "optical",
                "electrical",
                "temperature",
                "result",
                "confidence"
            ])

        writer.writerow([

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            sample_name,

            optical,

            electrical,

            temperature,

            result,

            confidence
        ])


def load_history():

    if not os.path.exists(
        HISTORY_FILE
    ):

        return []

    rows = []

    try:

        with open(
            HISTORY_FILE,
            "r",
            newline=""
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                rows.append(row)

    except Exception as error:

        print(
            "Could not load history:",
            error
        )

    # Show newest results first
    rows.reverse()

    return rows[:10]


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

            "result": "MODEL NOT AVAILABLE",

            "confidence": 0,

            "probabilities": {},

            "explanation": (
                "AI model is not available. "
                "Please train the model first."
            )
        }


    model = model_package[
        "model"
    ]


    values = np.array([[
        optical,
        electrical,
        temperature
    ]])


    prediction = model.predict(
        values
    )[0]


    probabilities = model.predict_proba(
        values
    )[0]


    classes = model.classes_


    probability_dict = {}

    for class_name, probability in zip(
        classes,
        probabilities
    ):

        probability_dict[
            str(class_name)
        ] = round(
            float(probability) * 100,
            1
        )


    confidence = round(
        float(
            np.max(probabilities)
        ) * 100,
        1
    )


    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation_parts = []


    if optical < 0.45:

        explanation_parts.append(
            "Optical response is relatively low."
        )

    elif optical > 0.68:

        explanation_parts.append(
            "Optical response is close to the reference range."
        )

    else:

        explanation_parts.append(
            "Optical response falls in an intermediate range."
        )


    if electrical > 2.6:

        explanation_parts.append(
            "Electrical response is relatively elevated."
        )

    elif electrical < 1.8:

        explanation_parts.append(
            "Electrical response is close to the reference range."
        )

    else:

        explanation_parts.append(
            "Electrical response shows an intermediate pattern."
        )


    if temperature > 28:

        explanation_parts.append(
            "Temperature response is relatively high."
        )

    elif temperature < 26:

        explanation_parts.append(
            "Temperature is close to the reference profile."
        )

    else:

        explanation_parts.append(
            "Temperature falls between the demonstration profiles."
        )


    if prediction == "Reference-like":

        recommendation = (
            "The sample resembles the learned reference pattern."
        )

    elif prediction == "Uncertain":

        recommendation = (
            "The sample shows an intermediate pattern. "
            "Further verification is recommended."
        )

    else:

        recommendation = (
            "The sample differs from the reference pattern. "
            "Further laboratory verification is recommended."
        )


    explanation = " ".join(
        explanation_parts
    )


    return {

        "result": str(
            prediction
        ),

        "confidence": confidence,

        "probabilities": probability_dict,

        "explanation": explanation,

        "recommendation": recommendation
    }


# ============================================================
# RESULT CLASS
# ============================================================

def result_class(result):

    if result == "Reference-like":

        return "reference-result"

    if result == "Uncertain":

        return "uncertain-result"

    if result == "Suspicious":

        return "suspicious-result"

    return "unknown-result"


# ============================================================
# HTML DASHBOARD
# ============================================================

HTML = """

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>PURESense | AI Food Authenticity Screening</title>


<style>

/* ============================================================
   GLOBAL
============================================================ */

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family:
        Inter,
        Arial,
        Helvetica,
        sans-serif;

    background:
        #f4f7fb;

    color:
        #172033;
}


/* ============================================================
   HEADER
============================================================ */

.header {

    background:
        linear-gradient(
            135deg,
            #101827,
            #1e293b
        );

    color: white;

    padding: 34px 25px;

    box-shadow:
        0 4px 18px
        rgba(0,0,0,0.15);
}


.header-inner {

    max-width: 1250px;

    margin: auto;

    display: flex;

    align-items: center;

    justify-content: space-between;

    gap: 25px;
}


.brand h1 {

    margin: 0;

    font-size: 42px;

    letter-spacing: 1px;
}


.brand p {

    margin: 8px 0 0;

    color:
        #cbd5e1;

    font-size: 16px;
}


.status-area {

    display: flex;

    flex-direction: column;

    align-items: flex-end;

    gap: 8px;
}


.status {

    display: inline-flex;

    align-items: center;

    gap: 7px;

    font-size: 13px;

    font-weight: 700;
}


.dot {

    width: 9px;

    height: 9px;

    border-radius: 50%;

    background: #22c55e;
}


/* ============================================================
   MAIN
============================================================ */

.container {

    max-width: 1250px;

    margin: 0 auto;

    padding: 25px 20px 50px;
}


/* ============================================================
   DEMO NOTICE
============================================================ */

.notice {

    background:
        #fff8e7;

    border:
        1px solid #f4d68f;

    border-radius:
        14px;

    padding:
        16px 20px;

    margin-bottom:
        25px;

    line-height:
        1.6;

    color:
        #714d0e;
}


/* ============================================================
   SECTION TITLES
============================================================ */

.section {

    margin-top: 28px;
}


.section-title {

    font-size: 22px;

    margin-bottom: 15px;

    font-weight: 750;
}


/* ============================================================
   SENSOR CARDS
============================================================ */

.cards {

    display:
        grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap:
        18px;
}


.card {

    background:
        white;

    border-radius:
        18px;

    padding:
        23px;

    box-shadow:
        0 7px 25px
        rgba(15,23,42,0.07);

    border:
        1px solid #e8edf5;
}


.sensor-card {

    min-height:
        160px;
}


.card-label {

    color:
        #6b7280;

    font-size:
        14px;

    font-weight:
        700;

    text-transform:
        uppercase;

    letter-spacing:
        0.6px;
}


.sensor-value {

    font-size:
        40px;

    font-weight:
        800;

    margin:
        15px 0 5px;
}


.unit {

    color:
        #64748b;

    font-size:
        13px;
}


/* ============================================================
   RESULT PANEL
============================================================ */

.result-panel {

    margin-top:
        22px;

    background:
        white;

    border-radius:
        20px;

    padding:
        28px;

    box-shadow:
        0 8px 28px
        rgba(15,23,42,0.08);

    border:
        1px solid #e8edf5;

    text-align:
        center;
}


.result-title {

    font-size:
        14px;

    font-weight:
        800;

    letter-spacing:
        1.1px;

    color:
        #64748b;
}


.result {

    display:
        inline-block;

    margin-top:
        13px;

    padding:
        13px 28px;

    border-radius:
        999px;

    font-size:
        28px;

    font-weight:
        800;
}


.reference-result {

    background:
        #dcfce7;

    color:
        #166534;
}


.uncertain-result {

    background:
        #fef3c7;

    color:
        #92400e;
}


.suspicious-result {

    background:
        #fee2e2;

    color:
        #991b1b;
}


.unknown-result {

    background:
        #e5e7eb;

    color:
        #374151;
}


.confidence {

    margin-top:
        16px;

    font-size:
        18px;

    color:
        #475569;
}


.confidence strong {

    color:
        #111827;

    font-size:
        25px;
}


/* ============================================================
   BUTTONS
============================================================ */

.buttons {

    display:
        flex;

    justify-content:
        center;

    flex-wrap:
        wrap;

    gap:
        12px;

    margin-top:
        20px;
}


button {

    border:
        none;

    padding:
        13px 20px;

    border-radius:
        10px;

    background:
        #111827;

    color:
        white;

    cursor:
        pointer;

    font-size:
        14px;

    font-weight:
        700;

    transition:
        0.2s;
}


button:hover {

    transform:
        translateY(-2px);

    opacity:
        0.9;
}


/* ============================================================
   TWO COLUMN
============================================================ */

.two-column {

    display:
        grid;

    grid-template-columns:
        1fr 1fr;

    gap:
        20px;
}


/* ============================================================
   EXPLANATION
============================================================ */

.explanation {

    min-height:
        240px;
}


.explanation-box {

    margin-top:
        15px;

    background:
        #f8fafc;

    border-radius:
        12px;

    padding:
        17px;

    line-height:
        1.65;

    color:
        #475569;
}


.recommendation {

    margin-top:
        14px;

    background:
        #eef2ff;

    padding:
        14px;

    border-radius:
        10px;

    color:
        #3730a3;

    line-height:
        1.55;
}


/* ============================================================
   PROBABILITY BARS
============================================================ */

.probability-row {

    margin:
        17px 0;
}


.probability-header {

    display:
        flex;

    justify-content:
        space-between;

    margin-bottom:
        7px;

    font-size:
        14px;

    font-weight:
        700;
}


.bar {

    height:
        11px;

    background:
        #e5e7eb;

    border-radius:
        20px;

    overflow:
        hidden;
}


.bar-fill {

    height:
        100%;

    background:
        #111827;

    border-radius:
        20px;
}


/* ============================================================
   METRICS
============================================================ */

.metrics-grid {

    display:
        grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap:
        14px;
}


.metric {

    background:
        #f8fafc;

    border:
        1px solid #e5e7eb;

    padding:
        18px;

    text-align:
        center;

    border-radius:
        12px;
}


.metric-number {

    font-size:
        27px;

    font-weight:
        800;

    margin-bottom:
        5px;
}


.metric-label {

    color:
        #64748b;

    font-size:
        12px;

    text-transform:
        uppercase;

    letter-spacing:
        0.5px;
}


/* ============================================================
   IMAGES
============================================================ */

.image-card img {

    width:
        100%;

    border-radius:
        12px;

    display:
        block;

    margin-top:
        12px;

    border:
        1px solid #e5e7eb;
}


/* ============================================================
   SENSOR FINGERPRINT
============================================================ */

.fingerprint-bars {

    margin-top:
        15px;
}


.fingerprint-row {

    margin-bottom:
        18px;
}


.fingerprint-head {

    display:
        flex;

    justify-content:
        space-between;

    font-size:
        13px;

    font-weight:
        700;

    margin-bottom:
        7px;
}


.fingerprint-track {

    height:
        15px;

    border-radius:
        20px;

    background:
        #e5e7eb;

    overflow:
        hidden;
}


.fingerprint-fill {

    height:
        100%;

    background:
        #334155;

    border-radius:
        20px;

    transition:
        width 0.4s ease;
}


/* ============================================================
   HISTORY
============================================================ */

.history-table {

    width:
        100%;

    border-collapse:
        collapse;

    margin-top:
        8px;

    font-size:
        13px;
}


.history-table th,
.history-table td {

    border-bottom:
        1px solid #e5e7eb;

    padding:
        11px 8px;

    text-align:
        left;
}


.history-table th {

    color:
        #64748b;

    font-size:
        12px;

    text-transform:
        uppercase;
}


.history-empty {

    padding:
        30px;

    text-align:
        center;

    color:
        #64748b;
}


/* ============================================================
   ARCHITECTURE
============================================================ */

.pipeline {

    display:
        grid;

    grid-template-columns:
        repeat(5, 1fr);

    gap:
        10px;

    align-items:
        center;
}


.pipeline-item {

    background:
        #f8fafc;

    border:
        1px solid #e2e8f0;

    border-radius:
        12px;

    padding:
        17px 10px;

    text-align:
        center;

    font-weight:
        700;

    font-size:
        13px;
}


.pipeline-arrow {

    text-align:
        center;

    font-size:
        20px;

    color:
        #64748b;
}


/* ============================================================
   FOOTER
============================================================ */

.footer {

    text-align:
        center;

    padding:
        30px 20px;

    color:
        #64748b;

    font-size:
        13px;

    line-height:
        1.7;
}


/* ============================================================
   RESPONSIVE
============================================================ */

@media(max-width: 900px) {

    .header-inner {

        flex-direction:
            column;

        text-align:
            center;
    }

    .status-area {

        align-items:
            center;
    }

    .cards,
    .metrics-grid {

        grid-template-columns:
            1fr 1fr;
    }

    .two-column {

        grid-template-columns:
            1fr;
    }

    .pipeline {

        grid-template-columns:
            1fr;
    }
}


@media(max-width: 600px) {

    .brand h1 {

        font-size:
            32px;
    }

    .cards,
    .metrics-grid {

        grid-template-columns:
            1fr;
    }

    .container {

        padding:
            18px 12px 40px;
    }
}

</style>

</head>


<body>


<!-- ============================================================
     HEADER
============================================================ -->

<header class="header">

<div class="header-inner">

<div class="brand">

<h1>PURESense</h1>

<p>
Portable Unified Rapid Evaluation Sensor
for Food Authenticity Screening
</p>

</div>


<div class="status-area">

<div class="status">

<span class="dot"></span>

AI MODEL LOADED

</div>


<div class="status">

<span class="dot"></span>

SYSTEM ONLINE

</div>


<div class="status">

<span class="dot"></span>

SOFTWARE DEMO

</div>

</div>

</div>

</header>


<!-- ============================================================
     MAIN
============================================================ -->

<main class="container">


<!-- ============================================================
     DEMO NOTICE
============================================================ -->

<div class="notice">

<strong>
DEMONSTRATION MODE:
</strong>

The current PURESense MVP uses simulated optical,
electrical, and temperature sensor measurements to
demonstrate the AI screening pipeline.

This prototype is intended for preliminary screening
and is not a substitute for certified laboratory analysis.

</div>


<!-- ============================================================
     SENSOR MEASUREMENTS
============================================================ -->

<section class="section">

<div class="section-title">

Multisensor Measurements

</div>


<div class="cards">


<div class="card sensor-card">

<div class="card-label">

Optical Sensor

</div>

<div
    class="sensor-value"
    id="optical"
>
{{ optical }}
</div>

<div class="unit">

Simulated optical response

</div>

</div>


<div class="card sensor-card">

<div class="card-label">

Electrical Sensor

</div>

<div
    class="sensor-value"
    id="electrical"
>
{{ electrical }}
</div>

<div class="unit">

Simulated electrical response

</div>

</div>


<div class="card sensor-card">

<div class="card-label">

Temperature

</div>

<div
    class="sensor-value"
    id="temperature"
>
{{ temperature }} °C
</div>

<div class="unit">

Sample temperature

</div>

</div>


</div>

</section>


<!-- ============================================================
     AI RESULT
============================================================ -->

<section class="result-panel">

<div class="result-title">

AI SCREENING RESULT

</div>


<div
    id="result"
    class="result {{ result_class }}"
>
{{ result }}
</div>


<div class="confidence">

Model confidence:

<strong id="confidence">
{{ confidence }}%
</strong>

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

</section>


<!-- ============================================================
     EXPLANATION + PROBABILITIES
============================================================ -->

<section class="section">

<div class="two-column">


<div class="card explanation">

<div class="section-title">

AI Interpretation

</div>


<div
    class="explanation-box"
    id="explanation"
>
{{ explanation }}
</div>


<div
    class="recommendation"
    id="recommendation"
>
{{ recommendation }}
</div>

</div>


<div class="card">

<div class="section-title">

Prediction Probabilities

</div>


<div
    id="probabilities"
>

{% for class_name, probability in probabilities.items() %}

<div class="probability-row">

<div class="probability-header">

<span>
{{ class_name }}
</span>

<span>
{{ probability }}%
</span>

</div>

<div class="bar">

<div
    class="bar-fill"
    style="width: {{ probability }}%"
></div>

</div>

</div>

{% endfor %}

</div>

</div>


</div>

</section>


<!-- ============================================================
     SENSOR FINGERPRINT
============================================================ -->

<section class="section">

<div class="card">

<div class="section-title">

Current Multisensor Fingerprint

</div>


<div class="fingerprint-bars">


<div class="fingerprint-row">

<div class="fingerprint-head">

<span>Optical Response</span>

<span id="opticalValue">
{{ optical }}
</span>

</div>

<div class="fingerprint-track">

<div
    class="fingerprint-fill"
    id="opticalBar"
    style="width: {{ optical * 100 }}%"
></div>

</div>

</div>


<div class="fingerprint-row">

<div class="fingerprint-head">

<span>Electrical Response</span>

<span id="electricalValue">
{{ electrical }}
</span>

</div>

<div class="fingerprint-track">

<div
    class="fingerprint-fill"
    id="electricalBar"
    style="width: {{ (electrical / 4) * 100 }}%"
></div>

</div>

</div>


<div class="fingerprint-row">

<div class="fingerprint-head">

<span>Temperature</span>

<span id="temperatureValue">
{{ temperature }} °C
</span>

</div>

<div class="fingerprint-track">

<div
    class="fingerprint-fill"
    id="temperatureBar"
    style="width: {{ ((temperature - 15) / 25) * 100 }}%"
></div>

</div>

</div>


</div>

</div>

</section>


<!-- ============================================================
     MODEL PERFORMANCE
============================================================ -->

<section class="section">

<div class="card">

<div class="section-title">

AI Model Performance

</div>


<div class="metrics-grid">


<div class="metric">

<div class="metric-number">

{{ accuracy }}%

</div>

<div class="metric-label">

Accuracy

</div>

</div>


<div class="metric">

<div class="metric-number">

{{ precision }}%

</div>

<div class="metric-label">

Precision

</div>

</div>


<div class="metric">

<div class="metric-number">

{{ recall }}%

</div>

<div class="metric-label">

Recall

</div>

</div>


<div class="metric">

<div class="metric-number">

{{ f1 }}%

</div>

<div class="metric-label">

F1 Score

</div>

</div>


</div>

</div>

</section>


<!-- ============================================================
     MODEL VISUALIZATIONS
============================================================ -->

<section class="section">

<div class="two-column">


<div class="card image-card">

<div class="section-title">

Confusion Matrix

</div>

<img
    src="/results/confusion_matrix.png"
    alt="PURESense confusion matrix"
>

</div>


<div class="card image-card">

<div class="section-title">

Feature Importance

</div>

<img
    src="/results/feature_importance.png"
    alt="PURESense feature importance"
>

</div>


</div>

</section>


<!-- ============================================================
     SENSOR PROFILES
============================================================ -->

<section class="section">

<div class="card image-card">

<div class="section-title">

Multisensor Reference Profiles

</div>

<img
    src="/results/sensor_profiles.png"
    alt="PURESense sensor profiles"
>

</div>

</section>


<!-- ============================================================
     PIPELINE
============================================================ -->

<section class="section">

<div class="card">

<div class="section-title">

PURESense AI Pipeline

</div>


<div class="pipeline">

<div class="pipeline-item">

Sensor Inputs

</div>

<div class="pipeline-item">

Multisensor Fusion

</div>

<div class="pipeline-item">

Feature Analysis

</div>

<div class="pipeline-item">

Random Forest AI

</div>

<div class="pipeline-item">

Screening Result

</div>

</div>

</div>

</section>


<!-- ============================================================
     HISTORY
============================================================ -->

<section class="section">

<div class="card">

<div class="section-title">

Recent Screening History

</div>


{% if history %}

<table class="history-table">

<thead>

<tr>

<th>Time</th>

<th>Sample</th>

<th>Optical</th>

<th>Electrical</th>

<th>Temperature</th>

<th>Result</th>

<th>Confidence</th>

</tr>

</thead>


<tbody>

{% for row in history %}

<tr>

<td>
{{ row.timestamp }}
</td>

<td>
{{ row.sample }}
</td>

<td>
{{ row.optical }}
</td>

<td>
{{ row.electrical }}
</td>

<td>
{{ row.temperature }}
</td>

<td>
<strong>
{{ row.result }}
</strong>
</td>

<td>
{{ row.confidence }}%
</td>

</tr>

{% endfor %}

</tbody>

</table>

{% else %}

<div class="history-empty">

No screening history yet.
Select a demonstration sample above.

</div>

{% endif %}

</div>

</section>


<!-- ============================================================
     PROJECT INFORMATION
============================================================ -->

<section class="section">

<div class="two-column">


<div class="card">

<div class="section-title">

What PURESense Does

</div>

<p style="line-height:1.7;color:#475569;">

PURESense creates a multidimensional fingerprint
from complementary sensor responses and uses machine
learning to identify whether a sample resembles the
learned reference population.

</p>


<p style="line-height:1.7;color:#475569;">

The current prototype demonstrates three screening
categories:

</p>


<ul style="line-height:1.9;color:#475569;">

<li>Reference-like</li>

<li>Uncertain</li>

<li>Suspicious</li>

</ul>

</div>


<div class="card">

<div class="section-title">

Intended Future Deployment

</div>

<p style="line-height:1.7;color:#475569;">

The software architecture is designed to receive
measurements from physical optical, electrical, and
thermal sensors through a microcontroller such as an
ESP32.

</p>


<p style="line-height:1.7;color:#475569;">

Future development includes experimental data
collection, hardware integration, calibration, and
laboratory validation.

</p>

</div>


</div>

</section>


</main>


<!-- ============================================================
     FOOTER
============================================================ -->

<footer class="footer">

<strong>
PURESense
</strong>

<br>

Portable Unified Rapid Evaluation Sensor for Food
Authenticity Screening

<br><br>

Software prototype • Simulated sensor data •
AI-assisted preliminary screening

<br>

Screening output is not a substitute for certified
laboratory analysis.

</footer>


<!-- ============================================================
     JAVASCRIPT
============================================================ -->

<script>


async function loadSample(type) {

    try {

        const response = await fetch(
            "/api/sample/" + type
        );


        const data = await response.json();


        if (data.error) {

            alert(data.error);

            return;
        }


        // ----------------------------------------------------
        // SENSOR VALUES
        // ----------------------------------------------------

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


        // ----------------------------------------------------
        // RESULT
        // ----------------------------------------------------

        const resultElement =
            document.getElementById("result");


        resultElement.innerText =
            data.result;


        resultElement.className =
            "result " +
            data.result_class;


        // ----------------------------------------------------
        // CONFIDENCE
        // ----------------------------------------------------

        document
            .getElementById("confidence")
            .innerText =
            data.confidence + "%";


        // ----------------------------------------------------
        // EXPLANATION
        // ----------------------------------------------------

        document
            .getElementById("explanation")
            .innerText =
            data.explanation;


        document
            .getElementById("recommendation")
            .innerText =
            data.recommendation;


        // ----------------------------------------------------
        // SENSOR VALUES
        // ----------------------------------------------------

        document
            .getElementById("opticalValue")
            .innerText =
            data.optical;


        document
            .getElementById("electricalValue")
            .innerText =
            data.electrical;


        document
            .getElementById("temperatureValue")
            .innerText =
            data.temperature + " °C";


        // ----------------------------------------------------
        // SENSOR BARS
        // ----------------------------------------------------

        document
            .getElementById("opticalBar")
            .style.width =
            (
                data.optical * 100
            ) + "%";


        document
            .getElementById("electricalBar")
            .style.width =
            (
                (data.electrical / 4) * 100
            ) + "%";


        document
            .getElementById("temperatureBar")
            .style.width =
            (
                (
                    (data.temperature - 15)
                    / 25
                ) * 100
            ) + "%";


        // ----------------------------------------------------
        // PROBABILITY BARS
        // ----------------------------------------------------

        let html = "";


        for (
            const [className, probability]
            of Object.entries(
                data.probabilities
            )
        ) {

            html += `

                <div class="probability-row">

                    <div class="probability-header">

                        <span>
                            ${className}
                        </span>

                        <span>
                            ${probability}%
                        </span>

                    </div>

                    <div class="bar">

                        <div
                            class="bar-fill"
                            style="width:${probability}%"
                        ></div>

                    </div>

                </div>

            `;
        }


        document
            .getElementById("probabilities")
            .innerHTML =
            html;


    } catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

        alert(
            "Could not communicate with the dashboard."
        );
    }
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

        optical=current_sample[
            "optical"
        ],

        electrical=current_sample[
            "electrical"
        ],

        temperature=current_sample[
            "temperature"
        ],

        result=prediction[
            "result"
        ],

        result_class=result_class(
            prediction["result"]
        ),

        confidence=prediction[
            "confidence"
        ],

        probabilities=prediction[
            "probabilities"
        ],

        explanation=prediction.get(
            "explanation",
            ""
        ),

        recommendation=prediction.get(
            "recommendation",
            ""
        ),

        accuracy=round(
            metrics.get(
                "accuracy",
                0
            ) * 100,
            2
        ),

        precision=round(
            metrics.get(
                "precision_macro",
                0
            ) * 100,
            2
        ),

        recall=round(
            metrics.get(
                "recall_macro",
                0
            ) * 100,
            2
        ),

        f1=round(
            metrics.get(
                "f1_macro",
                0
            ) * 100,
            2
        ),

        history=load_history()
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
                "Unknown sample type."

        }), 400


    current_sample = SAMPLES[
        sample_type
    ].copy()


    prediction = predict_sample(

        current_sample[
            "optical"
        ],

        current_sample[
            "electrical"
        ],

        current_sample[
            "temperature"
        ]
    )


    save_history(

        current_sample[
            "name"
        ],

        current_sample[
            "optical"
        ],

        current_sample[
            "electrical"
        ],

        current_sample[
            "temperature"
        ],

        prediction[
            "result"
        ],

        prediction[
            "confidence"
        ]
    )


    return jsonify({

        "optical":
            current_sample[
                "optical"
            ],

        "electrical":
            current_sample[
                "electrical"
            ],

        "temperature":
            current_sample[
                "temperature"
            ],

        "result":
            prediction[
                "result"
            ],

        "result_class":
            result_class(
                prediction[
                    "result"
                ]
            ),

        "confidence":
            prediction[
                "confidence"
            ],

        "probabilities":
            prediction[
                "probabilities"
            ],

        "explanation":
            prediction.get(
                "explanation",
                ""
            ),

        "recommendation":
            prediction.get(
                "recommendation",
                ""
            )

    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "status":
            "online",

        "model_loaded":
            model_package is not None,

        "simulation":
            True

    })


# ============================================================
# SERVE RESULT IMAGES
# ============================================================

@app.route(
    "/results/<path:filename>"
)
def results_file(filename):

    return send_from_directory(

        RESULTS_DIR,

        filename
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("PURESense Dashboard")
    print("=" * 60)

    print(
        "Open in browser:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )
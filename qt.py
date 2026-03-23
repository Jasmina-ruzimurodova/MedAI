from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# 📂 Dataset yuklash
df = pd.read_csv("Diases.csv")
df.columns = df.columns.str.strip()

# ❗ Bo‘sh qiymatlarni to‘ldirish
df = df.fillna("")

# 🔎 Qidiruv funksiyasi (WEIGHT bilan)
def find_disease(user_input):
    user_input = user_input.lower()
    words = user_input.split()

    scores = []

    for i, row in df.iterrows():
        score = 0

        asosiy = str(row["Asosiy simptom"]).lower()
        qoshimcha = str(row["Qo‘shimcha simptom"]).lower()
        subyektiv = str(row["Subyektiv shikoyat"]).lower()

        for word in words:
            if word in asosiy:
                score += 3
            if word in qoshimcha:
                score += 2
            if word in subyektiv:
                score += 1

        scores.append((score, row["disease"]))

    # 🔽 Saralash
    scores.sort(key=lambda x: x[0], reverse=True)

    # ❗ Agar hech narsa topilmasa
    if scores[0][0] == 0:
        return "Aniqlanmadi", []

    main = scores[0][1]

    # 🔁 takrorlarni olib tashlash
    similar = []
    seen = set()

    for score, disease in scores[1:]:
        if disease not in seen and disease != main:
            similar.append(disease)
            seen.add(disease)
        if len(similar) == 5:
            break

    return main, similar


# 🏠 Home sahifa
@app.route("/")
def home():
    return render_template("qt.html")  # html templates ichida bo‘lishi shart


# 📡 Predict API
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    text = data.get("text", "").strip()

    # ❗ Bo‘sh input tekshiruvi
    if not text:
        return jsonify({
            "main": "Iltimos simptom kiriting",
            "similar": []
        })

    main, similar = find_disease(text)

    return jsonify({
        "main": main,
        "similar": similar
    })


# 🚀 Run
if __name__ == "__main__":
    app.run(debug=True)
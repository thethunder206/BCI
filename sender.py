from flask import Flask, request, jsonify

app = Flask(__name__)

current_value = False


@app.route("/set_boolean", methods=["POST"])
def set_boolean():
    global current_value

    data = request.get_json()

    if not data or "value" not in data:
        return jsonify({
            "success": False,
            "message": "Missing 'value' in JSON"
        }), 400

    value = data["value"]

    if not isinstance(value, bool):
        return jsonify({
            "success": False,
            "message": "'value' must be true or false"
        }), 400

    current_value = value

    print(f"Received boolean value: {current_value}")

    return jsonify({
        "success": True,
        "received": current_value
    })


@app.route("/get_boolean", methods=["GET"])
def get_boolean():
    return jsonify({
        "success": True,
        "value": current_value
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

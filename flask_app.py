# flask app to serve the bot

from flask import Flask, send_file, request, jsonify
from bot import Bot, STICKER
from random import randint

app = Flask(__name__)

player = 0
MAX_STICKER = 6


@app.route("/", methods=["GET"])
def index():
    if "p" in request.args:
        player_new = int(request.args["p"])
        if player_new in [0, 1]:
            global player
            player = player_new

    return send_file("static/index.html")


@app.route("/chat", methods=["POST"])
def chat():
    json = request.json
    if not json:
        return jsonify({"reply": "server error"})
    prompt = json["prompt"]
    player_new = int(json["player"])
    if player_new in [0, 1]:
        global player
        player = player_new
    reply = bot.respond(prompt, player)
    if STICKER in reply:
        # return a random sticker with the reply
        return jsonify({
            "reply": reply.replace(STICKER, ""),
            "sticker": randint(1, MAX_STICKER)
        })
    else:
        return jsonify({"reply": reply})


@app.route("/player", methods=["POST"])
def switch():
    json = request.json
    if not json:
        return jsonify({"reply": "server error"})
    player_new = int(json["player"])
    if player_new in [0, 1]:
        global player
        player = player_new
    return jsonify({"player": player})


if __name__ == "__main__":
    from argparse import ArgumentParser
    # get command line args
    parser = ArgumentParser(description="flask app to serve the bot")
    parser.add_argument("model", help="model file")
    args = parser.parse_args()

    bot = Bot()
    bot.load_model(args.model)
    from waitress import serve
    serve(app, port=5050)

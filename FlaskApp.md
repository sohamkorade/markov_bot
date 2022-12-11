# flask app

A simple flask app to serve the bot.

## Requirements

- Python 3.6+
- Flask

## Installation

```bash
pip3 install -r requirements.txt
```

## Usage

1. Create a model and save it as `example.model` (see [here](README.md#basic-usage)).
2. Run the flask app:

```bash
python3 flask_app.py example.model
```
3. Open http://localhost:5050 in your browser.

### Advanced Usage
- To chat with bot1, go to http://localhost:5050/?p=0.
- To chat with bot2, go to http://localhost:5050/?p=1.

## Files
- `static/index.html`: HTML for the web interface.
- `static/script.js`: javascript code.
- `static/style.css`: CSS.

## Notes

- You can add stickers to the `static/stickers` folder to use them randomly in the chat. Change the `MAX_STICKER` variable in `flask_app.py` accordingly.

## TODO
- [ ] themes
- [ ] add option to use stickers


## License

[MIT](LICENSE.md)

# Author

Soham Korade
# markov bot

A simple chatbot that uses markov chains to generate responses. It can be trained on a WhatsApp chat log. Note that your logs are not sent anywhere, everything happens locally.

## Quick demo
1. Clone the repository, or just download the `bot.py` file.
2. Get a WhatsApp chat log, [how?](#how-to-get-a-whatsapp-chat-log)
3. Run `python3 bot.py -train <filename>.txt -b1`
4. Chat with your bot!

## Live demo
I've trained a bot on my own chat logs. You can chat with the bot [here](http://ssoohhaamm.pythonanywhere.com/). Use with caution.


## Usage

### For web interface, see [here](FlaskApp.md).

### Basic usage

```python
import bot
my_bot = bot.Bot()

# Train the bot on a WhatsApp chat log
my_bot.create_model("chatlog.txt")
my_bot.train()

# Save the model to a file
my_bot.save_model("example.model")

# Generate 10 lines of sample chat
my_bot.sample_chat(10)
```

### Interacting with the bot

```python
import bot
my_bot = bot.Bot()

# Load the model from a file
my_bot.load_model("example.model")

# Get a response to a message
my_bot.respond("hi") # output maybe "hello"
```

### Advanced Usage

- You can change number of previous words a word depends on, by changing the `states` parameter in the `train` function. The default value is 3.

	```python
	bot.train(states=2) # train the bot with 2 previous words
	```
- Use custom text transformations to transform the chat log before training. The default transformation function is `query_transform`. You can modify the transformation function to your custom function as follows:

	```python
	def my_transform(raw: str) -> str:
		# do something with raw
		return raw

	bot.query_transform = my_transform # used to transform the query
	bot.reply_transform = my_transform # used to transform the reply
	bot.line_transform = my_transform # used in training to transform each line of the chat log
	```

	For example, this will make your bot SHOUT at you:
	
	```python	
	def shout(raw: str) -> str:
		return raw.upper()
	
	bot.reply_transform = shout
	```

- Use debug mode to print debug messages. Debug mode is disabled by default. To enable debug mode, set `debug` to `True` in the `Bot` class, or
	```python
	my_bot = bot.Bot(debug=True)
	```
- You can block certain words from being used in the chat log. To do this, set `blacklist` to a list of words in the `Bot` class, or
	```python
	my_bot = bot.Bot(blacklist=["69"])
	```
- `my_bot.stats()` prints some statistics about the model.

## Using from the command line

The `bot.py` command line can be used to train the bot, generate sample chat, and interact with the bot. It can also be used to save and load the model.

### Examples

Train the bot on `chatlog.txt` and save the model to `example.model`:

```
$ python3 bot.py -train chatlog.txt -save example.model
```

Generate 10 lines of sample chat using the saved `example.model`:

```
$ python3 bot.py -load example.model -m 10
```

Interact with the bot using the saved `example.model`:

```
$ python3 bot.py -load example.model -b1
```

### All options
```
usage: python3 bot.py [-h]
              [-load LOAD]
			  [-train TRAIN]
			  [-save SAVE]
			  [-n N] [-m M]
			  [-b1] [-b2]
			  [-debug]
  -load LOAD    load model from file
  -train TRAIN  train on file/folder
  -save SAVE    save model to file
  -n N          N states in markov chain (3 is recommended)
  -b1           chat with Bot1
  -b2           chat with Bot2
  -m M          generate a sample chat log with M messages
  -debug        print debug messages
```

## Notes

- The bot by default trains on a single chat log file. If you want to train it on multiple chat logs, you can pass the folder path to `create_model` function to train on all the files in the folder.
- The bot doesn't have a database of responses. It uses the chat logs to generate responses. So, the more chat logs you feed it, the better it will be.

## How to get a WhatsApp chat log

1. Open WhatsApp on your phone.
2. Go to the chat you want to export.
3. Tap the menu button (3 dots on the top right corner).
4. Tap `More`.
5. Tap `Export chat`.
6. Tap `Without Media`.
7. The chat log will be saved to your phone's storage.

For more information, see [this](https://faq.whatsapp.com/en/android/23756533/).

## TODO

- [ ] context based responses (remember the last few messages)
- [x] training on multiple chat logs
- [ ] efficient storage of model
- [x] web interface
- [x] media support (images, stickers, etc.)
- [ ] easy way to train bots online (website?)
- [ ] you tell me

## License

[MIT](LICENSE.md)

## Author

Soham Korade
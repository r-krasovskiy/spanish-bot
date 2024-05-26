# Spanish bot
This is a Telegram bot which helps to learn Spanish words.
## The logic
1) the bot provides a word in Spanish which a user has to translate, sending a response message;
2) if the user's response is correct he/she receives a message with congrtulation and a new word, otherwice he/she receives a message with a correct answer.

## Installation
1) clone the repository on your local directory by the command <b><i>'$ git clone'</i></b>;
2) create a virtual environment by the command <b><i>python -m venv venv</i></b>
3) activate the virtual environment by the command <b><i>source venv/Scripts/activate</i></b> (for Windows) or by the command <b><i>source venv/bin/activate</i></b> (for Mac);
4) upload the requirements from <i>requirements.txt</i> by the command <b><i>pip install -r requirements.txt</i></b>
5) get Telegram tocken follwed by the standard process (a message in Telegram to <b><i>@BotFather</i></b> and dialogue with it);
6) create a file <b>.env</b> and put there the received Telegram tocken (in string format - 'XXX...XXX'), name this variable as <b><i>TELEGRAM_TOKEN</i></b>;
7) launch bot by the command <b><i>python spanish_bot.py</i></b>;
8) find your bot by name received within registration on the step 5 above;
9) start chatting with the bot and learn Spanish words.

## Steps for further development
<p>
<ol>
  <li>to add database with Esp-Rus words;</li>
  <li>to add option of reversal translation (Rus-Esp);</li>
  <li>to split words by random butches of 10 items, the user has to gain 10 points translating these words; the words which were not translated will be provided 
to the user again;</li>
  <li>to add levels of difficulty.</li>
</ol>
</p>


# Use venv
python -m venv venv
source venv/bin/activate
pip install django

# Get "bad words"
wget "https://raw.githubusercontent.com/arhankundu99/profanity-filter/master/data/profanity_wordlist.txt" -qO API/profanity.txt

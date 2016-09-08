# imessage-counter
Displays how many words you and your friend sent to each other per day in a simple graph.

Usage: python imessageCounter.py <name of friend> <phone number or email address of contact> [--word=<word>] [--interval=<number>] [--percent=<percent>]

1. The name of the friend is what will appear on the legend.
2. The phone number or email address is what you are sending your messages to; in most cases it will be the phone number. If the phone number in question is (xxx)-xxx-xxxx and is in the USA, type it as +1xxxxxxxxxx .
3. The optional word is a specific word to count, instead of all words in general.
4. The optional interval is how many days you should label. For example, if it's 7, every week will be labeled. The interval is automatically done by month.
5. The optional percent is what percent of the logs to skip. This lets you zoom in on more recent messages.

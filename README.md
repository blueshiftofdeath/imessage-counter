# imessage-counter
Displays how many words you and your friend sent to each other per day in a simple graph.

Usage: python imessageCounter.py --people [name of friend] [phone number or email address of contact] --words [word] --interval=[number] --start [year] [month] [day] --end [year] [month] [day] -split -direction=[to or from]

1. The name of the friend is what will appear on the legend.
2. The phone number or email address is what you are sending your messages to; in most cases it will be the phone number. If the phone number in question is (xxx)-xxx-xxxx and is in the USA, type it as +1xxxxxxxxxx .
3. You can put in multiple friends.
4. The optional word is a specific word to count, instead of all words in general. Can have spaces as long as enclosed in quotes. You can put in multiple words.
5. The optional interval is how many days you should label. For example, if it's 7, every week will be labeled. The interval is automatically done by month.
6. The optional start date is where to start the plot.
7. The optional end date is where to end the plot.
8. If -split is enabled, then both the number of texts you sent your friend, and the number of texts your friend sent you, will be plotted separately. Otherwise, the sum of both is plotted.
9. If -direction=to, then only the number of texts you sent your friend is plotted.
10. If -direction=from, then only the number of texts your friend sent you is plotted.

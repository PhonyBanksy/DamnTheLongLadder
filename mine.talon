# Take a screenshot selection
take a snip: key(win-shift-s)

# Close the current window/app
close the app: key(alt-f4)

# Save the current file
save it: key(ctrl-s)

control it:(ctrl:down)
don't control it:(ctrl:up)
# undo
undo it: key(ctrl-z)

# redo
redo it: key(ctrl-shift-z)

# find text
find text: key(ctrl-f)

# Basic Emoticon/Emoji Commands
smiley hello: "👋"
smiley laugh: "😂"
smiley wink: "😉"
smiley smile: "🙂"

# Text-only versions (if you prefer them)
text hello: "o/"
text laugh: ":D"
text wink: ";)"
text smile: ":)"

# Volume up by 10% (5 presses of 2%)
volume up: key(volup:5)

# Volume down by 10% (5 presses of 2%)
volume down: key(voldown:5)

# Bonus: Mute button
volume mute: key(mute)

# Continuous "Auto-Walk" (Holds keys down until you say stop)
walk up:
    key(w:down)
walk down:
    key(d:down)
walk left:
    key(a:down)
walk right:
    key(s:down)

# Emergency stop to release all movement keys
stop walking:
    key(w:up)
    key(d:up)
    key(a:up)
    key(s:up)
	
last word:
    key(ctrl-shift-left)
    key(backspace)
end that shit:
    key(ctrl-c)

other window:
	key("alt-tab")
	
	
take a copy:
	key("control-c")
	
friend text:
	key("ctrl-f3")

caps on:
	key("shift:down")
caps off:
	key("shift:up")
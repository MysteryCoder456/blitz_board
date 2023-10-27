from blinker import Namespace

auth_signals = Namespace()

friend_added = auth_signals.signal("friend-added")

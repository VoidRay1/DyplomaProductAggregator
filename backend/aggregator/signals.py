from django import dispatch

test_signal = dispatch.Signal(["test"])
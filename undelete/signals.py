from django import dispatch

pre_trash = dispatch.Signal()
post_trash = dispatch.Signal()

pre_restore = dispatch.Signal()
post_restore = dispatch.Signal()

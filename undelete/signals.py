from django import dispatch

pre_trash = dispatch.Signal(providing_args=['instance'])
post_trash = dispatch.Signal(providing_args=['instance'])

pre_restore = dispatch.Signal(providing_args=['instance'])
post_restore = dispatch.Signal(providing_args=['instance'])

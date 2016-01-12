#!/usr/bin/python
"""hill web framework"""
import hill
import config

urlmapping = config.urlmapping
app = hill.Application(urlmapping)

if __name__ == '__main__':
    app.run()

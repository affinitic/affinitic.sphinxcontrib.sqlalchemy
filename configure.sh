#!/bin/sh
git archive --format=tar --remote=git@git.affinitic.be:arsia/arsia.base.git master Makefile | tar -x


#!/usr/bin/env bash

find . -type d -name .git -exec git --git-dir={} --work-tree=$PWD/{}/.. pull \;


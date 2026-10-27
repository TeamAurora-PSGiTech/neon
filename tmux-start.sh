#!/bin/bash
tmux new-session \; \
split-window -h \; split-window -h \; split-window -h \; \
select-pane -t 0 \; split-window -v \; \
select-pane -t 1 \; split-window -v \; \
select-pane -t 2 \; split-window -v \; \
select-pane -t 3 \; split-window -v \; \
select-layout tiled

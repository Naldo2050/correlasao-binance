
# CORR-WATCH Aliases
alias cw-cd='cd ~/corr-watch-mvp && source venv/bin/activate'
alias cw-logs='tail -f ~/corr-watch-mvp/logs/system.log'
alias cw-status='sudo systemctl status corr-watch'
alias cw-restart='sudo systemctl restart corr-watch'
alias cw-test='cd ~/corr-watch-mvp && source venv/bin/activate && python3 test_quick.py'

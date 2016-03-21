#!/bin/bash
# xauth handling, code adapted from sshd(8)
if type -p xauth >/dev/null && read proto cookie && [[ "$DISPLAY" ]]; then
        if [[ "${DISPLAY:0:10}" = 'localhost:' ]] ; then
                # X11UseLocalhost=yes
                #echo add unix:"${DISPLAY:11}" $proto $cookie   #### egrehm changed to :10 because seems to be broken on rhel6 and clones
                echo add unix:"${DISPLAY:10}" $proto $cookie
        else
                # X11UseLocalhost=no
                echo add "$DISPLAY" $proto $cookie
        fi | xauth -q -
fi

# make ssh agent accessible through predictable socket path
# (required to reconnect to screen sessions and keeping ssh agent working)
if [[ "$SSH_AUTH_SOCK" && "$SSH_AUTH_SOCK" != ~/.ssh/ssh_auth_sock ]] ; then
        mkdir -p ~/.ssh
        ln -sf $SSH_AUTH_SOCK ~/.ssh/ssh_auth_sock
fi

# unpack personal environment
if [[ "$USERHOME_DATA" ]] ; then
        base64 -d <<<"$USERHOME_DATA" | tar -xzC ~
fi

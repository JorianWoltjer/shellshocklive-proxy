# ShellShock Live Proxy

A MITM proxy for the [ShellShock Live](https://store.steampowered.com/app/326460/ShellShock_Live/) game on Steam. It has implemented the HTTP protocol that speaks with [PlayerIO](https://playerio.com/) to decode and re-encode data. Specifically, the **server list** showing joinable games. 

ShellShock Live uses `http://` to connect to `api.playerio.com` for requesting servers, meaning no encryption or verification is done. This allows anyone to impersonate this server and become a "man-in-the-middle" (MITM). This allows you to change and completely replace the request and response however you want. This program contains a few mods that can be done using this technique to fool the client into certain things. 

In a real MITM scenario you would need to impersonate `api.playerio.com`, which there are different methods for. However, the main use-case is MITM'ing yourself to make the game behave differently. To do this to yourself you can simply change the `/etc/hosts` file (or `C:\Windows\System32\drivers\etc\hosts` on Windows) to add a record where `api.playerio.com` points to your listening proxy IP address. If you are running this locally, it will be `127.0.0.1` (localhost) for example:

```
127.0.0.1 api.playerio.com
```

Now all traffic intended to go to their API server, will now be sent to that IP address on port 80. Now you should set up the proxy on the host you gave in order to mess with the traffic:

```Shell
$ sudo ./main.py
Starting proxy server on 0.0.0.0:80
```

Done! Now when you start ShellShock Live on the victim it should forward all the traffic through your proxy, and any mods should be applied. 

### Set `CURRENT_LEVEL`

In order to determine if you should be allowed to join a given match or not, the game checks if your current level is not further away from the "max level difference". To find which matches you were normally not able to join, but now are able to with the mod you will need to set this `CURRENT_LEVEL` variable in the `join_any_game.py` mod. This way all matches that are bypassed will be correctly suffixed with `[LEVEL]`.

https://github.com/JorianWoltjer/shellshocklive-proxy/blob/75b17679f35f50d2b5c4a2e7c1a34fb1611659dd/mods/join_any_game.py#L11

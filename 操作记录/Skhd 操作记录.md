https://github.com/asmvik/skhd

```
--install-service: Install launchd service file into ~/Library/LaunchAgents/com.asmvik.skhd.plist
    skhd --install-service

--uninstall-service: Remove launchd service file ~/Library/LaunchAgents/com.asmvik.skhd.plist
    skhd --uninstall-service

--start-service: Run skhd as a service through launchd
    skhd --start-service

--restart-service: Restart skhd service
    skhd --restart-service

--stop-service: Stop skhd service from running
    skhd --stop-service
```
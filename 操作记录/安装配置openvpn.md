```bash
# 安装
brew install openvpn

# 创建快捷链接
/opt/homebrew/bin
ln -s /opt/homebrew/opt/openvpn/sbin/openvpn openvpn

# 从wps可以找到zhaoxin.ovpn方知道.ssh下

# 增加免密sudo
sudo echo "$(whoami) ALL=(ALL) NOPASSWD: /opt/homebrew/opt/openvpn/sbin/openvpn" > /private/etc/sudoers.d/openvpn
 
# 启动vpn
sudo openvpn --config ~/.ssh/zhaoxin.ovpn
```

```zsh
# 开始性能测试
# zmodload zsh/zprof

# 优化启动速度
zstyle ':bracketed-paste-magic' active-enabled off
zstyle ':bracketed-paste-magic' paste-enabled off
DISABLE_AUTO_UPDATE="true"
DISABLE_UPDATE_PROMPT="true"

source $ZSH/oh-my-zsh.sh
source $HOME/.config/working/working.sh

plugins=(git zsh-autosuggestions zsh-completions zsh-syntax-highlighting autoswitch_virtualenv)

# bun completions
[ -s "/Users/zhaoxin/.bun/_bun" ] && source "/Users/zhaoxin/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"


```
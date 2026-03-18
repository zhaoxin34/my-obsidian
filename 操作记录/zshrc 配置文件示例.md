```zsh
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export ZSH="$HOME/.oh-my-zsh"
export ZSH_THEME="robbyrussell"

plugins=(git autoswitch_virtualenv poetry)

source $ZSH/oh-my-zsh.sh
source $(brew --prefix)/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source $(brew --prefix)/share/zsh-autosuggestions/zsh-autosuggestions.zsh
source /opt/homebrew/share/powerlevel10k/powerlevel10k.zsh-theme
source $HOME/.config/working/working.sh

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# The following lines have been added by Docker Desktop to enable Docker CLI completions.
fpath=(/Users/zhaoxin/.docker/completions $fpath)
autoload -Uz compinit
compinit
# End of Docker CLI completions

# bun completions
[ -s "/Users/zhaoxin/.bun/_bun" ] && source "/Users/zhaoxin/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```
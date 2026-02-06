- [ ] Supper Tab 可以实现按tab键实现很多功能
	- [ ] AI 补全
	- [ ] 跳过'")等符号
- [ ] 测试运行的插件，可以启动单元测试，运行
- [ ] Treesitter 高亮配置
- [ ] blink.cmp 补全配置
- [ ] Conform的prettierd配置，可以用于pretier加速 https://github.com/fsouza/prettierd

super-tab的配置, https://cmp.saghen.dev/installation.html
```lua
return {
  'saghen/blink.cmp',
  opts = {
    keymap = {
      preset = 'super-tab',
      ['<Tab>'] = {
        function(cmp)
          if cmp.snippet_active() then return cmp.accept()
          else return cmp.select_and_accept() end
        end,
        'snippet_forward',
        'fallback'
      }
    }
  }
}
```

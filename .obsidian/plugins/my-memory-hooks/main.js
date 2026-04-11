"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const obsidian_1 = require("obsidian");
const child_process_1 = require("child_process");
const DEFAULT_SETTINGS = {
    repository: "my-obsidian",
    debounceMs: 1000,
};
class FileHookPlugin extends obsidian_1.Plugin {
    constructor() {
        super(...arguments);
        this.settings = DEFAULT_SETTINGS;
    }
    async onload() {
        await this.loadSettings();
        this.addSettingTab(new SettingTab(this.app, this));
        const debouncedModify = (0, obsidian_1.debounce)((file, action) => {
            this.runSync(file.path, 'debouncedModify');
        }, this.settings.debounceMs, true);
        // modify
        this.registerEvent(this.app.vault.on("modify", (file) => {
            if (this.shouldHandle(file)) {
                debouncedModify(file, 'modify');
            }
        }));
        // 不必监听create事件，因为create还没有真正创建有用的内容
        // this.registerEvent(
        //   this.app.vault.on("create", (file: TAbstractFile) => {
        //     if (this.shouldHandle(file)) {
        //       this.runSync((file as TFile).path, 'create');
        //     }
        //   })
        // );
        // delete
        this.registerEvent(this.app.vault.on("delete", (file) => {
            if (this.shouldHandle(file)) {
                debouncedModify(file, 'delete');
            }
        }));
        // rename
        this.registerEvent(this.app.vault.on("rename", (file, oldPath) => {
            if (this.shouldHandle(file)) {
                debouncedModify(file, 'rename');
            }
        }));
    }
    shouldHandle(file) {
        if (!(file instanceof obsidian_1.TFile))
            return false;
        if (!file.path.endsWith(".md"))
            return false;
        if (file.path.startsWith(".obsidian"))
            return false;
        return true;
    }
    runSync(filePath, action) {
        const cmd = `~/.local/bin/memory sync -r ${this.settings.repository}`;
        console.log(`[My Memory Hook] Syncing repository: ${this.settings.repository}`);
        new obsidian_1.Notice(`[My Memory Hook] Syncing...`, 2000);
        (0, child_process_1.exec)(cmd, (err, stdout, stderr) => {
            if (err) {
                console.error("[My Memory Hook] Sync failed:", err);
                new obsidian_1.Notice(`[My Memory Hook] Sync failed: ${err.message}`, 5000);
                return;
            }
            if (stdout) {
                console.log("[My Memory Hook]", stdout);
                // 提取关键信息显示
                const lines = stdout.trim().split("\n");
                const lastLine = lines[lines.length - 1];
                new obsidian_1.Notice(`[My Memory Hook] ${lastLine}`, 3000);
            }
            if (stderr)
                console.error("[My Memory Hook]", stderr);
        });
    }
    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }
    async saveSettings() {
        await this.saveData(this.settings);
    }
}
exports.default = FileHookPlugin;
class SettingTab extends obsidian_1.PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }
    display() {
        this.containerEl.empty();
        new obsidian_1.Setting(this.containerEl)
            .setName("Repository name")
            .setDesc("The repository to sync with (e.g., my-obsidian)")
            .addText((text) => text
            .setPlaceholder("my-obsidian")
            .setValue(this.plugin.settings.repository)
            .onChange(async (value) => {
            this.plugin.settings.repository = value;
            await this.plugin.saveSettings();
        }));
        new obsidian_1.Setting(this.containerEl)
            .setName("Debounce (ms)")
            .setDesc("Delay before triggering sync after file changes")
            .addText((text) => text
            .setPlaceholder("1000")
            .setValue(String(this.plugin.settings.debounceMs))
            .onChange(async (value) => {
            const ms = parseInt(value, 10);
            if (!isNaN(ms) && ms > 0) {
                this.plugin.settings.debounceMs = ms;
                await this.plugin.saveSettings();
            }
        }));
    }
}

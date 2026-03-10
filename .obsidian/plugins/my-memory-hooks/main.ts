import { Plugin, TFile, debounce } from "obsidian";
import { exec } from "child_process";

interface PluginSettings {
  onSave: string;
  onRename: string;
  onCreate: string;
  onDelete: string;
}

const DEFAULT_SETTINGS: PluginSettings = {
  onSave: "",
  onRename: "",
  onCreate: "",
  onDelete: ""
};

export default class FileHookPlugin extends Plugin {

  settings: PluginSettings;

  async onload() {

    await this.loadSettings();

    const debouncedModify = debounce((file: TFile) => {
      this.runCommand(this.settings.onSave, file.path);
    }, 1000, true);

    // modify
    this.registerEvent(
      this.app.vault.on("modify", (file) => {
        if (this.shouldHandle(file)) {
          debouncedModify(file);
        }
      })
    );

    // create
    this.registerEvent(
      this.app.vault.on("create", (file) => {
        if (this.shouldHandle(file)) {
          this.runCommand(this.settings.onCreate, file.path);
        }
      })
    );

    // delete
    this.registerEvent(
      this.app.vault.on("delete", (file) => {
        if (this.shouldHandle(file)) {
          this.runCommand(this.settings.onDelete, file.path);
        }
      })
    );

    // rename
    this.registerEvent(
      this.app.vault.on("rename", (file, oldPath) => {
        if (this.shouldHandle(file)) {
          this.runCommand(this.settings.onRename, file.path, oldPath);
        }
      })
    );
  }

  shouldHandle(file: any) {

    if (!(file instanceof TFile)) return false;

    if (!file.path.endsWith(".md")) return false;

    if (file.path.startsWith(".obsidian")) return false;

    return true;
  }

  runCommand(cmd: string, path: string, oldPath?: string) {

    if (!cmd) return;

    let finalCmd = cmd
      .replace("{path}", `"${path}"`)
      .replace("{oldPath}", `"${oldPath ?? ""}"`);

    exec(finalCmd, (err, stdout, stderr) => {

      if (err) {
        console.error("command failed", err);
        return;
      }

      if (stdout) console.log(stdout);
      if (stderr) console.error(stderr);
    });
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }
}

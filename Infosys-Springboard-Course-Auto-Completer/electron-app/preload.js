const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("courseApp", {
	getDefaultEnvPath: () => ipcRenderer.invoke("get-default-env-path"),
	pickEnvFile: () => ipcRenderer.invoke("pick-env-file"),
	startCompletion: (payload) => ipcRenderer.invoke("start-completion", payload),
	stopCompletion: () => ipcRenderer.invoke("stop-completion"),
	onRunOutput: (callback) => {
		const handler = (_event, payload) => callback(payload);
		ipcRenderer.on("run-output", handler);
		return () => ipcRenderer.removeListener("run-output", handler);
	},
	onRunError: (callback) => {
		const handler = (_event, payload) => callback(payload);
		ipcRenderer.on("run-error", handler);
		return () => ipcRenderer.removeListener("run-error", handler);
	},
	onRunExit: (callback) => {
		const handler = (_event, payload) => callback(payload);
		ipcRenderer.on("run-exit", handler);
		return () => ipcRenderer.removeListener("run-exit", handler);
	},
});

const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const { spawn } = require("child_process");

let mainWindow = null;
let currentProcess = null;

function getProjectRoot() {
	return path.resolve(__dirname, "..");
}

function getDefaultEnvPath() {
	return path.join(getProjectRoot(), ".env");
}

function createWindow() {
	mainWindow = new BrowserWindow({
		width: 1200,
		height: 860,
		minWidth: 980,
		minHeight: 700,
		webPreferences: {
			contextIsolation: true,
			nodeIntegration: false,
			preload: path.join(__dirname, "preload.js"),
		},
	});

	mainWindow.loadFile(path.join(__dirname, "index.html"));
}

app.whenReady().then(() => {
	createWindow();

	app.on("activate", () => {
		if (BrowserWindow.getAllWindows().length === 0) {
			createWindow();
		}
	});
});

app.on("window-all-closed", () => {
	if (currentProcess) {
		try {
			currentProcess.kill();
		} catch {
			// no-op
		}
	}

	if (process.platform !== "darwin") {
		app.quit();
	}
});

ipcMain.handle("get-default-env-path", async () => {
	return getDefaultEnvPath();
});

ipcMain.handle("pick-env-file", async () => {
	const result = await dialog.showOpenDialog({
		title: "Select .env File",
		properties: ["openFile"],
		filters: [
			{ name: "Env Files", extensions: ["env"] },
			{ name: "All Files", extensions: ["*"] },
		],
	});

	if (result.canceled || result.filePaths.length === 0) {
		return { canceled: true };
	}

	return { canceled: false, filePath: result.filePaths[0] };
});

ipcMain.handle("start-completion", async (event, payload) => {
	if (currentProcess) {
		return { ok: false, error: "A completion run is already active." };
	}

	const projectRoot = getProjectRoot();
	const scriptPath = path.join(projectRoot, "course_completer.py");
	const envFilePath = payload?.envFilePath?.trim() || getDefaultEnvPath();
	const pythonExecutable =
		payload?.pythonExecutable?.trim() ||
		(process.platform === "win32" ? "python" : "python3");
	const envOverrides = payload?.envOverrides || {};
	const unsetKeys = Array.isArray(payload?.unsetKeys) ? payload.unsetKeys : [];

	const childEnv = {
		...process.env,
		INFOSYS_ENV_FILE: envFilePath,
		NON_INTERACTIVE: "true",
	};

	for (const key of unsetKeys) {
		delete childEnv[key];
	}

	for (const [key, value] of Object.entries(envOverrides)) {
		if (value === undefined || value === null) {
			continue;
		}

		childEnv[key] = String(value);
	}

	try {
		currentProcess = spawn(pythonExecutable, [scriptPath], {
			cwd: projectRoot,
			env: childEnv,
			windowsHide: true,
		});

		currentProcess.stdout.on("data", (chunk) => {
			event.sender.send("run-output", {
				stream: "stdout",
				text: chunk.toString(),
			});
		});

		currentProcess.stderr.on("data", (chunk) => {
			event.sender.send("run-output", {
				stream: "stderr",
				text: chunk.toString(),
			});
		});

		currentProcess.on("error", (error) => {
			event.sender.send("run-error", {
				message: error.message,
			});
			currentProcess = null;
		});

		currentProcess.on("close", (code) => {
			event.sender.send("run-exit", { code });
			currentProcess = null;
		});

		return { ok: true };
	} catch (error) {
		currentProcess = null;
		return { ok: false, error: error.message };
	}
});

ipcMain.handle("stop-completion", async () => {
	if (!currentProcess) {
		return { ok: false, error: "No active run to stop." };
	}

	try {
		currentProcess.kill();
		return { ok: true };
	} catch (error) {
		return { ok: false, error: error.message };
	}
});

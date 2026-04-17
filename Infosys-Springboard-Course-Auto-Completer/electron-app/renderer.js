const envFilePathInput = document.getElementById("envFilePath");
const pythonExecInput = document.getElementById("pythonExec");
const tokenOverrideInput = document.getElementById("tokenOverride");
const browseEnvBtn = document.getElementById("browseEnvBtn");

const targetTypeSelect = document.getElementById("targetType");
const courseRefsGroup = document.getElementById("courseRefsGroup");
const playlistGroup = document.getElementById("playlistGroup");
const courseRefsInput = document.getElementById("courseRefs");
const playlistRefInput = document.getElementById("playlistRef");
const autoConfirmInput = document.getElementById("autoConfirm");
const dryRunInput = document.getElementById("dryRun");

const quickCourseIdInput = document.getElementById("quickCourseId");

const startFullBtn = document.getElementById("startFullBtn");
const startQuickBtn = document.getElementById("startQuickBtn");
const stopBtn = document.getElementById("stopBtn");
const clearLogsBtn = document.getElementById("clearLogsBtn");
const logOutput = document.getElementById("logOutput");

let isRunning = false;

function setRunningState(running) {
	isRunning = running;
	startFullBtn.disabled = running;
	startQuickBtn.disabled = running;
	stopBtn.disabled = !running;
}

function appendLog(text, stream = "stdout") {
	const prefix = stream === "stderr" ? "[ERR] " : "";
	logOutput.textContent += `${prefix}${text}`;
	logOutput.scrollTop = logOutput.scrollHeight;
}

function normalize(value) {
	return (value || "").trim();
}

function updateTargetGroups() {
	const targetType = targetTypeSelect.value;
	const isCourse = targetType === "course";

	courseRefsGroup.classList.toggle("hidden", !isCourse);
	playlistGroup.classList.toggle("hidden", isCourse);
}

function buildBasePayload() {
	return {
		envFilePath: normalize(envFilePathInput.value),
		pythonExecutable: normalize(pythonExecInput.value) || "python",
	};
}

function applyTokenOverride(envOverrides) {
	const tokenOverride = normalize(tokenOverrideInput.value);
	if (tokenOverride) {
		envOverrides.INFOSYS_TOKEN = tokenOverride;
		envOverrides.token = tokenOverride;
	}
}

async function startRun(payload, title) {
	if (isRunning) {
		appendLog("A run is already active. Stop current run first.\n", "stderr");
		return;
	}

	appendLog(`\n========== ${title} ==========\n`);
	setRunningState(true);

	const result = await window.courseApp.startCompletion(payload);
	if (!result.ok) {
		appendLog(`Failed to start run: ${result.error}\n`, "stderr");
		setRunningState(false);
	}
}

browseEnvBtn.addEventListener("click", async () => {
	const result = await window.courseApp.pickEnvFile();
	if (!result.canceled) {
		envFilePathInput.value = result.filePath;
	}
});

targetTypeSelect.addEventListener("change", updateTargetGroups);

startFullBtn.addEventListener("click", async () => {
	const targetType = targetTypeSelect.value;
	const envOverrides = {
		TARGET_TYPE: targetType,
		AUTO_CONFIRM: autoConfirmInput.checked ? "true" : "false",
		DRY_RUN: dryRunInput.checked ? "true" : "false",
	};

	applyTokenOverride(envOverrides);

	if (targetType === "course") {
		const refs = normalize(courseRefsInput.value);
		if (!refs) {
			appendLog("Please enter at least one course ID or URL.\n", "stderr");
			return;
		}

		envOverrides.INFOSYS_COURSE_IDS = refs;
		envOverrides.courseids = refs;
		envOverrides.INFOSYS_COURSE_ID = "";
		envOverrides.courseid = "";
		envOverrides.INFOSYS_TARGET_URLS = "";
		envOverrides.targeturls = "";
		envOverrides.INFOSYS_TARGET_URL = "";
		envOverrides.targeturl = "";
		envOverrides.INFOSYS_PLAYLIST_ID = "";
		envOverrides.playlistid = "";
		envOverrides.INFOSYS_PLAYLIST_URL = "";
		envOverrides.playlisturl = "";
	} else {
		const playlistRef = normalize(playlistRefInput.value);
		if (!playlistRef) {
			appendLog("Please enter a playlist ID or playlist URL.\n", "stderr");
			return;
		}

		envOverrides.INFOSYS_PLAYLIST_ID = playlistRef;
		envOverrides.playlistid = playlistRef;
		envOverrides.INFOSYS_COURSE_IDS = "";
		envOverrides.courseids = "";
		envOverrides.INFOSYS_COURSE_ID = "";
		envOverrides.courseid = "";
		envOverrides.INFOSYS_TARGET_URLS = "";
		envOverrides.targeturls = "";
		envOverrides.INFOSYS_TARGET_URL = "";
		envOverrides.targeturl = "";
	}

	const payload = {
		...buildBasePayload(),
		envOverrides,
	};

	await startRun(payload, "FULL COMPLETION RUN");
});

startQuickBtn.addEventListener("click", async () => {
	const courseId = normalize(quickCourseIdInput.value);
	if (!courseId) {
		appendLog("Please enter a course ID for quick completion.\n", "stderr");
		return;
	}

	const envOverrides = {
		TARGET_TYPE: "course",
		INFOSYS_COURSE_IDS: courseId,
		courseids: courseId,
		INFOSYS_COURSE_ID: "",
		courseid: "",
		INFOSYS_TARGET_URLS: "",
		targeturls: "",
		INFOSYS_TARGET_URL: "",
		targeturl: "",
		AUTO_CONFIRM: "true",
		DRY_RUN: "false",
		INFOSYS_PLAYLIST_ID: "",
		playlistid: "",
		INFOSYS_PLAYLIST_URL: "",
		playlisturl: "",
	};

	applyTokenOverride(envOverrides);

	const payload = {
		...buildBasePayload(),
		envOverrides,
	};

	await startRun(payload, `QUICK COMPLETION (${courseId})`);
});

stopBtn.addEventListener("click", async () => {
	const result = await window.courseApp.stopCompletion();
	if (!result.ok) {
		appendLog(`Stop failed: ${result.error}\n`, "stderr");
	} else {
		appendLog("Stop requested.\n", "stderr");
	}
});

clearLogsBtn.addEventListener("click", () => {
	logOutput.textContent = "";
});

window.courseApp.onRunOutput(({ stream, text }) => {
	appendLog(text, stream);
});

window.courseApp.onRunError(({ message }) => {
	appendLog(`Runtime error: ${message}\n`, "stderr");
	setRunningState(false);
});

window.courseApp.onRunExit(({ code }) => {
	appendLog(`\nRun finished with exit code: ${code}\n`);
	setRunningState(false);
});

(async function init() {
	setRunningState(false);
	updateTargetGroups();

	const defaultEnvPath = await window.courseApp.getDefaultEnvPath();
	envFilePathInput.value = defaultEnvPath;
})();

// ── Config ────────────────────────────────────────────────────────
const API_BASE = "http://localhost:8000";
const SESSION_ID = "session-" + Math.random().toString(36).slice(2, 9);

// ── State ─────────────────────────────────────────────────────────
let currentMode = "text";
let selectedImage = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// ── DOM refs ──────────────────────────────────────────────────────
const messagesEl = document.getElementById("messages");
const sessionDisplay = document.getElementById("session-display");
const modeBadge = document.getElementById("mode-badge");
const textInput = document.getElementById("text-input");
const sendTextBtn = document.getElementById("send-text-btn");
const recordBtn = document.getElementById("record-btn");
const recordLabel = document.getElementById("record-label");
const voiceStatus = document.getElementById("voice-status");
const uploadAudioBtn = document.getElementById("upload-audio-btn");
const audioFileInput = document.getElementById("audio-file-input");
const dropZone = document.getElementById("drop-zone");
const imageInput = document.getElementById("image-input");
const imagePreviewRow = document.getElementById("image-preview-row");
const imagePreview = document.getElementById("image-preview");
const analyseBtn = document.getElementById("analyse-btn");
const removeImgBtn = document.getElementById("remove-img-btn");
const clearBtn = document.getElementById("clear-btn");

// ── Init ──────────────────────────────────────────────────────────
sessionDisplay.textContent = SESSION_ID;
addBotMessage(
    "👋 Welcome to ShopSense AI! I can help you find the best products.\n\n" +
    "You can:\n• 💬 Type what you're looking for\n" +
    "• 🎤 Send a voice message\n• 📸 Upload a product photo"
);

// ── Mode switching ────────────────────────────────────────────────
const MODES = {
    text: { label: "Text mode", badge: { bg: "#e6f1fb", color: "#185FA5" } },
    voice: { label: "Voice mode", badge: { bg: "#e1f5ee", color: "#0f6e56" } },
    image: { label: "Image mode", badge: { bg: "#faece7", color: "#712b13" } },
};

function switchMode(mode) {
    currentMode = mode;

    // Update sidebar buttons
    document.querySelectorAll(".mode-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.mode === mode);
    });
    // Update pill buttons
    document.querySelectorAll(".mod-pill").forEach(p => {
        p.classList.toggle("active", p.dataset.mode === mode);
    });
    // Update header badge
    const cfg = MODES[mode];
    modeBadge.textContent = cfg.label;
    modeBadge.style.background = cfg.badge.bg;
    modeBadge.style.color = cfg.badge.color;

    // Show correct panel
    ["text", "voice", "image"].forEach(m => {
        document.getElementById("panel-" + m).classList.toggle("hidden", m !== mode);
    });
}

document.querySelectorAll(".mode-btn, .mod-pill").forEach(btn => {
    btn.addEventListener("click", () => switchMode(btn.dataset.mode));
});

// ── Clear session ─────────────────────────────────────────────────
clearBtn.addEventListener("click", async () => {
    await fetch(`${API_BASE}/session/${SESSION_ID}`, { method: "DELETE" });
    messagesEl.innerHTML = "";
    addBotMessage("Session cleared. How can I help you today?");
});

// ── Message rendering ─────────────────────────────────────────────
function addUserMessage(text, label = "You · Text") {
    const msg = document.createElement("div");
    msg.className = "msg user";
    msg.innerHTML = `
    <div class="bubble">${escHtml(text)}</div>
    <div class="msg-label">${escHtml(label)}</div>`;
    messagesEl.appendChild(msg);
    scrollBottom();
}

function addBotMessage(text, extras = "") {
    const msg = document.createElement("div");
    msg.className = "msg bot";
    const formattedText = formatBotText(text);
    msg.innerHTML = `
    <div class="msg-label">ShopSense AI · GPT-4</div>
    <div class="bubble">${formattedText}</div>
    ${extras}`;
    messagesEl.appendChild(msg);
    scrollBottom();
    return msg;
}

function addTypingIndicator() {
    const msg = document.createElement("div");
    msg.className = "msg bot";
    msg.id = "typing";
    msg.innerHTML = `
    <div class="msg-label">ShopSense AI</div>
    <div class="bubble typing-bubble">
      <span></span><span></span><span></span>
    </div>`;
    messagesEl.appendChild(msg);
    scrollBottom();
}

function removeTypingIndicator() {
    document.getElementById("typing")?.remove();
}

function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function escHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;")
        .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function formatBotText(text) {
    // Convert numbered lists and line breaks for readability
    return escHtml(text)
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

// ── TEXT: send ────────────────────────────────────────────────────
async function sendText() {
    const msg = textInput.value.trim();
    if (!msg) return;
    textInput.value = "";
    addUserMessage(msg, "You · Text");
    addTypingIndicator();

    try {
        const res = await fetch(`${API_BASE}/chat/text`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: SESSION_ID, message: msg }),
        });
        const data = await res.json();
        removeTypingIndicator();
        addBotMessage(data.recommendation);
    } catch (e) {
        removeTypingIndicator();
        addBotMessage("⚠️ Could not reach the backend. Is it running on port 8000?");
    }
}

sendTextBtn.addEventListener("click", sendText);
textInput.addEventListener("keydown", e => { if (e.key === "Enter") sendText(); });

// ── VOICE: record via MediaRecorder ──────────────────────────────
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: "audio/wav" });
            stream.getTracks().forEach(t => t.stop());
            await sendVoice(blob);
        };
        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add("recording");
        recordLabel.textContent = "Recording... release to send";
        voiceStatus.textContent = "🔴 Recording...";
    } catch {
        voiceStatus.textContent = "⚠️ Microphone access denied. Use file upload instead.";
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove("recording");
        recordLabel.textContent = "Hold to record";
        voiceStatus.textContent = "Processing...";
    }
}

recordBtn.addEventListener("mousedown", startRecording);
recordBtn.addEventListener("mouseup", stopRecording);
recordBtn.addEventListener("touchstart", e => { e.preventDefault(); startRecording(); });
recordBtn.addEventListener("touchend", stopRecording);

// File upload fallback
uploadAudioBtn.addEventListener("click", () => audioFileInput.click());
audioFileInput.addEventListener("change", async () => {
    if (audioFileInput.files[0]) await sendVoice(audioFileInput.files[0]);
});

async function sendVoice(audioBlob) {
    voiceStatus.textContent = "Sending to Azure Speech...";
    addTypingIndicator();

    const form = new FormData();
    form.append("session_id", SESSION_ID);
    form.append("audio_file", audioBlob, "recording.wav");

    try {
        const res = await fetch(`${API_BASE}/chat/voice`, { method: "POST", body: form });
        const data = await res.json();
        removeTypingIndicator();

        // Show transcript + recommendation
        const transcriptHtml = `
      <div class="transcript-tag">🎤 Heard: "${escHtml(data.transcript)}"</div>`;
        addUserMessage("", "You · Voice");

        // Fetch TTS audio for the response
        const audioExtras = await getTTSAudio(data.recommendation);
        addBotMessage(data.recommendation, audioExtras);
        voiceStatus.textContent = "Press and hold the button, speak your query, then release";
    } catch (e) {
        removeTypingIndicator();
        addBotMessage("⚠️ Voice processing failed. Check the backend is running.");
        voiceStatus.textContent = "Error — try again";
    }
}

async function getTTSAudio(text) {
    try {
        const res = await fetch(`${API_BASE}/tts`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: SESSION_ID, message: text }),
        });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        return `<audio class="audio-player" controls src="${url}"></audio>`;
    } catch {
        return "";
    }
}

// ── IMAGE: drag-drop + file picker ────────────────────────────────
dropZone.addEventListener("dragover", e => {
    e.preventDefault(); dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", e => {
    e.preventDefault(); dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) setImagePreview(file);
});

imageInput.addEventListener("change", () => {
    if (imageInput.files[0]) setImagePreview(imageInput.files[0]);
});

function setImagePreview(file) {
    selectedImage = file;
    const url = URL.createObjectURL(file);
    imagePreview.src = url;
    imagePreviewRow.classList.remove("hidden");
    dropZone.style.display = "none";
}

removeImgBtn.addEventListener("click", () => {
    selectedImage = null;
    imagePreview.src = "";
    imagePreviewRow.classList.add("hidden");
    dropZone.style.display = "";
    imageInput.value = "";
});

analyseBtn.addEventListener("click", async () => {
    if (!selectedImage) return;

    // Show thumbnail in chat
    const thumbUrl = URL.createObjectURL(selectedImage);
    const msg = document.createElement("div");
    msg.className = "msg user";
    msg.innerHTML = `
    <img class="msg-image" src="${thumbUrl}" alt="uploaded product"/>
    <div class="msg-label">You · Image upload</div>`;
    messagesEl.appendChild(msg);
    scrollBottom();

    addTypingIndicator();

    const form = new FormData();
    form.append("session_id", SESSION_ID);
    form.append("image_file", selectedImage, selectedImage.name);

    try {
        const res = await fetch(`${API_BASE}/chat/image`, { method: "POST", body: form });
        const data = await res.json();
        removeTypingIndicator();

        const visionNote = `
      <div class="transcript-tag" style="margin-bottom:6px">
        🔍 Vision: ${escHtml(data.vision_summary.slice(0, 120))}...
      </div>`;
        addBotMessage(data.recommendation, visionNote);

        // Reset image panel
        removeImgBtn.click();
    } catch (e) {
        removeTypingIndicator();
        addBotMessage("⚠️ Image analysis failed. Check the backend is running.");
    }
});
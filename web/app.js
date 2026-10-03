const promptInput = document.querySelector("#prompt");
const count = document.querySelector("#count");
const form = document.querySelector("#form");
const chat = document.querySelector("#chat");
const theme = document.querySelector("#theme");
const menu = document.querySelector("#menu");

function setBusy(busy) {
  const button = form.querySelector("button");
  button.disabled = busy;
  button.textContent = busy ? "Storm is working…" : "Ask Storm ↵";
}

function addMessage(author, text, kind = "") {
  const message = document.createElement("div");
  message.className = "msg " + kind;
  const avatar = document.createElement("b");
  avatar.textContent = author === "You" ? "Y" : "S";
  const body = document.createElement("p");
  const label = document.createElement("small");
  label.textContent = author;
  const content = document.createElement("span");
  content.textContent = text;
  body.append(label, content);
  message.append(avatar, body);
  chat.append(message);
  chat.scrollTop = chat.scrollHeight;
  return message;
}

async function askStorm(prompt) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json", "Accept": "application/json"},
    body: JSON.stringify({prompt})
  });
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("Server returned an invalid response.");
  }
  if (!response.ok) {
    throw new Error(data.error || "Request failed.");
  }
  return data.answer;
}

async function loadWorkspace() {
  try {
    const response = await fetch("/api/workspace", {headers: {"Accept": "application/json"}});
    if (!response.ok) return;
    const data = await response.json();
    const metric = document.querySelector(".metric");
    if (metric && Array.isArray(data.files)) {
      metric.querySelector("b").textContent = String(data.files.length);
    }
  } catch {
    // The dashboard remains usable if workspace discovery is temporarily unavailable.
  }
}

promptInput.addEventListener("input", () => {
  count.textContent = promptInput.value.length + " / 4000";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const value = promptInput.value.trim();
  if (!value || form.querySelector("button").disabled) return;

  addMessage("You", value);
  promptInput.value = "";
  count.textContent = "0 / 4000";
  setBusy(true);

  const pending = addMessage("StormCodAI", "Analyzing the workspace…");
  try {
    const answer = await askStorm(value);
    pending.querySelector("span").textContent = answer;
  } catch (error) {
    pending.querySelector("span").textContent = error instanceof Error ? error.message : "Request failed.";
    pending.classList.add("error");
  } finally {
    setBusy(false);
  }
});

theme.addEventListener("click", () => {
  document.documentElement.classList.toggle("light");
});

menu.addEventListener("click", () => {
  const side = document.querySelector("#side");
  side.style.display = side.style.display === "none" ? "" : "none";
});

loadWorkspace();

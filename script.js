document.querySelectorAll(".level").forEach(label => {
  label.addEventListener("click", () => {
    document.querySelectorAll(".level").forEach(x => x.classList.remove("selected"));
    label.classList.add("selected");
    const radio = label.querySelector("input");
    if (radio) radio.checked = true;
  });
});

async function askAI(topic) {
  const input = document.getElementById("aiQuestion");
  const box = document.getElementById("aiAnswer");
  const question = input.value.trim();
  if (!question) {
    box.textContent = "Please enter a question.";
    return;
  }
  box.textContent = "Thinking...";
  try {
    const response = await fetch("/ask-ai", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({topic, question})
    });
    const data = await response.json();
    box.textContent = data.answer;
  } catch (e) {
    box.textContent = "Unable to get an answer right now.";
  }
}

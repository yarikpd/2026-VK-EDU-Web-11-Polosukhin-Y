"use strict";

async function sendAction(form, body) {
  const response = await fetch(form.action, {
    method: "POST",
    headers: { Accept: "application/json" },
    body,
  }).catch(() => {
    throw new Error("Не удалось связаться с сервером. Попробуйте ещё раз.");
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok || !payload) {
    throw new Error(payload?.error || "Не удалось выполнить действие. Попробуйте ещё раз.");
  }
  return payload;
}

function showActionError(form, message = "") {
  const alert = form.querySelector("[data-action-error]");
  alert.hidden = !message;
  alert.textContent = message;
}

for (const form of document.querySelectorAll("[data-vote-form]")) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fieldset = form.querySelector("fieldset");
    const button = event.submitter;
    if (!button || fieldset.disabled || button.getAttribute("aria-pressed") === "true") {
      return;
    }

    const data = new FormData(form, button);
    fieldset.disabled = true;
    showActionError(form);
    try {
      const result = await sendAction(form, data);
      form.querySelector("[data-rating]").textContent = result.rating;
      for (const choice of form.querySelectorAll("[aria-pressed]")) {
        const selected = Number(choice.value) === result.value;
        choice.setAttribute("aria-pressed", String(selected));
        choice.classList.toggle("active", selected);
      }
    } catch (error) {
      showActionError(form, error.message);
    } finally {
      fieldset.disabled = false;
    }
  });
}

const answerChoices = document.querySelectorAll("[data-accepted-form] [name=accepted]");
for (const choice of answerChoices) {
  choice.addEventListener("change", async () => {
    const form = choice.form;
    const data = new FormData(form);
    data.set("accepted", choice.checked ? "1" : "0");
    for (const item of answerChoices) {
      item.disabled = true;
      showActionError(item.form);
    }

    try {
      const result = await sendAction(form, data);
      for (const item of answerChoices) {
        item.checked = item.form.elements.answer_id.value === String(result.accepted_answer_id);
        item.closest("article").classList.toggle("border-success", item.checked);
      }
    } catch (error) {
      choice.checked = !choice.checked;
      showActionError(form, error.message);
    } finally {
      for (const item of answerChoices) {
        item.disabled = false;
      }
    }
  });
}

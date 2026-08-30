// Notes widget shared by the reading pane (home page) and the article page.
// Talks to the /article/<id>/notes JSON endpoints. Luxon must be loaded for
// relative dates; without it the raw ISO date is shown.
function setupNotes(options) {
  const list = options.list;
  const form = options.form;
  const input = options.input;
  const articleBase = options.articleBase;
  const csrfToken = options.csrfToken;
  const deleteTitle = options.deleteTitle;
  const getArticleId = options.getArticleId;

  function renderNote(note) {
    const li = document.createElement("li");
    li.className = "border-bottom pb-2 mb-2";
    li.dataset.noteId = note.id;

    const body = document.createElement("div");
    body.className = "d-flex justify-content-between align-items-start";

    const text = document.createElement("div");
    text.className = "small";
    text.style.whiteSpace = "pre-wrap";
    text.style.overflowWrap = "break-word";
    text.textContent = note.content;
    body.appendChild(text);

    const delBtn = document.createElement("button");
    delBtn.type = "button";
    delBtn.className = "btn btn-link btn-sm text-danger p-0 ms-2 note-delete";
    delBtn.title = deleteTitle;
    const delIcon = document.createElement("i");
    delIcon.className = "bi bi-trash";
    delIcon.setAttribute("aria-hidden", "true");
    delBtn.appendChild(delIcon);
    body.appendChild(delBtn);

    li.appendChild(body);

    if (note.created_date) {
      const date = document.createElement("div");
      date.className = "text-muted";
      date.style.fontSize = "0.75rem";
      try {
        date.textContent = luxon.DateTime.fromISO(note.created_date).toRelative();
      } catch (e) {
        date.textContent = note.created_date;
      }
      li.appendChild(date);
    }
    return li;
  }

  async function loadNotes(articleId) {
    list.innerHTML = "";
    try {
      const resp = await fetch(`${articleBase}/${articleId}/notes`);
      if (!resp.ok) throw new Error("Failed to load notes");
      const data = await resp.json();
      data.notes.forEach(function (note) {
        list.appendChild(renderNote(note));
      });
    } catch (e) {
      console.error(e);
    }
  }

  if (form) {
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const articleId = getArticleId();
      const content = input.value.trim();
      if (!content || articleId === null) return;
      try {
        const resp = await fetch(`${articleBase}/${articleId}/notes`, {
          method: "POST",
          headers: { "X-CSRFToken": csrfToken },
          body: new URLSearchParams({ content: content }),
        });
        if (!resp.ok) throw new Error("Failed to add note");
        const data = await resp.json();
        list.appendChild(renderNote(data.note));
        input.value = "";
      } catch (e) {
        console.error(e);
      }
    });
  }

  if (list) {
    list.addEventListener("click", async function (event) {
      const btn = event.target.closest(".note-delete");
      if (!btn) return;
      const li = btn.closest("[data-note-id]");
      if (!li) return;
      try {
        const resp = await fetch(`${articleBase}/note/${li.dataset.noteId}/delete`, {
          method: "POST",
          headers: { "X-CSRFToken": csrfToken },
        });
        if (!resp.ok) throw new Error("Failed to delete note");
        li.remove();
      } catch (e) {
        console.error(e);
      }
    });
  }

  return { loadNotes: loadNotes };
}

const cards = document.querySelectorAll(".kanban-card");
const columns = document.querySelectorAll(".kanban-column");

cards.forEach(card => {
    card.addEventListener("dragstart", dragStart);
});

columns.forEach(col => {
    col.addEventListener("dragover", dragOver);
    col.addEventListener("dragleave", dragLeave);
    col.addEventListener("drop", dropCard);
});

let draggedCard = null;

function dragStart(e) {
    draggedCard = this;
    e.dataTransfer.setData("text/plain", this.dataset.id);
}

function dragOver(e) {
    e.preventDefault();
    this.classList.add("drag-over");
}

function dragLeave(e) {
    this.classList.remove("drag-over");
}

async function dropCard(e) {
    e.preventDefault();
    this.classList.remove("drag-over");

    const newStatus = this.dataset.status;
    const taskId = draggedCard.dataset.id;

    // Move card visually
    this.querySelector(".kanban-list").appendChild(draggedCard);

    // Persist change in backend
    await fetch(`/tasks/update-status/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
    });
}


// Elements
const modal = document.getElementById("taskEditModal");
const closeBtn = document.getElementById("taskModalClose");
const cancelBtn = document.getElementById("cancelEditBtn");
const editButton = document.getElementById("editTasksBtn");


// CLOSE the modal (close button + cancel button)
closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
});
cancelBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
});

// CLOSE when clicking outside the modal-content
modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.add("hidden");
    }
});

editButton.addEventListener("click", () => {
    loadTasksIntoModal(window.allTasks);
    modal.classList.remove("hidden");
});

function loadTasksIntoModal(tasks) {
    const list = document.getElementById("task-edit-body");
    list.innerHTML = "";

    tasks.forEach(task => {
        list.appendChild(createTaskRow(task));
    });
}

function createTaskRow(task) {
    const row = document.createElement("div");
    row.classList.add("task-edit-row");
    row.dataset.id = task.id;
    row.setAttribute("draggable", "true");

    console.log(task);

    row.innerHTML = `
        <div class="drag-handle">☰</div>

        <input 
            type="text" 
            class="task-name-input" 
            value="${task.description}"
            draggable="true"
        >

        <select class="task-status-select">
            <option value="todo" ${task.completed === "False" ? "selected" : ""}>To Do</option>
            <option value="in_progress" ${task.status === "in_progress" ? "selected" : ""}>In Progress</option>
            <option value="done" ${task.completed === "True" ? "selected" : ""}>Done</option>
        </select>

        <button class="delete-task-btn" onclick="deleteTaskRow(this)">🗑️</button>
    `;

    return row;
}

// --------------------------------------------
// DRAGGABLE SORTING FOR TASK EDIT MODAL
// --------------------------------------------

let draggedRow = null;

// When drag starts
document.addEventListener("dragstart", (e) => {
    if (e.target.classList.contains("task-edit-row")) {
        draggedRow = e.target;
        e.target.classList.add("dragging");
    }
});

// When dragging ends
document.addEventListener("dragend", (e) => {
    if (e.target.classList.contains("task-edit-row")) {
        e.target.classList.remove("dragging");
        draggedRow = null;
    }
});

// When dragging over another task row
document.addEventListener("dragover", (e) => {
    e.preventDefault();

    const container = document.getElementById("task-edit-body");
    const afterElement = getDragAfterElement(container, e.clientY);

    if (!draggedRow) return;

    if (afterElement == null) {
        container.appendChild(draggedRow);
    } else {
        container.insertBefore(draggedRow, afterElement);
    }
});

// Helper: find the correct insert position
function getDragAfterElement(container, y) {
    const rows = [...container.querySelectorAll(".task-edit-row:not(.dragging)")];

    return rows.reduce(
        (closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;

            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        },
        { offset: Number.NEGATIVE_INFINITY }
    ).element;
}


function saveTasks() {
    const rows = document.querySelectorAll(".task-edit-row");

    const updatedOrder = [...rows].map(row => ({
        id: row.dataset.id,
        name: row.querySelector(".task-name-input").value,
        status: row.querySelector(".task-status-select").value
    }));

    console.log("Saving:", updatedOrder);

    fetch("/tasks/update-all/{{ project_id }}", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(updatedOrder)
    }).then(() => {
        location.reload();
    });
}


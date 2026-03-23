document.querySelectorAll(".task-checkbox").forEach(checkbox => {
    checkbox.addEventListener("change", async (event) => {
        const taskId = event.target.dataset.taskId;
        const isCompleted = event.target.checked;

        await updateTaskCompletion(taskId, isCompleted);
        updateProgressBar();
        updateUrgencyState();
    });
});

async function updateTaskCompletion(taskId, completed) {
    const res = await fetch(`/tasks/update/${taskId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ completed })
    });

    const data = await res.json();

    if (!data.success) {
        alert("Failed to update task.");
    }
}

function updateProgressBar() {
    const checkboxes = document.querySelectorAll(".task-checkbox");
    const total = checkboxes.length;
    const completedCount = Array.from(checkboxes).filter(cb => cb.checked).length;

    const percent = total > 0 
        ? Math.round((completedCount / total) * 100)
        : 0;

    const bar = document.getElementById("progress-bar");
    bar.style.width = percent + "%";
    bar.textContent = percent + "%";

    // NEW: update X/Y display
    const completedDisplay = document.getElementById("completed-tasks-display");
    if (completedDisplay) {
        completedDisplay.textContent = `${completedCount}/${total}`;
    }
}


function updateUrgencyState() {
    const tile = document.getElementById("deadline-tile");
    const valueElem = document.getElementById("days-remaining-val");
    const progressElem = document.getElementById("progress-bar");

    if (!tile || !valueElem || !progressElem) return;

    const progressVal = parseInt(progressElem.textContent.trim());
    const daysRemaining = parseInt(valueElem.textContent.trim());

    // If progress > 90% → clear warnings
    if (progressVal > 90) {
        tile.classList.remove("shake", "urgent");
        return;
    }

    // If progress <= 90 AND days < 5 → show warnings
    if (daysRemaining < 5) {
        tile.classList.add("shake", "urgent");
    } else {
        tile.classList.remove("shake", "urgent");
    }
}

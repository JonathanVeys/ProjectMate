document.querySelectorAll(".task-checkbox").forEach(checkbox => {
    checkbox.addEventListener("change", async (event) => {
        const taskId = event.target.dataset.taskId;
        const isCompleted = event.target.checked;

        await updateTaskCompletion(taskId, isCompleted);
        updateProgressBar();
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
}

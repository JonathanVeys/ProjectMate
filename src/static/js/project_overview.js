// API endpoint callers to gather user or project data
async function get_project_data(accessToken, project_id) {
    const response = await fetch(`/projects/${project_id}/data`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${accessToken}`
        }
    });

    if (!response.ok) {
        throw new Error("Failed to retrieve project data")
    }

    return await response.json();
}

async function get_tasks(accessToken, project_id) {
    const response = await fetch(`/tasks/${project_id}`, {
        method: "GET",
        headers: {
            Authorization: `Bearer ${accessToken}`
        }
    });

    if (!response.ok) {
        throw new Error("Failed to retrieve project data")
    }

    return await response.json();
}



// Update project functions
function update_element(content = "Loading...", element_id) {
    const element = document.getElementById(element_id);
    if (element) {
        element.textContent = content;
    }
}

async function update_task_completion(acessToken, taskId, completed) {
    const res = await fetch(`/tasks/update/${taskId}`, {
        method: "PATCH",
        headers: { 
            "Content-Type": "application/json",
            Authorization: `Bearer ${acessToken}`
        },
        body: JSON.stringify({ completed })
    });
    const data = await res.json();

    if (!data.success) {
        alert("Failed to update task.");
    }
}

async function show_tasks(tasks) {
    const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
    const accessToken = sessionData.session?.access_token;
    const container = document.getElementById("upcoming-tasks");
    tasks.forEach(task => {
        const taskEl = document.createElement("div");
        taskEl.className = "task-item";
        taskEl.innerHTML = `
            <input type="checkbox" id="task-${task.task_id}" data-task-id="${task.task_id}" ${task.completed ? "checked" : ""}>
            <label for="task-${task.task_id}">${task.description}</label>
        `;

        const checkbox = taskEl.querySelector("input[type='checkbox']");
        checkbox.addEventListener("change", async (event) => {
            const taskId = event.target.dataset.taskId;
            const isCompleted = event.target.checked;
            await update_task_completion(accessToken, taskId, isCompleted);
            update_progress_bar()
            // updateUrgencyState();
        });

        container.appendChild(taskEl);
    });
}

function update_progress_bar() {
    const checkboxes = document.querySelectorAll("#upcoming-tasks input[type='checkbox']");
    const total = checkboxes.length;
    const completedCount = Array.from(checkboxes).filter(cb => cb.checked).length;

    const percent = completedCount / total * 100;

    const bar = document.getElementById("progress-bar");
    bar.style.width = percent + "%";
    bar.textContent = percent + "%";
}



// Main document listener
document.addEventListener("DOMContentLoaded", async () => {
    const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
    const accessToken = sessionData.session?.access_token;
    const user = sessionData.session?.user ?? "User";
    const pathParts = window.location.pathname.split("/");
    const projectId = pathParts[pathParts.length - 1];

    if (!accessToken) {
        console.error("No access token found");
        return;
    }


    const project_data = await get_project_data(accessToken, projectId)
    const tasks = await get_tasks(accessToken, projectId)

    console.log(project_data);

    // User data
    const username = user?.user_metadata?.full_name

    // Project data
    const project_title = project_data?.title
    const project_deadline = project_data?.deadline
    const project_weighting = project_data?.weighting

    // Task data
    const completedTasks = tasks.filter(task => task.completed === true);
    const incompleteTasks = tasks.filter(task => task.completed === false); 

    update_element(`${username} ▼`, "username");
    update_element(project_title, "project-title");
    update_element(project_deadline, "metadata-deadline");
    update_element(project_weighting, "metadata-weighting");
    await show_tasks(tasks);
    update_progress_bar(completedTasks.length / tasks.length * 100, "progress-bar");
});






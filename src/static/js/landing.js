// --- Utility Functions ---

function load_avatar(avatar_url) {
    document.getElementById("avatar-icn").src = avatar_url;
}

function renderProjects(projects) {
    const container = document.getElementById("projects-container");
    const newProjectTile = document.getElementById("new-project-tile");

    projects.forEach(project => {
        const tile = document.createElement("div");
        tile.className = "tile";

        tile.innerHTML = `
            <h3>${project.title}</h3>
            <p>Deadline: ${project.deadline ?? "No deadline"}</p>
            <div class="tile-buttons">
                <button class="btn delete-project" data-project-id="${project.project_id}">Delete</button>
                <button class="btn open-project" data-project-id="${project.project_id}">Open</button>
            </div>
        `;
        container.insertBefore(tile, newProjectTile);
    });
}

// --- API Calls ---

async function get_projects(accessToken) {
    const response = await fetch("/projects/my-projects", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        const data = await response.json();
        const projects = data.projects || [];

    return projects;
}

async function deleteUser() {
    const confirmed = confirm(
        "Are you sure you want to delete your account? This action cannot be undone."
    );
    if (!confirmed) return;

    const res = await fetch("/delete", {
        method: "DELETE",
        credentials: "include",
    });

    if (res.ok) {
        window.location.href = "/";
    } else {
        alert("Failed to delete account. Please try again.");
    }
}

async function submitProjectForm(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
    const accessToken = sessionData.session?.access_token;

    // Show spinner
    document.getElementById("loading-overlay").classList.remove("hidden-loading");

    try {
        const response = await fetch("/projects/create", {
            method: "POST",
            headers : {
                Authorization: `Bearer ${accessToken}`
            },
            body: formData
        });

        const data = await response.json();

        closeModal();

        if (data.success) {
            location.reload();
        } else {
            alert("Error creating project");
        }
    } catch (err) {
        console.error(err);
        alert("Unexpected error");
    } finally {
        // Hide spinner after everything completes
        document.getElementById("loading-overlay").classList.add("hidden-loading");
    }
}

async function handle_delete(project_id, accessToken) {
    try {
        const response = await fetch(`/projects/delete/${project_id}`, {
            method: "DELETE",
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            throw new Error("Failed to delete project");
        }

        location.reload();
    } catch (err) {
        console.error(err);
        alert("Error deleting project");
    }
}

// --- UI Functions ---

function openModal() {
    document.getElementById("newProjectModal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("newProjectModal").classList.add("hidden");
}

// --- Initialisation ---

async function init() {
    const { data: sessionData, error: sessionError } = await supabaseClient.auth.getSession();
    const accessToken = sessionData.session?.access_token;
    const user = sessionData.session?.user;

    if (!accessToken || !user) return;  // ← add this

    const projects = await get_projects(accessToken)
    const avatar_url = user?.user_metadata?.avatar_url;

    renderProjects(projects);
    load_avatar(avatar_url);
}

// --- Event Listeners ---

document.addEventListener("DOMContentLoaded", init);

// Linstener for handling project logic
document.addEventListener("click", async (event) => {
    const deleteButton = event.target.closest(".delete-project");
    const openButton = event.target.closest(".open-project");

    if (!deleteButton && !openButton) return;

    const { data: sessionData } = await supabaseClient.auth.getSession();
    const accessToken = sessionData.session?.access_token;

    if (deleteButton) {
        const projectId = deleteButton.dataset.projectId;
        await handle_delete(projectId, accessToken);
    }

    if (openButton) {
        const projectId = openButton.dataset.projectId;
        window.location.href = `/pages/projects/${projectId}`;
    }
})




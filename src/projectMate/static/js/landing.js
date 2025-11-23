// Function to delete a project
async function deleteProject(id) {
    if (!confirm("Are you sure you want to delete this project?")) return;

    const res = await fetch(`/projects/delete/${id}`, {
        method: "DELETE"
    });

    const data = await res.json();

    if (data.success) {
        window.location.reload();
    } else {
        alert(data.error);
    }
}


// Open model
function openModal() {
    document.getElementById("newProjectModal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("newProjectModal").classList.add("hidden");
}

// async function submitProjectForm(event) {
//     event.preventDefault();

//     const form = event.target;
//     const formData = new FormData(form);

//     const response = await fetch("/projects/create", {
//         method: "POST",
//         body: formData
//     });

//     const data = await response.json();

//     closeModal()
//     if (data.success) {
//         location.reload();
//     } else {
//         alert("Error creating project");
//     }
// }

async function submitProjectForm(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Show spinner
    document.getElementById("loading-overlay").classList.remove("hidden-loading");

    try {
        const response = await fetch("/projects/create", {
            method: "POST",
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

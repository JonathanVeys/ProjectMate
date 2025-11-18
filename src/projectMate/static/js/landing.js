// Function to create a new project
async function createProject() {
    const title = prompt("Enter project title:");
    if (!title) return;

    try {
        const res = await fetch("/projects/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title })
        });

        const data = await res.json();

        if (data.success) {
            window.location.reload();  
        } else {
            alert("Error: " + data.error);
        }
    } catch (err) {
        console.error(err);
        alert("Something went wrong.");
    }
}

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

// Function to handle menu bar
function toggleUserMenu() {
    const menu = document.getElementById("userDropdown");
    menu.classList.toggle("open");
}

// Close menu if user clicks outside
document.addEventListener("click", function(event) {
    const menu = document.querySelector(".user-menu");
    const dropdown = document.getElementById("userDropdown");

    if (!menu.contains(event.target)) {
        dropdown.classList.remove("open");
    }
});
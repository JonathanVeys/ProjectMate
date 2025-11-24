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
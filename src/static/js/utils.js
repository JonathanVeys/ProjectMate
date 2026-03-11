// Supabase client - shared across all pages
const SUPABASE_URL = "https://bagwatovrhptoojzjfhz.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJhZ3dhdG92cmhwdG9vanpqZmh6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM0NTI2MTIsImV4cCI6MjA3OTAyODYxMn0.Qh1tSXVlrnEBWoE8ZGGkWPY1ygUpPTtGdC4z4ZKwCSc";
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);



// Function to handle menu bar
function toggleUserMenu() {
    const menu = document.getElementById("userDropdown");
    menu.classList.toggle("open");
}

// Close menu if user clicks outside
document.addEventListener("click", function(event) {
    const menu = document.querySelector(".user-menu");
    const dropdown = document.getElementById("userDropdown");

    if (!menu || !dropdown) return; 

    if (!menu.contains(event.target)) {
        dropdown.classList.remove("open");
    }
});


document.addEventListener("DOMContentLoaded", () => {
    const deleteLink = document.getElementById("deleteAccount");
    console.log(deleteLink);
    if (!deleteLink) return;

    deleteLink.addEventListener("click", (e) => {
        e.preventDefault(); 
        deleteUser();
    });
});

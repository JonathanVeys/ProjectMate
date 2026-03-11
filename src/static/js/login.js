function redirectUrl() {
  return window.location.origin + "/pages/landing";
}

// Google login handler
async function signInWithGoogle() {
  return supabaseClient.auth.signInWithOAuth({
    provider: "google",
    options: { redirectTo: redirectUrl() }
  });
}

// Github login handler
async function signInWithGithub() {
  return supabaseClient.auth.signInWithOAuth({
    provider: "github",
    options: { redirectTo: redirectUrl() }
  });
}

async function signUpNewUser() {
  const email = document.getElementById("signup-email-address").value;
  const password = document.getElementById("signup-password").value;
  const username = document.getElementById("signin-name").value;

  const { data, error } = await supabaseClient.auth.signUp({
    email: email,
    password: password,
    options: {
      emailRedirectTo: 'http://127.0.0.1:8000/pages/landing',
      data: {
            full_name: username 
        }
    },
  })

  if (error) {
      alert(error.message);
  } else {
      alert("Check your email to confirm your account!");
      show_login(); 
  }
}

async function signInWithEmail() {
  const email = document.getElementById("signin-email-address").value;
  const password = document.getElementById("signin-password").value;

  const { data, error } = await supabaseClient.auth.signInWithPassword({
        email: email,
        password: password,
    });

    if (error) {
        alert(error.message);
    } else {
        window.location.href = redirectUrl();
    }
}


// Attach event listeners once DOM loads
document.addEventListener("DOMContentLoaded", () => {
  const googleBtn = document.getElementById("google-login");
  const githubBtn = document.getElementById("github-login");
  const signupBtn = document.getElementById("sign-up-btn");
  const signinBtn = document.getElementById("sign-in-btn");

  if (googleBtn) googleBtn.addEventListener("click", signInWithGoogle);
  if (githubBtn) githubBtn.addEventListener("click", signInWithGithub);
  if (signupBtn) signupBtn.addEventListener("click", signUpNewUser);
  if (signinBtn) signinBtn.addEventListener("click", signInWithEmail);
});






// Function to hide the login div and show the sign up div
async function show_signup(){
    const logInDiv = document.getElementById("login-div");
    const SignUpDiv = document.getElementById("sign-up-div");
    const signupForm = document.getElementById("signup-form");

    signupForm.reset()
    logInDiv.style.display = "none";
    SignUpDiv.style.display = "flex";
}

// Function to hide the signup div and show the login div
async function show_login(){
    const logInDiv = document.getElementById("login-div");
    const SignUpDiv = document.getElementById("sign-up-div");

    logInDiv.style.display = "flex";
    SignUpDiv.style.display = "none";


}

// Event listeners to listen for when either the signup of back buttons are pressed to hide or show the divs
document.addEventListener("DOMContentLoaded", () => {
    const signUpBtn = document.getElementById("show-sign-up-btn");

    signUpBtn.addEventListener("click", show_signup);
});

document.addEventListener("DOMContentLoaded", () => {
    const signUpBtn = document.getElementById("signup-back-btn");

    signUpBtn.addEventListener("click", show_login);
});
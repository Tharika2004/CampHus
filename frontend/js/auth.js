// ===============================
// 📧 EMAILJS CONFIG
// ===============================
const SERVICE_ID = "service_egj2sgk";
const TEMPLATE_ID = "template_ya33paa";
const PUBLIC_KEY = "n5d8umgXLeW0FsXxA";

// init emailjs
(function(){
  if(typeof emailjs !== "undefined"){
    emailjs.init(PUBLIC_KEY);
  }
})();

// ===============================
// 🔢 GENERATE OTP
// ===============================
function generateOTP(){
  return Math.floor(100000 + Math.random()*900000).toString();
}

// ===============================
// 📩 SEND OTP 
// ===============================

function sendOTP(email){
  const generatedOTP = generateOTP();
  const otpExpiry = Date.now() + 5 * 60 * 1000; 

  localStorage.setItem("otp", generatedOTP);
  localStorage.setItem("otpExpiry", otpExpiry);
  localStorage.setItem("otpEmail", email);

  
  return emailjs.send(SERVICE_ID, TEMPLATE_ID, {
    to_email: email,
    otp: generatedOTP
  }); 
}
// ===============================
// ✅ VERIFY OTP & REGISTER
// ===============================
async function verifyOTP(){
  const entered = document.getElementById("otp").value.trim();
  const savedOTP = localStorage.getItem("otp");
  const expiry = localStorage.getItem("otpExpiry");

  if(!expiry || Date.now() > parseInt(expiry)){
    alert("OTP expired ❌ Please register again.");
    window.location.href = "register.html";
    return;
  }

  if(entered != savedOTP){
    alert("Wrong OTP ❌");
    return;
  }

  const tempUserData = localStorage.getItem("tempUser");
  if(tempUserData){
    let user = JSON.parse(tempUserData);
    
    // --- DATABASE SYNC ---
    try {
      await fetch('https://tharika2004-event-project.hf.space/sync-user', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
              name: user.name, 
              email: user.email 
          })
      });
    } catch (err) {
      console.warn("DB Sync failed, but proceeding locally.");
    }

    let users = JSON.parse(localStorage.getItem("users")) || [];
    if(!users.find(u => u.email === user.email)){
        users.push(user);
        localStorage.setItem("users", JSON.stringify(users));
    }
    
    localStorage.setItem("loggedInUser", user.name);
    localStorage.setItem("userEmail", user.email);
    localStorage.setItem("isLoggedIn", "true");

    localStorage.removeItem("tempUser");
    localStorage.removeItem("otp");

    alert("Verified & Registered Successfully! ✅");
    window.location.href = "home.html";
  }
}

// ===============================
// 🔐 PASSWORD HASHING (SHA-256)
// ===============================
async function hashPassword(password){
  const msgBuffer = new TextEncoder().encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2,'0')).join('');
}
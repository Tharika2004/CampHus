const API_URL = "https://tharika2004-event-project.hf.space/get-events";
let events = [];

// 1. Backend and Local Storage sync function
async function syncEventsWithBackend() {
    const container = document.getElementById("events");
    if (!container) return;

    try {
        console.log("📡 Fetching from Backend (Cloudinary Ready)...");
        
        // Fetch from Hugging Face API
        const response = await fetch(`${API_URL}?t=${Date.now()}`);
        const backendData = await response.json();
        
        // Retrieve locally posted events (if any)
        const localEvents = JSON.parse(localStorage.getItem("myPostedEvents") || "[]");

        // Merge both sources
        events = [...backendData, ...localEvents];
        
        console.log("✅ Total Events Loaded:", events.length);
        displayCards(events);

    } catch (error) {
        console.warn("Backend failed. Loading local fallback...", error.message);
        const localEvents = JSON.parse(localStorage.getItem("myPostedEvents") || "[]");
        displayCards(localEvents);
    }
}

// 2. Updated displayCards Function (Optimized for Cloudinary)
function displayCards(list) {
    const container = document.getElementById("events");
    if (!container) return;
    container.innerHTML = "";

    const wishlist = JSON.parse(localStorage.getItem("wishlist") || "[]");
    const isMyEventsPage = document.getElementById('pageTitle')?.innerText === "My Registered Events";

    if (list.length === 0) {
        container.innerHTML = "<p style='grid-column: 1/-1; text-align: center; color: #A3AED0; padding: 40px;'>No events found.</p>";
        return;
    }

    list.forEach((e) => {
        const name = e.event_name || "Untitled Event";
        const college = e.college_name || "College Campus";
        const type = e.event_type || "Event";
        const date = e.event_date || "Upcoming";
        
        const isSaved = wishlist.some(item => String(item.id) === String(e.id));
        const activeClass = isSaved ? 'active' : '';

        let finalImgUrl = e.poster_image || `https://picsum.photos/seed/${e.id || name}/400/250`;

        container.innerHTML += `
        <div class="event-card" style="background: var(--card-bg); border-radius: 20px; padding: 12px; border: 1px solid var(--border); position: relative;">
          <div class="img-wrapper">
            <div class="category-badge" style="position: absolute; top: 10px; left: 10px; background: rgba(147, 51, 234, 0.85); color: white; padding: 4px 10px; border-radius: 15px; font-size: 10px; font-weight: 600; z-index: 5;">${type}</div>
            <img src="${finalImgUrl}" alt="${name}" style="width: 100%; height: 100%; object-fit: cover;"
                 onerror="this.onerror=null; this.src='https://via.placeholder.com/400/250?text=Image+Not+Found'">
            <button class="save-btn ${activeClass}" onclick="toggleWishlist(${e.id})">
                <i data-lucide="heart"></i>
            </button>
          </div>
          <div class="card-body">
            <div style="font-size: 10px; color: #9333ea; font-weight: 700; margin-bottom: 5px; text-transform: uppercase;">${date}</div>
            <h3 style="font-size: 15px; color: var(--text-main); margin: 0 0 5px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${name}</h3>
            <p style="font-size: 12px; color: var(--text-dim); margin-bottom: 10px;">📍 ${college}</p>
            
            <button class="details-btn-single" onclick="goToDetails(${e.id})">View / Register</button>

            ${isMyEventsPage ? `
                <button onclick="removeFromMyEvents(${e.id})" 
                        style="width: 100%; padding: 8px; margin-top: 10px; border-radius: 25px; 
                               background: #fee2e2; color: #ef4444; border: 1px solid #ef4444; 
                               cursor: pointer; font-weight: 600; font-size: 11px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                    <i data-lucide="trash-2" size="14"></i> Remove
                </button>
            ` : ''}
          </div>
        </div>`;
    });

    if (window.lucide) lucide.createIcons();
}

// Start
window.addEventListener('load', syncEventsWithBackend);

// Search Logic
const searchInput = document.getElementById("searchInput");

if (searchInput) {
    searchInput.onkeyup = (e) => {
        const term = e.target.value.toLowerCase().trim();
        
        // Term empty-ah irundha ella events-ayum thirumba kaattuvom
        if (term === "") {
            displayCards(events);
            return;
        }

        const filtered = events.filter(ev => {
            // Database-la irundhu varra values-ai safe-ah string-ah maathikuvom
            const name = (ev.event_name || "").toLowerCase();
            const state = (ev.state || "").toLowerCase(); // New: State filter
            const venue = (ev.venue || "").toLowerCase(); // New: Venue filter
            const type = (ev.event_type || "").toLowerCase();
            const date = (ev.event_date || "").toLowerCase(); // New: Date filter
            const city = (ev.city || "").toLowerCase(); // New: city filter 
            // Check if search term matches ANY of these fields
            return name.includes(term) ||  
                   state.includes(term) || 
                   venue.includes(term) || 
                   type.includes(term) || 
                   date.includes(term) ||
                   city.includes(term);
        });

        displayCards(filtered);
    };
}

// Optimized Tag Filter Logic
document.addEventListener('click', function (e) {
    const tag = e.target.closest('.tag');
    if (!tag) return;

    // 1. UI update: Active class setup
    document.querySelectorAll('.tag').forEach(t => t.classList.remove('active'));
    tag.classList.add('active');

    const selectedTag = tag.textContent.trim().toLowerCase();
    const titleElem = document.getElementById('pageTitle');

    if (selectedTag === "trending") {
        if (titleElem) titleElem.innerText = "Campus Vibes";
        displayCards(events);
    } else {
        if (titleElem) titleElem.innerText = tag.textContent;
        
        const filtered = events.filter(ev => {
            const dbType = (ev.event_type || "").toLowerCase();
            const dbName = (ev.event_name || "").toLowerCase();
            
        
            return dbType.includes(selectedTag) || dbName.includes(selectedTag);
        });
        
        displayCards(filtered);
    }
});

function toggleWishlist(eventId) {
    // 1. Current event-ai 'events' array-la irundhu kandupidikalam
    const eventToSave = events.find(ev => ev.id === eventId);
    if (!eventToSave) return;

    // 2. LocalStorage-la irundhu current wishlist-ai edukkalam
    let wishlist = JSON.parse(localStorage.getItem("wishlist") || "[]");

    // 3. Check if already exists
    const index = wishlist.findIndex(item => item.id === eventId);

    if (index === -1) {
        // Illana: Add pannu
        wishlist.push(eventToSave);
        console.log("❤ Event saved to wishlist");
    } else {
        // Irundha: Remove pannu
        wishlist.splice(index, 1);
        console.log("💔 Event removed from wishlist");
    }

    // 4. Update LocalStorage & UI
    localStorage.setItem("wishlist", JSON.stringify(wishlist));
    displayCards(events); // Refresh cards to show heart color change
}
// app.js - Common Dark Mode Logic
function toggleDarkMode() {
    // 1. Check current state and toggle
    const isDark = document.documentElement.classList.toggle('dark-theme');
    
    // 2. Save to Local Storage
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    
    // 3. Update Icon and Text (Home page sidebar-kaga)
    updateThemeUI(isDark);
}

function updateThemeUI(isDark) {
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');
    
    if (themeIcon && themeText) {
        themeText.innerText = isDark ? "Light Mode" : "Dark Mode";
        // Lucide icon-ai dinamiga maatha mudiyum
        themeIcon.setAttribute('data-lucide', isDark ? 'sun' : 'moon');
        if (window.lucide) lucide.createIcons();
    }
}

// 4. Page load aagumbodhu theme-ai apply panna:
(function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark-theme');
        // UI elements update panna load-ku appuram wait panrom
        window.addEventListener('load', () => updateThemeUI(true));
    }
})();

function goToDetails(id) {
    window.location.href = `event.html?id=${id}`;
}
// --- Logout Logic (Common for all pages) ---
function logout() {
    // Confirmation dialog before logging out
    if (confirm("Are you sure you want to logout? 🔒")) {
        
        // 1. Clear session keys only (Keep theme/preferences)
        localStorage.removeItem("loggedInUser");
        localStorage.removeItem("userEmail");
        localStorage.removeItem("isLoggedIn");
        
        // Optional: If you want to clear EVERYTHING (including theme), use:
        // localStorage.clear();

        console.log("🚪 User logged out successfully.");

        // 2. Redirect to Login Page
        window.location.href = "login.html";
    }
}

// --- Page Protection (Security Check) ---
// Intha code page load aagum podhu user login panni irukkangalanu check pannum
(function() {
    const user = localStorage.getItem("loggedInUser");
    // Path check: Login page-la irundha intha check thevai illai
    const isLoginPage = window.location.pathname.includes("login.html") || window.location.pathname.endsWith("/");
    
    if (!user && !isLoginPage) {
        // User login pannama direct-ah home/settings-ku vandha, login-ku thalliduvom
        window.location.href = "login.html";
    }
})();

function showMyRegisteredEvents(btn) {
    // 1. Sidebar UI Update
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // 2. Change Title (This is important for the button to show up)
    document.getElementById('pageTitle').innerText = "My Registered Events";

    // 3. Get Data and Display
    const registered = JSON.parse(localStorage.getItem("myRegisteredEvents") || "[]");
    displayCards(registered); 
}
function removeFromMyEvents(id) {
    // English Confirmation
    if (confirm("Are you sure you want to remove this event from your list?")) {
        // 1. Get current list
        let registered = JSON.parse(localStorage.getItem("myRegisteredEvents") || "[]");
        
        // 2. Filter logic (String match ensures it works even if ID is a number)
        const updatedList = registered.filter(e => String(e.id) !== String(id));
        
        // 3. Save back to LocalStorage
        localStorage.setItem("myRegisteredEvents", JSON.stringify(updatedList));
        
        console.log("Event Removed. Updated count:", updatedList.length);

        // 4. UI Refresh
        // Namma current-ah "My Registered Events" page-la irukkurathaala 
        // thirumba showMyRegisteredEvents call panna cards update aagidum
        const activeBtn = document.querySelector('.nav-btn.active');
        showMyRegisteredEvents(activeBtn);
        
        // Lucide icons refresh
        if (window.lucide) lucide.createIcons();
    }
}
// Sidebar Toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }
}

// Navigation
function goTo(page) { window.location.href = page + ".html"; }

function preparePost() {
    localStorage.removeItem("editIndex");
    window.location.href = "post.html";
}

// Typing Animation
const textArray = ["Vibes", "Hackathons", "Workshops", "Symposiums", "Fests"];
let textIndex = 0, charIndex = 0, isDeleting = false;

function typeText() {
    const textElement = document.querySelector(".change-text");
    if (!textElement) return;
    const currentText = textArray[textIndex];
    textElement.textContent = isDeleting ? currentText.substring(0, charIndex - 1) : currentText.substring(0, charIndex + 1);
    charIndex = isDeleting ? charIndex - 1 : charIndex + 1;
    let speed = isDeleting ? 80 : 150;
    if (!isDeleting && charIndex === currentText.length) { speed = 2000; isDeleting = true; }
    else if (isDeleting && charIndex === 0) { isDeleting = false; textIndex = (textIndex + 1) % textArray.length; speed = 500; }
    setTimeout(typeText, speed);
}
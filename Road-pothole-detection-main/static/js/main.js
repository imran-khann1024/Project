/* ==========================================
   AI POTHOLE DETECTION
   main.js
==========================================*/

// ==========================
// Show Selected File Name
// ==========================

const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            fileName.innerHTML =
                `<strong>Selected:</strong> ${this.files[0].name}`;

        } else {

            fileName.innerHTML =
                "Drag & Drop or Browse File";

        }

    });

}

// ==========================
// Loading Screen
// ==========================

const uploadForm = document.getElementById("uploadForm");
const loading = document.getElementById("loadingScreen");

if (uploadForm) {

    uploadForm.addEventListener("submit", function () {

        loading.style.display = "flex";

    });

}

// ==========================
// Scroll Animation
// ==========================

const fadeElements = document.querySelectorAll(
    ".about-card, .feature-card, .contact-card, .stat-item, .upload-card"
);

const observer = new IntersectionObserver(

    entries => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                entry.target.classList.add("active");

            }

        });

    },

    {
        threshold: 0.2
    }

);

fadeElements.forEach(el => {

    el.classList.add("fade-in");

    observer.observe(el);

});

// ==========================
// Counter Animation
// ==========================

const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {

    const text = counter.innerText;

    if (text.includes("%") || text.includes("+") || isNaN(text)) return;

    const target = parseInt(text);

    let count = 0;

    const update = () => {

        count += Math.ceil(target / 100);

        if (count < target) {

            counter.innerText = count;

            requestAnimationFrame(update);

        } else {

            counter.innerText = target;

        }

    };

    update();

});

// ==========================
// Navbar Shadow on Scroll
// ==========================

const header = document.querySelector("header");

window.addEventListener("scroll", () => {

    if (window.scrollY > 60) {

        header.style.boxShadow =
            "0 10px 30px rgba(0,0,0,0.15)";

    } else {

        header.style.boxShadow =
            "0 5px 20px rgba(0,0,0,0.08)";

    }

});

// ==========================
// Smooth Scroll
// ==========================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        const target = document.querySelector(
            this.getAttribute("href")
        );

        if (target) {

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});

// ==========================
// Detect Button Animation
// ==========================

const detectBtn = document.getElementById("detectBtn");

if (detectBtn) {

    detectBtn.addEventListener("mouseenter", () => {

        detectBtn.style.transform = "scale(1.05)";

    });

    detectBtn.addEventListener("mouseleave", () => {

        detectBtn.style.transform = "scale(1)";

    });

}

// ==========================
// Console Message
// ==========================

console.log("🚧 AI Pothole Detection Website Loaded Successfully");
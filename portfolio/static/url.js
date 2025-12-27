// Handle header padding for fixed header
let header = document.querySelector("header");
let main = document.querySelector("main");

if (header && main) {
  main.style.paddingTop = header.offsetHeight + "px";
}

// Mobile menu toggle
let link = document.querySelector(".links");

function menu() {
  if (link) {
    link.classList.toggle("active");
  }
}

// Close menu when link is clicked (mobile)
document.querySelectorAll(".links a").forEach(link => {
  link.addEventListener("click", function() {
    document.querySelector(".links").classList.remove("active");
  });
});

// Smooth scroll behavior for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// Header shadow on scroll
window.addEventListener("scroll", function() {
  const header = document.querySelector("header");
  if (window.scrollY > 10) {
    header.style.boxShadow = "0 8px 16px rgba(214, 52, 71, 0.15)";
  } else {
    header.style.boxShadow = "0 2px 8px rgba(214, 52, 71, 0.1)";
  }
});

// Add animation on scroll for cards
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px"
};

const observer = new IntersectionObserver(function(entries) {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1";
      entry.target.style.transform = "translateY(0)";
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe all cards
document.querySelectorAll(".card").forEach(card => {
  card.style.opacity = "0";
  card.style.transform = "translateY(20px)";
  card.style.transition = "all 0.5s ease";
  observer.observe(card);
});

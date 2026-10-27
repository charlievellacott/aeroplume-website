const toggle = document.querySelector(".nav-toggle");
const nav = document.querySelector("header.site nav");

if (toggle && nav) {
  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
}

document.getElementById("year")?.replaceChildren(document.createTextNode(String(new Date().getFullYear())));

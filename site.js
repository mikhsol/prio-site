document.querySelectorAll("[data-language-selector]").forEach((selector) => {
  selector.addEventListener("change", (event) => {
    const destination = event.currentTarget.value;
    if (destination) {
      window.location.assign(destination);
    }
  });
});

document.querySelectorAll("[data-mobile-menu]").forEach((menu) => {
  const summary = menu.querySelector("summary");
  const label = menu.querySelector(".mobile-menu__label");

  const updateLabel = () => {
    const text = menu.open
      ? summary.dataset.closeLabel
      : summary.dataset.openLabel;
    summary.setAttribute("aria-label", text);
    label.textContent = text;
  };

  menu.addEventListener("toggle", updateLabel);
  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      menu.open = false;
    });
  });
  menu.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      summary.focus();
    }
  });
  updateLabel();
});

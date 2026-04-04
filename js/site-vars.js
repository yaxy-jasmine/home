// Site-wide variables — add new entries here as needed
var SITE = {
  name: "Jasmine Yaxin Zheng",
  short_name: "Jasmine Zheng",
};

// Apply variables to the page
document.addEventListener("DOMContentLoaded", function () {
  // Update elements with class "site-name" (full name)
  document.querySelectorAll(".site-name").forEach(function (el) {
    el.textContent = SITE.name;
  });

  // Update elements with class "site-short-name" (short name)
  document.querySelectorAll(".site-short-name").forEach(function (el) {
    el.textContent = SITE.short_name;
  });

  // Update document title (uses short name)
  document.title = document.title
    .replace("Jasmine Yaxin Zheng", SITE.name)
    .replace("Jasmine Zheng", SITE.short_name);

  // Replace {site_name} and {site_short_name} in meta tags and other attributes
  var meta = document.querySelector('meta[name="description"]');
  if (meta) {
    meta.content = meta.content.replace("{site_name}", SITE.name);
    meta.content = meta.content.replace("{site_short_name}", SITE.short_name);
  }

  document.querySelectorAll('img[alt*="{site_name}"]').forEach(function (img) {
    img.alt = img.alt.replace("{site_name}", SITE.name);
  });
});

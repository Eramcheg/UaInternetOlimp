function getNavBarMetaConfig() {
  const metaTag = document.querySelector('meta[name="navbar-config"]');
  if (metaTag) {
    try {
      return JSON.parse(metaTag.getAttribute("content"));
    } catch (e) {
      console.error("Error while parsing mini-cart-urls", e);
    }
  } else {
    console.error('Meta tag "django-urls" has not been found');
  }
  return {};
}
const navBarConfig = getNavBarMetaConfig();
document.addEventListener("DOMContentLoaded", () => {
    let dropdownTrigger = document.getElementById("dropdownTrigger");
    let overlay = document.getElementById("overlay-mobile");
    let menuIcon = document.getElementById("menuIcon");

    dropdownTrigger.addEventListener("click", function() {
        overlay.classList.toggle("visible");
        overlay.classList.toggle("hidden");
        menuIcon.src = overlay.classList.contains("visible")
            ? navBarConfig.crossIcon
            : navBarConfig.menuIcon;
    });

    // Закрываем оверлей при клике на любую ссылку или на сам оверлей
    overlay.addEventListener("click", function(e) {
        if (e.target === overlay || e.target.tagName === "A") {
            overlay.classList.remove("visible");
            overlay.classList.add("hidden");
            menuIcon.src = navBarConfig.menuIcon;
        }
    });

    const toggle = document.getElementById("results-toggle");
    const menu = document.getElementById("results-menu");
    if (toggle && menu) {
        toggle.addEventListener("click", function (e) {
          e.preventDefault();
          menu.style.display = menu.style.display === "flex" ? "none" : "flex";
        });
        // Закрытие меню при клике вне его
        document.addEventListener("click", function (e) {
          if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            menu.style.display = "none";
          }
        });
    }

});


function dropdownTrigger(){
    const dropdownMenu = document.getElementById('accountDropdownMenu');
    dropdownMenu.classList.toggle('open');
    event.stopPropagation();
}

document.addEventListener('click', function() {
    const dropdownMenu = document.getElementById('dropdownMenu');
    if(document.getElementById('accountDropdownMenu')) {
        const accountDropdownMenu = document.getElementById('accountDropdownMenu');
        dropdownMenu.style.display = 'none';
        accountDropdownMenu.classList.remove('open');
    }
});

window.addEventListener('scroll', function() {
    let toolbar = document.querySelector('.toolbar');
    // Check if the page is scrolled more than 50 pixels
    if(window.pageYOffset > 50) {
        // User has scrolled down, shrink the toolbar
        toolbar.classList.remove('large');
        toolbar.classList.add('small');
    } else {
        // User is near the top of the page, expand the toolbar
        toolbar.classList.remove('small');
        toolbar.classList.add('large');
    }
});

document.getElementById('overlay').addEventListener('click', function() {
    document.getElementById('cartPanel').classList.remove('open');
    document.getElementById('side_acc_wrap').classList.remove('open');
    this.style.display = 'none'; // Hide the overlay
});
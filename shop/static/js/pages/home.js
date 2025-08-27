function setupItemsCarousel(){
    const prev = document.getElementById('prev-btn');
    const next = document.getElementById('next-btn');
    const list = document.getElementById('item-list');

    const itemWidth = 250;
    let autoScroll = setInterval(function () {
        list.scrollLeft += itemWidth;
        // Reset to the beginning if it reaches the end
        if (list.scrollWidth - list.clientWidth === list.scrollLeft) {
            list.scrollLeft = 0;
        }
    }, 6000); // Scroll every 9000 milliseconds

    prev.addEventListener('click', () => {
        list.scrollLeft -= itemWidth;  // Adjusted to include gap
        resetAutoScroll();
    });
    next.addEventListener('click', () => {
        list.scrollLeft += itemWidth;  // Adjusted to include gap
        resetAutoScroll();
    });

    function resetAutoScroll() {
        clearInterval(autoScroll);
        autoScroll = setInterval(function () {
            list.scrollLeft += itemWidth;
            // Reset to the beginning if it reaches the end
            if (list.scrollWidth - list.clientWidth === list.scrollLeft) {
                list.scrollLeft = 0;
            }
        }, 6000);
    }
}
document.addEventListener("DOMContentLoaded", function() {
    setupItemsCarousel();
    const milestones = document.querySelectorAll(".milestone");
    const progressBar = document.querySelector(".progress");
    const currentDateElem = document.getElementById("currentDate");

    const currentDate = new Date();
    currentDateElem.textContent = currentDate.toLocaleDateString();

    let startDate = new Date(milestones[0].dataset.date);
    let endDate = new Date(milestones[milestones.length - 1].dataset.date);

    milestones.forEach((milestone, index) => {
        let milestoneDate = new Date(milestone.dataset.date);

        // Рассчитываем позицию контрольной точки в процентах от начала
        let milestonePercent = ((milestoneDate - startDate) / (endDate - startDate)) * 100;

        if (window.innerWidth <= 768) {
            // Если это мобильное устройство, позиционируем по top
            milestone.style.top = `${milestonePercent}%`;
        } else {
            // Для десктопов позиционируем по left
            milestone.style.left = `${milestonePercent}%`;
        }

        // Если текущая дата больше или равна дате контрольной точки, активируем её
        if (currentDate >= milestoneDate) {
            milestone.classList.add("active");

            if (index < milestones.length - 1) {
                let nextMilestoneDate = new Date(milestones[index + 1].dataset.date);
                let nextMilestonePercent = ((nextMilestoneDate - startDate) / (endDate - startDate)) * 100;

                let progressPercent = milestonePercent + ((nextMilestonePercent - milestonePercent) * (currentDate - milestoneDate) / (nextMilestoneDate - milestoneDate));

                if (window.innerWidth <= 768) {
                    // Для мобильных устройств прогресс измеряем по высоте
                    progressBar.style.height = `${progressPercent}%`;
                } else {
                    // Для десктопов измеряем по ширине
                    progressBar.style.width = `${progressPercent}%`;
                }
            } else {
                if (window.innerWidth <= 768) {
                    progressBar.style.height = `${milestonePercent}%`;
                } else {
                    progressBar.style.width = `${milestonePercent}%`;
                }
            }
        }
    });
    if (currentDate >= endDate) {
        if (window.innerWidth <= 768) {
            progressBar.style.height = "100%";
        } else {
            progressBar.style.width = "100%";
        }
    }
});
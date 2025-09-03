function initPagination(wrapper, fullData, buildTable) {
    let itemsPerPageElement = wrapper.querySelector('#items-per-page');
    let currentPage = 1;
    let itemsPerPage = itemsPerPageElement
        ? parseInt(itemsPerPageElement.value, 10)
        : 10;
    let totalPages = Math.ceil(fullData.length / itemsPerPage);
    function render() {
        totalPages = Math.ceil(fullData.length / itemsPerPage);
        const start = (currentPage - 1) * itemsPerPage;
        const pageItems = fullData.slice(start, start + itemsPerPage);

        wrapper.dataset.startIndex = start;
        buildTable(pageItems, wrapper.querySelector('tbody'));

        updateControls();
        updateInfo(pageItems.length);
    }
    function updateControls() {
        const paginationContainer = wrapper.querySelector('.pagination');
        paginationContainer.innerHTML = '';

        const first = document.createElement('span');
        first.textContent = '1';
        first.classList.add('firstPageContainer');
        if (currentPage > 1) {
          first.classList.add('clickable');
          first.addEventListener('click', () => goTo(1));
        } else {
          first.classList.add('disabled', );
        }
        paginationContainer.appendChild(first);

        const prev = document.createElement('i');
        prev.classList.add('fa-solid','fa-chevron-left','previousContainer');
        console.log(currentPage);
        if (currentPage > 1) {
          console.log(true);
          prev.classList.add('clickable');
          prev.addEventListener('click', () => goTo(currentPage - 1));
        } else {
          prev.classList.add('disabled');
        }
        paginationContainer.appendChild(prev);

        const input = document.createElement('input');
        input.type = 'number';
        input.value = currentPage;
        input.min = 1;
        input.max = totalPages;
        input.addEventListener('change', () => {
          const v = parseInt(input.value, 10);
          if (v >= 1 && v <= totalPages) goTo(v);
          else input.value = currentPage;
        });
        paginationContainer.appendChild(input);

        const next = document.createElement('i');
        next.className = 'fa-solid fa-chevron-right';
        next.classList.add('nextContainer');
        if (currentPage < totalPages) {
          next.classList.add('clickable');
          next.addEventListener('click', () => goTo(currentPage + 1));
        } else {
          next.classList.add('disabled');
        }
        paginationContainer.appendChild(next);

        const last = document.createElement('span');
        last.textContent = totalPages;
        last.classList.add('lastPageContainer');
        if (currentPage < totalPages) {
          last.classList.add('clickable');
          last.addEventListener('click', () => goTo(totalPages));
        } else {
          last.classList.add('disabled');
        }
        paginationContainer.appendChild(last);
    }
    function updateInfo(shownCount) {
        const info = wrapper.querySelector('.pgntn-info');
        const start = (currentPage - 1) * itemsPerPage + 1;
        const end = start + shownCount - 1;
        info.textContent = `Viewing ${start}-${end} out of ${fullData.length} (page ${currentPage}/${totalPages})`;
    }

    function goTo(page) {
        currentPage = page;
        render();
    }
    if (itemsPerPageElement) {
      itemsPerPageElement.addEventListener('change', e => {
        itemsPerPage = parseInt(e.target.value, 10);
        currentPage  = 1;
        render();
      });
    }

    render();
    return {
        setData(newData) {
            fullData    = newData;
            currentPage = 1;
            render();
        }
    };
}
function updateSortPriority(columnIndex, sortPriority) {
    const existingPriority = sortPriority.findIndex(sp => sp.columnIndex === columnIndex);
    if (existingPriority === -1) {
        // Add new sort priority if not already present
        sortPriority.push({ columnIndex: columnIndex, direction: 'asc' });
    } else {
        // If clicked again, update direction or remove if it's the third click
        if (sortPriority[existingPriority].direction === 'asc') {
            sortPriority[existingPriority].direction = 'desc';
        } else {
            sortPriority.splice(existingPriority, 1); // Remove this sort priority
        }
    }
}

function adjustSortIcon(columnIndex, realIndex, sortPriority) {
    const arrows = document.querySelectorAll('.sort-arrow');
    const currentArrow = arrows[realIndex];
    const existingPriority = sortPriority.find(sp => sp.columnIndex === columnIndex);
    const direction = existingPriority ? existingPriority.direction : null;
    // Set current arrow based on direction
    if (direction === 'asc') {
        currentArrow.classList.remove('fa-arrow-up','fa-x' );
        currentArrow.classList.add( "fa-arrow-down"); //= '↓'; // Down arrow indicates ascending sort

    } else if (direction === 'desc') {
        currentArrow.classList.remove('fa-arrow-down','fa-x' );
        currentArrow.classList.add("fa-arrow-up");// = '↑'; // Up arrow indicates descending sort
    } else {
        currentArrow.classList.remove('fa-arrow-down', 'fa-arrow-up','fa-x' );
        currentArrow.classList.add("fa-x");
    }
}
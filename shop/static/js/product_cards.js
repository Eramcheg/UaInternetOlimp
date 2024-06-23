function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function updatePlatings(selectedPlating, stoneSelect, sizeSelect, image, maxQuantity, show_quantities, vocabulary){
    const firstStone = selectedPlating ? Object.values(selectedPlating.stones || {})[0] : null;

    while (stoneSelect.firstChild) {
        stoneSelect.removeChild(stoneSelect.firstChild);
    }
    fulfilDropdown(stoneSelect, selectedPlating.stones, vocabulary);
    return updateStones(firstStone, sizeSelect, image, maxQuantity, show_quantities, vocabulary);
}
function updateStones(selectedStone, sizeSelect, image, maxQuantity, show_quantities, vocabulary){

    const firstSizeKey = selectedStone ? Object.keys(selectedStone.sizes || {})[0] : null;
    const withSizes = !!firstSizeKey;
    const firstSizeQuantity = withSizes ? selectedStone.sizes[firstSizeKey].quantity : selectedStone.quantity;
    if (selectedStone?.image) {
        image.src = selectedStone.image; // Update the image src
    }

    while (sizeSelect.firstChild) {
        sizeSelect.removeChild(sizeSelect.firstChild);
    }
    if(withSizes) {
        fulfilDropdown(sizeSelect, selectedStone.sizes, vocabulary);
        return updateSizes(firstSizeQuantity, maxQuantity, show_quantities, vocabulary);
    }
    else{
        console.log(firstSizeQuantity);
         if(show_quantities) {
            maxQuantity.innerText = `${vocabulary['In stock']}: `+firstSizeQuantity;
        }
        else{
            if (firstSizeQuantity<=5){
                maxQuantity.innerText = `${vocabulary['Less than 5 pieces left!']}`
            }
            else{
                maxQuantity.innerText = ``
            }
        }
    }
}
function updateSizes(sizeQuantity, maxQuantity, show_quantities, vocabulary){
     if(show_quantities) {
        maxQuantity.innerText = `${vocabulary['In stock']}: `+sizeQuantity;
    }
    else{
        if (sizeQuantity<=5){
            maxQuantity.innerText = `${vocabulary['Less than 5 pieces left!']}`;
        }
        else{
            maxQuantity.innerText = ``
        }
    }
    return Number(sizeQuantity);
}

function fulfilDropdown(dropdown, array, vocabulary){
    if(array) {
        (Object.keys(array)).forEach(element => {
            let option = document.createElement('option');
            option.innerText = vocabulary[element] ? vocabulary[element]: element;
            option.value = element;
            dropdown.add(option);
        });
    }
}

 function closeDialogWithAnimation(dialog) {
    dialog.style.transform = 'translate(0%, 0%) scale(0)';
        setTimeout(() => {
            dialog.style.display = 'none';
        dialog.close();
    }, 250); // 500 milliseconds is the duration of the animation
 }

 function bindGlobalClickEvent(dialog) {
    document.addEventListener('click', (event) => {
        const rect = dialog.getBoundingClientRect();
        const isInDialog = (rect.top <= event.clientY && event.clientY <= rect.top + rect.height
                            && rect.left <= event.clientX && event.clientX <= rect.left + rect.width);

        // Check if the event target is inside a select element or another form control
        let targetElement = event.target;
        while (targetElement != null) {
            if (targetElement.tagName === 'SELECT' || targetElement.tagName === 'OPTION') {
                // If the click is inside the dialog or on a select element, do nothing
                return;
            }
            targetElement = targetElement.parentNode; // Move up the DOM tree
        }

        if (!isInDialog && dialog.open) {
            document.body.style.overflow = '';

            closeDialogWithAnimation(dialog);
        }
    }, true);
}

function dialogCommonSetup(dialog, image_url, card_content, image){

    image.src = image_url;
    image.width = `400`;
    image.height = `400`;
    image.classList.add('img-card');
    card_content.appendChild(image);

    const close_dialog = document.createElement('div');
    const icon_close = document.createElement('i');
    icon_close.classList.add('fa-solid', 'fa-close');
    close_dialog.appendChild(icon_close);
    close_dialog.addEventListener('click',()=>{
       document.body.style.overflow = '';
       closeDialogWithAnimation(dialog);
    });

    close_dialog.classList.add('close-card');
    card_content.appendChild(close_dialog);

}

function showTooltip(event, message) {
    const existingTooltip = document.querySelector('.custom-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = message;
    tooltip.style.position = 'absolute';
    tooltip.style.left = `${event.pageX + 10}px`; // Adjust positioning as needed
    tooltip.style.top = `${event.pageY + 10}px`; // Adjust positioning as needed
    document.body.appendChild(tooltip);

    // Move tooltip with cursor
    event.target.addEventListener('mousemove', (e) => {
        tooltip.style.left = `${e.pageX + 10}px`;
        tooltip.style.top = `${e.pageY + 10}px`;
    });

    // Remove tooltip on mouseleave
    event.target.addEventListener('mouseleave', () => {
        tooltip.remove();
    });
}


function generateDialogContent(id, items_array, currency, show_quantities, add_to_cart_url, vocabulary, cookie, checkout_url){
    let quantity_max = 1;
    document.body.style.overflow = 'hidden';
    const item = items_array.find(item => item.name === id);
    console.log(item);
    if (!item) {
        console.error('Item not found');
        return;
    }

    const firstPlatingKey = Object.keys(item.platings)[0];
    const firstPlating = item.platings[firstPlatingKey];

    // Get the first stone in the first plating
    const firstStoneKey = firstPlating && Object.keys(firstPlating.stones)[0];
    const firstStone = firstPlating ? firstPlating.stones[firstStoneKey] : null;

    // Get the first size in the first stone
    const firstSizeKey = firstStone && Object.keys(firstStone.sizes)[0];
    const firstSizeQuantity = firstStone ? firstStone.sizes[firstSizeKey] ? firstStone.sizes[firstSizeKey].quantity: null : null;


    const dialog = document.getElementById('product-card');
    const image = document.createElement('img');
    bindGlobalClickEvent(dialog);
    dialog.innerHTML = '';

    const card_content = document.createElement('div');
    card_content.classList.add('card-content');

    let imagePath = '';

    if (firstStone) {
        imagePath = firstStone.image || '';
        quantity_max = Object.keys(firstStone.sizes || {}).length === 0 ? firstStone.quantity : firstSizeQuantity;
    }

    dialogCommonSetup(dialog, imagePath, card_content, image);

    const secondColumn = document.createElement('div');
    secondColumn.classList.add('second-column');

    let parts = item.product_name.split(" ");
    // Remove the last word
    let last_word = parts.pop();
    // Join the remaining parts to form the full phrase
    let full_phrase = parts.join(" ");
    const nameSpan = document.createElement('h2');
    nameSpan.textContent = vocabulary[full_phrase] ? vocabulary[full_phrase] + " " + last_word : item.product_name;
    secondColumn.appendChild(nameSpan);

    const numberSpan = document.createElement('h4');
    numberSpan.textContent = `${item.name}`;
    secondColumn.appendChild(numberSpan);

    const priceSpan = document.createElement('div');
    priceSpan.textContent = currency+`${item.price}`;
    secondColumn.appendChild(priceSpan);

    const quantitySpan = document.createElement('div');
    if(show_quantities) {
        quantitySpan.textContent = `${vocabulary['In stock']}: ${quantity_max}`;
    }
    else{
        if (quantity_max<=5){
            quantitySpan.textContent = `${vocabulary['Less than 5 pieces left!']}`;
        }
    }
    quantitySpan.classList.add('maximum-span');

    const platingLabel = document.createElement('span');
    platingLabel.innerText = `${vocabulary['Plating Material']}`;
    platingLabel.classList.add('card-dropdown-label');
    const platingsSelect = document.createElement('select');
    platingsSelect.classList.add('card-dropdown');
    fulfilDropdown(platingsSelect, item.platings, vocabulary);
    secondColumn.appendChild(platingLabel);
    secondColumn.appendChild(platingsSelect);

    const stoneLabel = document.createElement('span');
    stoneLabel.innerText = `${vocabulary['Stone color']}`;
    stoneLabel.classList.add('card-dropdown-label');
    const stoneSelect = document.createElement('select');
    stoneSelect.classList.add('card-dropdown');
    fulfilDropdown(stoneSelect, firstPlating.stones, vocabulary);
    secondColumn.appendChild(stoneLabel);
    secondColumn.appendChild(stoneSelect);

    const sizeLabel = document.createElement('span');
    sizeLabel.innerText = `${vocabulary['Size']}`;
    sizeLabel.classList.add('card-dropdown-label');
    const sizeSelect = document.createElement('select');
    sizeSelect.classList.add('card-dropdown');
    if(Object.keys(firstStone.sizes).length>0) {
        fulfilDropdown(sizeSelect, firstStone.sizes, vocabulary);
        secondColumn.appendChild(sizeLabel);
        secondColumn.appendChild(sizeSelect);
    }
    const inputQuantity = document.createElement('input');

    platingsSelect.addEventListener('change', (event) => {
        const selectedPlatingKey = event.target.value;
        const selectedPlating = item.platings[selectedPlatingKey];
        inputQuantity.value = '1';
        quantity_max = updatePlatings(selectedPlating, stoneSelect, sizeSelect, image, quantitySpan, show_quantities, vocabulary);
    });

    stoneSelect.addEventListener('change', (event) => {
        const selectedStoneKey = event.target.value;
        const selectedPlatingKey = platingsSelect.value;
        const selectedPlating = item.platings[selectedPlatingKey];
        const selectedStone = selectedPlating && selectedPlating.stones ? selectedPlating.stones[selectedStoneKey] : null;
        inputQuantity.value = '1';
        quantity_max = updateStones(selectedStone, sizeSelect, image, quantitySpan, show_quantities,vocabulary);

    });

    sizeSelect.addEventListener('change', (event) => {
        const selectedSizeKey = event.target.value;
        const selectedPlatingKey = platingsSelect.value;
        const selectedPlating = item.platings[selectedPlatingKey];
        const selectedStoneKey = stoneSelect.value;
        const selectedSizeQuantity = selectedPlating.stones[selectedStoneKey].sizes[selectedSizeKey].quantity;
        inputQuantity.value = '1';
        quantity_max = updateSizes(selectedSizeQuantity, quantitySpan, show_quantities, vocabulary);

    });

    const bottom_part = document.createElement('div');
    bottom_part.classList.add('bottom-card-part');

    const counter = document.createElement('div');

    const button_minus = document.createElement('button');
    button_minus.innerText = '-';
    button_minus.classList.add('minus-button-dialog');

    inputQuantity.type = 'number';
    inputQuantity.style.textAlign = 'center';
    inputQuantity.value = 1;
    inputQuantity.classList.add('quantity-input-dialog');
    inputQuantity.min = '1';

    inputQuantity.addEventListener('input', function() {
        if(inputQuantity.value > quantity_max || inputQuantity.value < 1 ){
            if(inputQuantity.value > quantity_max){
                inputQuantity.value = quantity_max;
            }
            else{
                inputQuantity.value = 1;
            }
            alert(`${vocabulary['Quantity number has to be less than or equal to quantity number in stock or and be greater than 0']}`);
        }
    });

    button_minus.addEventListener('click', () => {
        if(inputQuantity.value > 1)
            inputQuantity.value -= 1;
    });
    const button_plus = document.createElement('button');
    button_plus.innerText = '+';
    button_plus.classList.add('plus-button-dialog');
    button_plus.addEventListener('click', () => {

        if(inputQuantity.value<quantity_max) {
            let currentValue = Number(inputQuantity.value === "" ? 1 : inputQuantity.value);
            inputQuantity.value = currentValue + 1;
        }
    });
    counter.appendChild(button_minus);
    counter.appendChild(inputQuantity);
    counter.appendChild(button_plus);



    const add_to_cart = document.createElement('button');
    add_to_cart.type = 'submit';
    add_to_cart.classList.add('add-to-cart-dialog');
    add_to_cart.addEventListener('click', function() {
        add_to_cart_func(item, platingsSelect.value, stoneSelect.value, sizeSelect.value, Number(inputQuantity.value), add_to_cart, dialog, currency, add_to_cart_url, vocabulary, cookie, checkout_url);
    });
    const icon_cart = document.createElement('i');
    icon_cart.classList.add('fa-solid', 'fa-cart-shopping');
    add_to_cart.appendChild(icon_cart);
    const text_add_to_cart = document.createElement('span');
    text_add_to_cart.innerText = `${vocabulary['Add to cart']}`;
    add_to_cart.appendChild(icon_cart);
    add_to_cart.appendChild(text_add_to_cart);
    bottom_part.appendChild(counter);
    bottom_part.appendChild(quantitySpan);
    bottom_part.appendChild(add_to_cart);
    secondColumn.appendChild(bottom_part);

    card_content.appendChild(secondColumn);
    dialog.appendChild(card_content);
    dialog.style.transform = 'translate(0%, 0%) scale(0)';

    dialog.showModal();
    setTimeout(() => {
    dialog.style.transform = 'translate(0%, 0%) scale(1)';
  }, 0); // 0 milliseconds delay is often enough to ensure the reapplication triggers the animation

    dialog.style.display = 'block';
}

function add_to_cart_func(item, plating, stone, size, quantity, add_button, dialog, currency, add_to_cart_url, vocabulary, cookie, checkout_url){
    let doc;
    if( size === "" ){
         doc = item.platings[plating].stones[stone].real_name;
    }
    else{
         doc = item.platings[plating].stones[stone].sizes[size].real_name;
    }
    add_button.textContent = `${vocabulary['Processing']}...`;
    add_button.style.backgroundColor = "#7894a6";
    add_button.disabled = true;

    fetch(add_to_cart_url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': cookie,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'document': doc, 'quantity': quantity})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {

            closeDialogWithAnimation(dialog);
            setTimeout(() => {
                activate_success_card(data.product, data.quantity, data.cart_size, data.subtotal, currency, vocabulary, checkout_url);
            }, 0);

        } else {
            alert(`${vocabulary['An error occured']}: ` + data.error);
            closeDialogWithAnimation(dialog);
        }
    });
}

function activate_success_card(item, quantity, cart_count, subtotalValue, currency, vocabulary, checkout_url){
    const dialog = document.getElementById('product-card-success');

    bindGlobalClickEvent(dialog);
    dialog.innerHTML = '';
    const card_content = document.createElement('div');
    card_content.classList.add('success-card-content');
    const image = document.createElement('img');
    dialogCommonSetup(dialog, item.image_url, card_content, image);

    //Column with text information and everything about added to cart product
    const secondColumn = document.createElement('div');
    secondColumn.classList.add('second-column');

    //Add information about added the product and about the cart
    informationSuccessSetup(secondColumn, item, quantity, cart_count, subtotalValue, currency, vocabulary);

    //Add buttons to continue shopping or to procceed to checkout
    manageButtonsSuccessSetup(dialog, secondColumn, vocabulary, checkout_url);

    card_content.appendChild(secondColumn);
    dialog.appendChild(card_content);

    setTimeout(() => {
        dialog.showModal();
        dialog.style.transform = 'translate(0%, 0%) scale(1)';
    }, 249); // 0 milliseconds delay is often enough to ensure the reapplication triggers the animation
    dialog.style.display = 'block';

}

function informationSuccessSetup(column, item, actual_quantity, cart_count, cartSubtotal, currency, vocabulary){
    const addedText = document.createElement('h4');
    addedText.classList.add('added-text');
    addedText.innerHTML = `<i class='fa-solid fa-check'></i> `+`${vocabulary['Product successfully added to your shopping cart']}`;
    column.appendChild(addedText);
    const nameSpan = document.createElement('h3');
    nameSpan.textContent = `${vocabulary[item.category]} ${item.product_name}`;
    column.appendChild(nameSpan);

    const numberSpan = document.createElement('h4');
    numberSpan.textContent = `${item.name}`;
    column.appendChild(numberSpan);

    const priceSpan = document.createElement('div');
    priceSpan.textContent = currency + `${item.price.toFixed(2)}`;
    column.appendChild(priceSpan);

    const platingSpan = document.createElement('spanSucc');
    platingSpan.innerHTML= `<strong>${vocabulary['Plating Material']}: </strong>` + `${vocabulary[item.plating]?vocabulary[item.plating]:item.plating}`;
    column.appendChild(platingSpan);
    const crystalSpan = document.createElement('spanSucc');
    crystalSpan.innerHTML = `<strong>${vocabulary['Crystal color']}: </strong> ` +`${vocabulary[item.stone]?vocabulary[item.stone]:item.stone}`;
    column.appendChild(crystalSpan);
    const baseSpan = document.createElement('spanSucc');
    baseSpan.innerHTML =`<strong>${vocabulary['Base material']}: </strong> ` + `${vocabulary[item.material]?vocabulary[item.material]:item.material}`;
    column.appendChild(baseSpan);

    const quantitySpan = document.createElement('spanSucc');
    quantitySpan.innerHTML = `<strong>${vocabulary['Quantity']}: </strong> ` + `${actual_quantity}`;
    quantitySpan.style.marginBottom = '20px';
    column.appendChild(quantitySpan);

    const items_count = document.createElement('spanSucc');
    items_count.textContent = `${vocabulary['Number of items in your cart']}: ${cart_count}`;
    column.appendChild(items_count);

    const subtotal = document.createElement('spanSucc');
    subtotal.innerHTML =`<strong>${vocabulary['Subtotal']}: </strong>`+ currency + `${cartSubtotal}`;
    subtotal.style.marginBottom = '20px';
    column.appendChild(subtotal);
}

function manageButtonsSuccessSetup(dialog, column, vocabulary, checkout_url){
    const container_for_success_buttons = document.createElement('div');
    const continue_shopping = document.createElement('button');
    continue_shopping.classList.add('button-continue-shopping');
    continue_shopping.textContent = `${vocabulary['Continue shopping']}`;
    container_for_success_buttons.appendChild(continue_shopping);

    continue_shopping.addEventListener('click', ()=>{
         document.body.style.overflow = '';
        closeDialogWithAnimation(dialog);
    });

    const proceed_to_checkout = document.createElement('a');
    proceed_to_checkout.textContent = `${vocabulary['Proceed to checkout']}`;
    proceed_to_checkout.classList.add('button-proceed-to-checkout');
    console.log(checkout_url);
    proceed_to_checkout.href = `${checkout_url}`;

    container_for_success_buttons.appendChild(proceed_to_checkout);
    column.appendChild(container_for_success_buttons);
}

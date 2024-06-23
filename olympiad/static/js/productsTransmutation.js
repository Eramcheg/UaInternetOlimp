function productsTransmutation(items, price_category, sale){

    let products = {};
    const regex = /^[a-zA-Z]{0,2}\d{5}[a-zA-Z]{0,5}$/;
    items.forEach(item => {
        if(item.Visible === false){
            return;
        }
        let itemName = item.name;

        itemName = itemName.split(' ')[0];
         if (regex.test(itemName)) {
            let processedName = itemName.match(/^([a-zA-Z]{0,2})(\d{5})/);
             // This includes both the initial letters and the 5 digits
             itemName = processedName[0];
        } else {
            itemName = (item.name).split(' ')[0];
        }

        if (!products[itemName] ) { //&& item.plating && item.stone
                products[itemName] = {
                    name: itemName,
                    product_name: item.category + " "+ item.product_name,
                    description: item.description,
                    price:calculatePrice(item, price_category, sale),
                    category: item.category,
                    material: item.material,
                    preview_image: item.image_url,
                    platings: {}
                };
            }
            if (item.plating) {
                // Initialize plating if it doesn't exist.
                if (!products[itemName].platings[item.plating]) {
                    products[itemName].platings[item.plating] = {
                        stones: {},
                    };
                }

                // Proceed only if stone is defined.
                if (item.stone) {
                    // Initialize the stone if it doesn't exist under the current plating.
                    if (!products[itemName].platings[item.plating].stones[item.stone]) {
                        products[itemName].platings[item.plating].stones[item.stone] = {
                            sizes: {},
                            image: item.image_url,
                            real_name: item.name

                        };
                    }

                    // If size is present, add or update the size and quantity for the stone.
                    if (item.size) {
                        let stoneSizes = products[itemName].platings[item.plating].stones[item.stone].sizes;
                        if (!stoneSizes[item.size]) {
                            stoneSizes[item.size] = {'quantity': item.quantity, 'real_name':item.name };

                        } else {
                            // Assuming you want to sum quantities for the same size.
                            stoneSizes[item.size].quantity += item.quantity;
                        }
                    } else {
                        // If there's no size, add the quantity directly to the stone.
                        if (!products[itemName].platings[item.plating].stones[item.stone].quantity) {
                            products[itemName].platings[item.plating].stones[item.stone].quantity = item.quantity;
                            products[itemName].platings[item.plating].stones[item.stone].real_name = item.name;
                        } else {
                            products[itemName].platings[item.plating].stones[item.stone].quantity += item.quantity;
                        }
                    }
                }
            }
    });
    for (let productName in products) {
        for (let platingName in products[productName].platings) {
            for (let stoneName in products[productName].platings[platingName].stones) {
                let stoneEntry = products[productName].platings[platingName].stones[stoneName];
                if (stoneEntry.sizes) {
                    stoneEntry.sizes = orderSizes(stoneEntry.sizes);
                }
            }
        }
    }
    return Object.values(products);
}

function orderSizes(sizes) {
    const sizeOrder = ['S', 'M', 'L', 'XL'];
    const orderedSizes = {};
    sizeOrder.forEach(size => {
        if (sizes.hasOwnProperty(size)) {
            orderedSizes[size] = sizes[size];
        }
    });
    // Include other sizes not in the specified order
    Object.keys(sizes).forEach(size => {
        if (!orderedSizes.hasOwnProperty(size)) {
            orderedSizes[size] = sizes[size];
        }
    });
    return orderedSizes;
}

function calculatePrice(item, price_category, sale) {
    return (Number(((price_category === "VK3" ? item.priceVK3 :
             price_category === "GH" ? item.priceGH :
             price_category === "GH_USD" ? item.priceUSD_GH :
             price_category === "Default_USD" ? (item.priceUSD * (1 - sale)) :
             (item.priceVK4 * (1 - sale)))).toFixed(1))).toFixed(2);
}
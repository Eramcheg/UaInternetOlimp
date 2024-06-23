function calculate_final(vat, currency){
     let totalQuantity = 0;
     let totalSum = 0;
     let totalItems = 0;

     documentss.forEach(doc => {
            totalItems+=1;
            totalQuantity += doc.quantity;
            totalSum += (doc.quantity * doc.price);
     });

     const quantity_items = totalItems%10===1 ? "item" : "items";
     const totalSumFinal =  totalSum;
     const included_vat = (totalSumFinal * vat/100);
     const sum_with_vat = (included_vat + totalSumFinal);
     document.querySelector('.final-unique-quantity').innerText =  totalItems +" " + quantity_items;
     document.getElementById('final-sum').innerText = currency + totalSumFinal.toFixed(2);
     document.querySelector('.value-total').innerText = currency + sum_with_vat.toFixed(2);
     document.querySelector('.value-taxes').innerText = currency + included_vat.toFixed(2);
}
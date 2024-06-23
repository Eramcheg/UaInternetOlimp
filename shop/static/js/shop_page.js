//
// document.addEventListener('DOMContentLoaded', function() {
//             restoreState();
// });
//  function restoreState() {
//      document.querySelectorAll('.radio-buttons').forEach(group => {
//         let radios = group.querySelectorAll('input[type="radio"]');
//
//         if (radios.length > 0) {
//             radios[0].checked = true;
//         }
//     });
//     const Id =  document.querySelector('.number-in-cart').getAttribute('data-product-id');
//     document.querySelector('.number-in-cart').innerText = localStorage.getItem('number-'+Id);
//
//     const sum = document.getElementById('sum-'+Id);
//     if (localStorage.getItem('sum-'+Id)!==null && inside !== "False")
//         sum.innerText = "Total: " + localStorage.getItem('sum-'+Id);
//     else {
//         sum.innerText = "Total: €0";
//
//     }
//     if (localStorage.getItem('quantity-'+Id)!==null && inside !== "False" )
//         changeCurrentQuantityText(Id, localStorage.getItem('quantity-'+Id));
//     else {
//         changeCurrentQuantityText(Id, 0);
//     }
//
//  }
// document.getElementById('cart-icon').addEventListener('click', function() {
//           const miniCartElement = document.getElementById('mini-cart');
//           const arrowIcon = document.getElementById('arrow-icon');
//           const isDisplayed = miniCartElement.style.display !== 'none';
//
//           // Toggle display property of the mini-cart
//           miniCartElement.style.display = isDisplayed ? 'none' : 'block';
//
//           // Toggle the arrow icon class
//           if (isDisplayed) {
//               document.getElementById('show-cart').innerText = "Show my cart";
//             arrowIcon.classList.remove('fa-arrow-down');
//             arrowIcon.classList.add('fa-arrow-right');
//           } else {
//               document.getElementById('show-cart').innerText = "Hide my cart";
//             arrowIcon.classList.remove('fa-arrow-right');
//             arrowIcon.classList.add('fa-arrow-down');
//           }
//
//           // If we're showing the cart, update its content
//           if (!isDisplayed) {
//             updateMiniCart();
//           }
//     });
//     function updateMiniCart() {
//
//       const miniCartElement = document.getElementById('mini-cart');
//       miniCartElement.innerHTML = ''; // Clear current mini-cart content
//
//       let total = 0;
//
//       cartData.forEach(item => {
//         const itemElement = document.createElement('div');
//         itemElement.classList.add('mini-cart-item');
//
//         itemElement.innerHTML = `
//             <div style="display: flex;flex-direction: column; align-items: center;">
//               <p style=""> ${item.name}</p>
//               <div style="display: flex; justify-content: space-between; width: 100%;">
//                 <span>Price: €${item.price.toFixed(2)}</span>
//                 <span>Quantity: ${item.quantity}</span>
//                 <span>Sum: €${(item.sum)}</span>
//               </div>
//             </div>
//         `;
//
//
//         miniCartElement.appendChild(itemElement);
//       });
//     }
//
//
//     document.getElementById('searchForm').addEventListener('submit', function() {
//         // localStorage.clear();
//     });
//     function updateDropdown() {
//         var inputVal = document.getElementById('number').value;
//         if (inputVal.length === 0) {
//             document.getElementById('dropdown').innerHTML = '';
//             return;
//         }
//         fetch('/fetch-numbers/?term=' + inputVal)
//             .then(response => response.json())
//             .then(data => {
//                 let dropdownHTML = '';
//                 data.forEach((item) => {
//                     dropdownHTML += `<div onclick="fillInput('${item}')">${item}</div> <hr style="margin: 0 10px; ">`;
//                 });
//                 document.getElementById('dropdown').innerHTML = dropdownHTML;
//             });
//     }
//
//     function fillInput(value) {
//         document.getElementById('number').value = value;
//         document.getElementById('dropdown').innerHTML = '';
//     }
//
//     document.querySelectorAll('.purchase').forEach(button => {
//         button.addEventListener('click', function() {
//             const productId = this.getAttribute('data-product-id');
//             const documentContainer = this.closest('.document-container');
//             const documentValue = documentContainer.getAttribute('data-document');
//             fetch('{% url "add_to_cart" %}', {
//                 method: 'POST',
//                 headers: {
//                     'X-CSRFToken': getCookie('csrftoken'),
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ document: documentValue })
//             }).then(response => response.json())
//               .then(data => {
//                   if (data.status === 'success') {
//                       document.getElementById('quantity-' + productId).innerText = data.quantity;
//
//                       togglePurchaseButton(productId);
//                       saveState('quantity-'+productId, 1);
//                       saveState("number-"+productId, data.number);
//                       saveState("sum-"+productId, "€"+data.sum);
//                       restoreState();
//
//
//                   }
//               });
//         });
//     });
//
//     function togglePurchaseButton(productId) {
//     const deleteButton = document.querySelector('.deleteBut[data-product-id="' + productId + '"]');
//     const number = document.querySelector('.number-in-cart');
//     const quantityInput = document.getElementById('quantity-input-' + productId);
//     const sum = document.getElementById('sum-'+productId);
// const current_quantity = document.getElementById('current-quantity-'+productId);
// current_quantity.style.display = 'inline';
//     number.style.display = 'flex';
//     quantityInput.style.display = 'block';
//     deleteButton.style.display = 'inline';
//     sum.style.display = 'block';
//
// }
//
//
// document.querySelectorAll('.deleteBut').forEach(button => {
//     button.addEventListener('click', function() {
//         const documentId = this.getAttribute('data-product-id');
//
//         const confirmed = confirm("Do you really want to delete this product from your cart?");
//
//         if (confirmed) {
//             fetch('{% url "delete_document" %}', {  // Replace with your actual URL
//                 method: 'POST',
//                 headers: {
//                     'X-CSRFToken': getCookie('csrftoken'),
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({ document_id: documentId })
//             })
//             .then(response => {
//                 if(response.ok) {
//
//
//                     inside = "False";
//                     saveState();
//                     toggleQuantityForm(documentId);
//                 } else {
//                     console.error('Error in deletion');
//                 }
//             })
//             .catch(error => console.error('Error:', error));
//         }
//     });
// });
//  function toggleQuantityForm(productId) {
//     const delBut = document.querySelector('.deleteBut[data-product-id="' + productId + '"]');
//     const number = document.querySelector('.number-in-cart');
//     const total = document.getElementById('sum-'+productId);
//     delBut.style.display = 'none';
//     number.style.display = 'none';
//     total.style.display = 'none';
//     let input = document.getElementById('quantity-input-inp-'+productId);
//     input.value = "";
//     let slider = document.getElementById('slider-'+productId);
//     slider.value = 1;
//     changeCurrentQuantityText(productId,0);
//     const button = document.getElementById("quantity-input-apply-"+ productId);
//     button.innerText = "Confirm";
//     button.style.background = "#1daede"
// }
//
// document.querySelectorAll('.radio-buttons input[type="radio"]').forEach(radio => {
//     radio.addEventListener('change', function() {
//         const documentContainer = this.closest('.document-container');
//         const documentString = documentContainer.getAttribute('data-document');
//         const doc = documentString.replace(/'/g, '"');
//
//         const dataObject = JSON.parse(doc);
//
//         const docName = dataObject.name;
//
//         const quantityControl = document.getElementById('quantity-control-' + docName);
//         const quantitySlider = document.getElementById('quantity-slider-' + docName);
//         const quantityInput = document.getElementById('quantity-input-' + docName);
//         if (this.value === 'quantityControl') {
//             const quantityElementControl = document.getElementById('quantity-' + docName);
//             quantityElementControl.innerText = localStorage.getItem('quantity-'+docName);
//             quantityControl.style.display = 'block';
//             quantitySlider.style.display = 'none';
//             quantityInput.style.display = 'none';
//         } else if (this.value === 'quantitySlider') {
//             const quantityElement = document.getElementById('quantity-slider-text-' + docName);
//             const slider = document.getElementById('slider-'+docName);
//             quantityElement.innerText = localStorage.getItem('quantity-'+docName);
//             slider.value = localStorage.getItem('quantity-'+docName);
//             quantitySlider.style.display = 'flex';
//             quantityControl.style.display = 'none';
//             quantityInput.style.display = 'none';
//         }else if (this.value === 'quantityInput') {
//             quantitySlider.style.display = 'none';
//             quantityControl.style.display = 'none';
//             quantityInput.style.display = 'block';
//             const inp = document.getElementById('quantity-input-inp-' + docName);
//             inp.value = '';
//         }
//     });
// });
//  function saveState(name, value) {
//     localStorage.setItem(name, value);
// }
//
//  $(document).ready(function(){
//     $('.slider').on('input change', function() {
//         let product_id = $(this).attr('id').split('-')[1];
//         let quantity_new = $(this).val();
//         const quantityElement = document.getElementById('quantity-input-inp-' + product_id);
//         quantityElement.value = quantity_new;
//
//         const button = document.getElementById("quantity-input-apply-"+ product_id);
//             button.innerText = "Confirm";
//             button.style.background = "#1daede"
//     });
// });
//
// document.querySelectorAll('.quantity-input-button').forEach(button => {
//     button.addEventListener('click', function() {
//         const documentContainer = this.closest('.document-container');
//
//         const documentValue = JSON.parse(documentContainer.getAttribute('data-document').replace(/'/g, '"'));
//
//         const productId = documentValue['name'];
//
//         const inp = document.getElementById('quantity-input-inp-' + productId);
//
//         const quantity = parseInt(inp.value);
//
//
//         if (isNaN(quantity) || quantity <= 0) {
//             alert("Type of written quantity has to be numeric and greater than 0");
//         }
//         else if (quantity > documentValue.quantity) {
//
//             alert("Quantity has to be less than maximum on storage");
//         }
//         else {
//             updateQuantityInput(productId, quantity, documentValue);
//         }
//     });
// });
//
//     function updateQuantityInput(product_id, quantity_new, doc) {
//         fetch('{% url "update_input" %}', {
//             method: 'POST',
//             headers: {
//                 'X-CSRFToken': getCookie('csrftoken'),
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ product_id: product_id, quantity_new: quantity_new, 'document': JSON.stringify(doc), price:doc.price})
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 changeCurrentQuantityText(product_id, quantity_new);
//
//
//                 const button = document.getElementById("quantity-input-apply-"+ product_id);
//                 button.innerText = "Confirmed!";
//                 button.style.background = "#06b206";
//
//                 const sum  = document.getElementById('sum-'+data.product_id);
//                 sum.innerText = "Total: " + data.sum;
//                  saveState('sum-'+product_id, data.sum);
//
//                 saveState('quantity-'+data.product_id, data.quantity);
//                 if(data.was_inside === 'False'){
//                     inside = "True";
//                     saveState('number-'+product_id, data.number);
//                     togglePurchaseButton(product_id);
//                     restoreState();
//                 }
//
//
//             } else {
//             }
//     });
//
//     }
//     document.querySelectorAll('.quantity-input input[type="number"]').forEach(input => {
//     input.addEventListener('input', function() {
//
//         const documentContainer = this.closest('.document-container');
//         const documentValue = JSON.parse(documentContainer.getAttribute('data-document').replace(/'/g, '"'));
//         const productId = documentValue['name'];
//         const slider = document.getElementById('slider-'+productId);
//         slider.value =  input.value;
//         const button = document.getElementById("quantity-input-apply-"+ productId);
//             button.innerText = "Confirm";
//             button.style.background = "#1daede"
//     });
// });
//     function getCookie(name) {
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }
// let csrftoken = getCookie('csrftoken');
//
// function changeCurrentQuantityText(productId, quantity){
//     const current_quantity = document.getElementById('current-quantity-'+productId);
//     current_quantity.innerText = "Current quantity: "+ quantity;
// }
// $.ajaxSetup({
//     beforeSend: function(xhr, settings) {
//         if (!this.crossDomain) {
//             xhr.setRequestHeader("X-CSRFToken", csrftoken);
//         }
//     }
// });
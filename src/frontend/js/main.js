let registerBtn = document.querySelector("#registerBtn");
let loginBtn = document.querySelector("#loginBtn");
let logo = document.querySelector("#logo");
let interfaceBtn = document.querySelector("#interfaceBtn");
let interfaceCont = document.querySelector("#interfaceMainContainer");
let receptionCont = document.querySelector("#receptionMainContainer");


function Swap(hidde,appear) {
    hidde.classList.toggle("hidden") 
    appear.classList.toggle("hidden") 
}

loginBtn.addEventListener("click",()=> {
Swap(receptionCont,interfaceCont);
});
interfaceBtn.addEventListener("click",()=> {
Swap(interfaceCont,receptionCont);
});
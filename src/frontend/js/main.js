const testCont=document.querySelector("#congrats")
const registerBtn = document.querySelector("#registerBtn");
const loginBtn = document.querySelector("#loginBtn");
const logo = document.querySelector("#logo");
const interfaceBtn = document.querySelector("#interfaceContinue");
const interfaceCont = document.querySelector("#interfaceMainContainer");
const receptionCont = document.querySelector("#receptionMainContainer");
const interfaceGoBack = document.querySelector("#interfaceBack");
const interfaceInputs = document.querySelector("#interfaceInputs");
const interfaceText = document.querySelector("#interfaceText");
const loginInputUser= document.querySelector("#loginUserInput");
const loginInputPassword=document.querySelector("#loginPasswordInput");

let currentDisplay=receptionCont;
let userLoginData= {
    username:"Diego",
    password:"1234"
}
let userLoginInput={
    username:"",
    password:""
}
function interfaceMode(mode) {
  interfaceText.textContent=mode;
  interfaceBtn.textContent=mode;  
    
}
function navigateTo(newDisplay) {
    currentDisplay.classList.add("hidden") 
    newDisplay.classList.remove("hidden") 
    
    currentDisplay=newDisplay;
}
function loginCheck(userInput) {
   if(userInput.username===userLoginData.username && userInput.password===userLoginData.password){
   navigateTo(testCont)
   }
   
    
}

loginBtn.addEventListener("click",()=> {

interfaceMode("Login")    
navigateTo(interfaceCont);
});
registerBtn.addEventListener("click",()=> {
interfaceMode("Register")      
navigateTo(interfaceCont);
});
interfaceGoBack.addEventListener("click",()=> {
navigateTo(receptionCont);
});
interfaceBtn.addEventListener("click",()=> {
   userLoginInput.username=loginInputUser.value;
   userLoginInput.password=loginInputPassword.value;
loginCheck(userLoginInput);
});
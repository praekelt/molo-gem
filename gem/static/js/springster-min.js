"use strict";var domReady=function(e){"interactive"===document.readyState||"complete"===document.readyState?e():document.addEventListener("DOMContentLoaded",e)},stickyHeader=function(){var e=document.getElementById("header"),t=document.getElementById("content-wrapper"),n=document.getElementById("header").clientHeight,o=document.getElementById("language-bar").clientHeight;window.addEventListener("scroll",function(){var r=this.y-window.pageYOffset,i=window.scrollY;r>0&&i>o?(e.style.top=0,t.style.top=n+"px",e.classList.add("header-fixed")):i>n+o?e.style.top=-n+"px":(r<0||i<n)&&(t.style.top="0",e.classList.remove("header-fixed")),this.y=window.pageYOffset})},loadMore=function(){var e=document.getElementById("articles-more");e&&e.addEventListener("click",function(t){var n=t.target;"A"==n.tagName&&n.classList.contains("more-link")&&(t.preventDefault(),n.childNodes[1].innerHTML="<img src='/static/img/loading.gif' alt='Loading...' />",fetch(n.getAttribute("data-next")).then(function(e){return e.text()}).then(function(t){e.insertAdjacentHTML("beforeend",t),e.removeChild(n)}))})},scrollTo=function(e,t,n){if(!(n<0||e.scrollTop==t)){var o=(t-e.scrollTop)/n*2;setTimeout(function(){e.scrollTop=e.scrollTop+o,scrollTo(e,t,n-2)},10)}},backTop=function(){document.getElementById("back-to-top").onclick=function(e){e.preventDefault(),scrollTo(document.body,0,100)}},formUI=function(){for(var e=document.querySelectorAll("form"),t=0;t<e.length;t++)!function(e){e.addEventListener("invalid",function(e){e.preventDefault()},!0),e.addEventListener("submit",function(e){this.checkValidity()||e.preventDefault()});var t=e.querySelectorAll(".errorlist");if(t.length>0)for(var n=0;n<t.length;n++)console.log("yo"),parent=t[n].parentNode,parent.classList.add("input-error");e.querySelector("button:not([type=button]), input[type=submit]").addEventListener("click",function(t){for(var n,o=e.querySelectorAll(":invalid"),r=e.querySelectorAll(".error-message"),i=0;i<r.length;i++)r[i].parentNode.removeChild(r[i]);for(i=0;i<o.length;i++)(n=o[i].parentNode).insertAdjacentHTML("beforeend","<div class='error-message'>"+o[i].validationMessage+"</div>"),n.classList.add("input-error");o.length>0&&scrollTo(document.body,o[0].offsetTop,100)})}(e[t])};domReady(function(){stickyHeader(),loadMore(),backTop(),formUI()});
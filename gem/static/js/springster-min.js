!function(){"use strict";function e(e,t){var n=window.XMLHttpRequest?new XMLHttpRequest:new ActiveXObject("Microsoft.XMLHTTP");return n.open("GET",e),n.onreadystatechange=function(){n.readyState>3&&200==n.status&&t(n.responseText)},n.setRequestHeader("X-Requested-With","XMLHttpRequest"),n.send(),n}var t=function(){document.documentElement.className=""},n=function(){document.body.classList.add("toggle-hide")},o=function(){var e=document.getElementById("header-wrapper"),t=document.getElementById("content-wrapper"),n=document.getElementById("nav-list"),o=function(e){window.innerWidth<1024?t.style.backgroundColor="#7300ff":t.style.backgroundColor="transparent",n.offsetHeight>50?n.classList.add("section-nav-list-wrap"):n.classList.remove("section-nav-list-wrap")};window.onresize=o,window.onload=o,window.addEventListener("scroll",function(){var n=this.y-window.pageYOffset,o=window.scrollY,r=document.getElementById("header-wrapper").clientHeight,i=document.getElementById("language-bar").clientHeight;o>0&&window.innerWidth>320&&(e.classList.add("header-fixed"),t.style.paddingTop=r+"px"),n>0&&o>r&&window.innerWidth>320?(e.style.transform="translate3d(0px, "+-i+"px, 0px)",t.style.paddingTop=r+"px"):o>r?e.style.transform="translate3d(0px, "+-r+"px, 0px)":(n<0||o<r)&&(e.style.transform="translate3d(0px, 0px, 0px)"),this.y=window.pageYOffset})},r=function(){var t=document.getElementById("more-link");if(t&&null===document.getElementById("articles-more")){var n=document.createElement("div");t.parentNode.insertBefore(n,t),n.appendChild(t),n.setAttribute("id","articles-more"),n.addEventListener("click",function(t){var n=t.target;"A"==n.tagName&&n.classList.contains("more-link")&&(t.preventDefault(),n.childNodes[1].innerHTML="<img src='/static/img/loading.gif' alt='Loading...' />",e(n.getAttribute("data-next"),function(e){n.parentNode.insertAdjacentHTML("beforeend",e),n.parentNode.removeChild(n)}))})}},i=function(e,t,n){if(!(n<0||e.scrollTop==t)){var o=(t-e.scrollTop)/n*2;setTimeout(function(){e.scrollTop=e.scrollTop+o,i(e,t,n-2)},10)}},a=function(){document.getElementById("back-to-top").onclick=function(e){e.preventDefault(),i(document.body,0,100)}},d=function(){var e=document.querySelectorAll("form");if(e)for(var t=0;t<e.length;t++)!function(e){e.addEventListener("invalid",function(e){e.preventDefault()},!0),e.addEventListener("submit",function(e){this.checkValidity()||e.preventDefault()});var t=e.querySelectorAll(".errorlist");if(t.length>0)for(var n=0;n<t.length;n++)parent=t[n].parentNode,parent.classList.add("input-error");var o=e.querySelector("button:not([type=button]), input[type=submit]"),r=document.getElementById("header-wrapper").clientHeight;o&&o.addEventListener("click",function(t){for(var n,o=e.querySelectorAll(":invalid"),a=e.querySelectorAll(".error-message"),d=0;d<a.length;d++)a[d].parentNode.removeChild(a[d]);for(var s=0;s<o.length;s++)(n=o[s].parentNode).insertAdjacentHTML("beforeend","<div class='error-message'>"+o[s].validationMessage+"</div>"),n.classList.add("input-error");o.length>0&&i(document.body,o[0].offsetTop-r,100)})}(e[t])};!function(e){"interactive"===document.readyState||"complete"===document.readyState?e():document.addEventListener("DOMContentLoaded",e)}(function(){t(),n(),o(),r(),a(),d()})}();
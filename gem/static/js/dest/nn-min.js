"use strict";!function(){var e;e=function(){!function(){var t=document.getElementById("header");document.getElementById("content_wrapper");window.addEventListener("scroll",function(){var e=this.y-window.pageYOffset,n=window.scrollY,o=document.getElementById("header").clientHeight+366.66;768<window.innerWidth&&(0<e&&o<n?(t.style.transform="translate3d(0px, 0px, 0px)",t.style.position="fixed"):o<n?(t.style.transform="translate3d(0px, "+-o+"px, 0px)",t.style.position="absolute"):(e<0||n<o)&&(t.style.transform="translate3d(0px, 0px, 0px)")),this.y=window.pageYOffset})}()},"interactive"===document.readyState||"complete"===document.readyState?e():document.addEventListener("DOMContentLoaded",e),$(document).ready(function(n){n(".dropdown-toggle").click(function(){var e=n(this).parents(".dropdown").children(".dropdown-menu").is(":hidden");n(".dropdown .dropdown-menu").hide(),n(".dropdown .dropdown-toggle").removeClass("open"),e&&n(this).parents(".dropdown").children(".dropdown-menu").toggle().parents(".dropdown").children(".dropdown-toggle").addClass("open")}),n(document).bind("click",function(e){n(e.target).parents().hasClass("dropdown")||n(".dropdown .dropdown-menu").hide()}),n(document).bind("click",function(e){n(e.target).parents().hasClass("dropdown")||n(".dropdown .dropdown-toggle").removeClass("open")})})}();
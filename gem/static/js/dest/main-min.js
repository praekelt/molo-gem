"use strict";!function(){for(var e=document.getElementById("image__identity").src.split(".").slice(-1),t=[{type:"image",ext:["png","jpg","jpeg","gif","svg"]},{type:"media",ext:["mpeg","ogg","jpeg"]}],g=0;g<t.length;g++)if("image"==t[g].type)for(var i=0;i<t[g].ext.length;i++)t[g].ext[i]==e[0]&&document.querySelector("meta[property='og:image:type']").setAttribute("content",t[0].type+"/"+t[0].ext[i]);else if("media"==t[g].type)for(i=0;i<t[g].ext.length;i++)t[g].ext[i]==e[0]&&document.querySelector("meta[property='og:image:type']").setAttribute("content",t[0].type+"/"+t[0].ext[i])}();
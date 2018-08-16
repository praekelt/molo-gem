/*! grunt-grunticon Stylesheet Loader - v2.1.6 | https://github.com/filamentgroup/grunticon | (c) 2015 Scott Jehl, Filament Group, Inc. | MIT license. */

!function(){function e(e,n){function t(){!a&&n&&(a=!0,n.call(e))}var a;e.addEventListener&&e.addEventListener("load",t),e.attachEvent&&e.attachEvent("onload",t),"isApplicationInstalled"in navigator&&"onloadcssdefined"in e&&e.onloadcssdefined(t)}!function(e){"use strict";var n=function(n,t,a){function o(e){if(d.body)return e();setTimeout(function(){o(e)})}function i(){l.addEventListener&&l.removeEventListener("load",i),l.media=a||"all"}var r,d=e.document,l=d.createElement("link");if(t)r=t;else{var s=(d.body||d.getElementsByTagName("head")[0]).childNodes;r=s[s.length-1]}var c=d.styleSheets;l.rel="stylesheet",l.href=n,l.media="only x",o(function(){r.parentNode.insertBefore(l,t?r:r.nextSibling)});var f=function(e){for(var n=l.href,t=c.length;t--;)if(c[t].href===n)return e();setTimeout(function(){f(e)})};return l.addEventListener&&l.addEventListener("load",i),l.onloadcssdefined=f,f(i),l};"undefined"!=typeof exports?exports.loadCSS=n:e.loadCSS=n}("undefined"!=typeof global?global:this),function(n){var t=function(a,o){"use strict";if(a&&3===a.length){var i=n.navigator,r=n.document,d=n.Image,l=!(!r.createElementNS||!r.createElementNS("http://www.w3.org/2000/svg","svg").createSVGRect||!r.implementation.hasFeature("http://www.w3.org/TR/SVG11/feature#Image","1.1")||n.opera&&-1===i.userAgent.indexOf("Chrome")||-1!==i.userAgent.indexOf("Series40")),s=new d;s.onerror=function(){t.method="png",t.href=a[2],loadCSS(a[2])},s.onload=function(){var n=1===s.width&&1===s.height,i=a[n&&l?0:n?1:2];t.method=n&&l?"svg":n?"datapng":"png",t.href=i,e(loadCSS(i),o)},s.src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==",r.documentElement.className+=" grunticon"}};t.loadCSS=loadCSS,t.onloadCSS=e,n.grunticon=t}(this)}();
(window.webpackJsonp=window.webpackJsonp||[]).push([[1],{teak:function(e,t,n){"use strict";n.r(t);var a,s=n("p0pE"),r=n.n(s),c=n("d6i3"),i=n.n(c),o=n("HP82");t.default={namespace:"bsmSetting",state:null!==(a=window.$$settings)&&void 0!==a?a:{},effects:{getSettings:i.a.mark(function e(t,n){var a,s,r;return i.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return a=n.call,s=n.put,e.next=3,a(o.getSettings);case 3:return r=e.sent,e.next=6,s({type:"changeSettings",payload:r});case 6:return e.next=8,s({type:"saveSettings",payload:r});case 8:case"end":return e.stop()}},e)}),changeSettings:i.a.mark(function e(t,n){var a,s,r,c;return i.a.wrap(function(e){for(;;)switch(e.prev=e.next){case 0:return a=t.payload,s=n.put,r=Object.keys(a),c={},r.forEach(function(e){void 0!==a[e]&&(c[e]=a[e])}),e.next=7,s({type:"setting/changeDefaultSettings",payload:c});case 7:case"end":return e.stop()}},e)})},reducers:{saveSettings:function(e,t){var n=t.payload;return r()({},e,n)}}}}}]);
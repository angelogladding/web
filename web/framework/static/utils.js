window.$ = function(selector) {
    if (typeof selector == "string")
        var node = document.querySelector(selector);
    else
        var node = selector;
    return node
}

window.$$ = function(selector) {
    var nodes = document.querySelectorAll(selector);
    var results = Array.prototype.slice.call(nodes);
    var items = {};
    for (var i = 0; i < results.length; i++)
        items[i] = results[i];
    items.length = results.length;
    items.splice = [].splice();  // simulates an array
    items.each = function(callback) {
        for (var i = 0; i < results.length; i++)
            callback.call(items[i]);
    }
    return items;
}

Element.prototype.appendAfter = function (element) {
    element.parentNode.insertBefore(this, element.nextSibling);
}, false;

var loadScripts = [];
var unloadScripts = [];
window.$.load = function(handler) {
    loadScripts.push(handler);
}
window.$.unload = function(handler) {
    unloadScripts.push(handler);
}

function executeLoadScripts() {
    loadScripts.forEach(function(handler) { handler(); });
    loadScripts = [];
}
function executeUnloadScripts() {
    unloadScripts.forEach(function(handler) { handler() });
    unloadScripts = [];
}

document.addEventListener("DOMContentLoaded", function() {
    executeLoadScripts();
});

window.addEventListener("beforeunload", function() {
    // XXX if (WEBACTION == false)
    // XXX     executeUnloadScripts();
});

function upgradeTimestamps() {
    var pageLoad = moment.utc();
    $$("time").each(function() {
        var value = this.attributes["datetime"].value;
        this.setAttribute("title", value);
        this.innerHTML = moment(value).from(pageLoad);
    });
}

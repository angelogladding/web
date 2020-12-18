/*! js-cookie v2.2.0 | MIT */
!function(e){var n=!1;if("function"==typeof define&&define.amd&&(define(e),n=!0),"object"==typeof exports&&(module.exports=e(),n=!0),!n){var o=window.Cookies,t=window.Cookies=e();t.noConflict=function(){return window.Cookies=o,t}}}(function(){function e(){for(var e=0,n={};e<arguments.length;e++){var o=arguments[e];for(var t in o)n[t]=o[t]}return n}function n(o){function t(n,r,i){var c;if("undefined"!=typeof document){if(arguments.length>1){if("number"==typeof(i=e({path:"/"},t.defaults,i)).expires){var a=new Date;a.setMilliseconds(a.getMilliseconds()+864e5*i.expires),i.expires=a}i.expires=i.expires?i.expires.toUTCString():"";try{c=JSON.stringify(r),/^[\{\[]/.test(c)&&(r=c)}catch(e){}r=o.write?o.write(r,n):encodeURIComponent(r+"").replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g,decodeURIComponent),n=(n=(n=encodeURIComponent(n+"")).replace(/%(23|24|26|2B|5E|60|7C)/g,decodeURIComponent)).replace(/[\(\)]/g,escape);var s="";for(var f in i)i[f]&&(s+="; "+f,!0!==i[f]&&(s+="="+i[f]));return document.cookie=n+"="+r+s}n||(c={});for(var p=document.cookie?document.cookie.split("; "):[],d=/(%[0-9A-Z]{2})+/g,u=0;u<p.length;u++){var l=p[u].split("="),C=l.slice(1).join("=");this.json||'"'!==C.charAt(0)||(C=C.slice(1,-1));try{var m=l[0].replace(d,decodeURIComponent);if(C=o.read?o.read(C,m):o(C,m)||C.replace(d,decodeURIComponent),this.json)try{C=JSON.parse(C)}catch(e){}if(n===m){c=C;break}n||(c[m]=C)}catch(e){}}return c}}return t.set=t,t.get=function(e){return t.call(t,e)},t.getJSON=function(){return t.apply({json:!0},[].slice.call(arguments))},t.defaults={},t.remove=function(n,o){t(n,"",e(o,{expires:-1}))},t.withConverter=n,t}return n(function(){})});

window.onerror = function(message, url, lineNumber) {
    alert(message);
}

function upgrade_fragmention(quote) {
    var last;
    $$("*").each(function() {
        if (!this.innerHTML)
            return
        var loc = this.innerHTML.search(quote);
        if (loc != -1)
            last = this;
    });
    if (last) {
        fragmention = escape(quote.replace(/\ /g, "-"));
        last.innerHTML = last.innerHTML.replace(quote,
            `<span class=fragmention id="#${fragmention}">${quote}</span>`);
        window.location.hash = "##" + fragmention;
    }
}

$.load(function() {
    upgradeTimestamps();

    // TODO window.debugSocket = new WebSocketClient.default(socket_origin + "debug",
    // TODO                                                  null,
    // TODO                                                  {backoff: "exponential"});
    // window.onerror = function(message, url, lineNumber) {
    //     window.debugSocket.send({message: message, url: url,
    //                              lineNumber: lineNumber});
    // };

    if (window.navigator.standalone && $("#signout"))
        $("#signout").style.display = "none";

    fragmention = window.location.href.split("##")[1];
    if (fragmention)
        upgrade_fragmention(unescape(fragmention.replace(/\-/g, " ")));

    fragment = window.location.href.split("#")[1];
    if (fragment)
        setTimeout(function() { window.location.hash = "#" + fragment; }, 1000);

    document.addEventListener("mouseup", event => {  
        var selection = window.getSelection().toString();
        if (selection.length) {
            upgrade_fragmention(selection);
        }
    });
});


/* ------------------------------- */


function contrast(shade) {
    document.querySelector("html").setAttribute("class", shade);
    Cookies("shade", shade, {expires: 365, path: "/", secure: true});
}
var shade = Cookies("shade");
if (shade)
    contrast(shade);
else
    contrast("dark");


/*
window.$ = function(selector) {
    try {
        return document.querySelector(selector)
    } catch (err) {
        console.log("ERROR", err);
    }
}

window.$.load = function(callback) {
    document.addEventListener("DOMContentLoaded", callback);
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
*/

function bindWebActions() {
    $$("indie-action").each(function() {
        this.onclick = function(e) {
            var action_link = this.querySelector("a");
            // TODO action_link.attr("class", "fa fa-spinner fa-spin");

            var action_do = this.getAttribute("do");
            var action_with = this.getAttribute("with");

            // protocolCheck("web+action://" + action_do + "?url=" + action_with,
            // setTimeout(function() {
            //     var url = "//canopy.garden/?origin=" + window.location.href +
            //               "do=" + action_do + "&with=" + action_with;
            //     var html = `<!--p>Your device does not support web
            //                 actions<br><em><strong>or</strong></em><br>
            //                 You have not yet paired your website with
            //                 your browser</p>
            //                 <hr-->
            //                 <p>If you have a website that supports web
            //                 actions enter it here:</p>
            //                 <form id=action-handler action=/actions-finder>
            //                 <label>Your Website
            //                 <div class=bounding><input type=text
            //                 name=url></div></label>
            //                 <input type=hidden name=do value="${action_do}">
            //                 <input type=hidden name=with value="${action_with}">
            //                 <p><small>Target:
            //                 <code>${action_with}</code></small></p>
            //                 <button>${action_do}</button>
            //                 </form>
            //                 <p>If you do not you can create one <a
            //                 href="${url}">here</a>.</p>`;
            //     switch (action_do) {
            //         case "sign-in":
            //             html = html + `<p>If you are the owner of this site,
            //                            <a href=/security/identification>sign
            //                            in here</a>.</p>`;
            //     }
            //     html = html + `<p><small><a href=/help#web-actions>Learn
            //                    more about web actions</a></small></p>`;
            //     $("#webaction_help").innerHTML = html;
            //     $("#webaction_help").style.display = "block";
            //     $("#blackout").style.display = "block";
            //     $("#blackout").onclick = function() {
            //         $("#webaction_help").style.display = "none";
            //         $("#blackout").style.display = "none";
            //     };
            // }, 200);

            window.location = action_link.getAttribute("href");

            e.preventDefault ? e.preventDefault() : e.returnValue = false;
        }
    });
}

$.load(function() {
    var alt_shade = {light: "dark", dark: "light"}
    $("body").innerHTML += "<p id=status><span class=disconnected></span></p>" +
                           "<p style='margin-top:1em;position:absolute;text-" +
                           "align:right;right:1em;top:0;z-index:9;'><small><a " +
                           " class=breakout style='border:0;' " +
                           "id=stylesheet_switcher>" +
                           '<svg class=contrast-icon style="height: 14px; width: 16px;">' +
                           '<use xlink:href="/icons.svg#contrast-icon"></use>' +
                           '<svg></a></small></p>';
    $("#stylesheet_switcher").addEventListener("click", function() { 
        var shade = Cookies("shade");
        contrast(alt_shade[shade]);
        // this.innerHTML = shade + " mode";
    });

    bindWebActions();

    /*
    $$(".pubkey").each(function() {
        var armored_pubkey = $(this).text();
        if (armored_pubkey) {
            var pubkey = get_pubkey(armored_pubkey);
            var fingerprint = pubkey.fingerprint.substring(0, 2);
            for (i = 2; i < 40; i = i + 2)
                fingerprint = fingerprint + ":" +
                              pubkey.fingerprint.substring(i, i + 2);
            $(this).after("<code class=fingerprint><span>" +
                          fingerprint.substr(0, 30) + "</span><span>" +
                          fingerprint.substr(30, 60) + "</span></code>");
        }
    });
    */

    // var mySVG = document.getElementById("action_like");
    // var svgDoc;
    // mySVG.addEventListener("load",function() {
    //     svgDoc = mySVG.contentDocument;
    //     path = svgDoc.querySelector("path");
    //     setTimeout(function() {
    //         path.setAttribute("fill", "red");
    //         mySVG.setAttribute("class", "icon animated pulse");
    //     }, 2000);
    // }, false);

    // $$(".icon").each(function() {
    //     var svgDoc;
    //     var mySVG = this;
    //     mySVG.addEventListener("load", function() {
    //         svgDoc = mySVG.contentDocument;
    //         // function z() {
    //             svgDoc.querySelector("path").setAttribute("fill", "#2aa198");
    //             // mySVG.setAttribute("class", "icon animated pulse");
    //         // }
    //         // setTimeout(z, 2000);
    //     }, false);
    // });

    var blackout = document.createElement("div");
    blackout.setAttribute("id", "blackout");
    document.body.appendChild(blackout);
    $("#blackout").style["display"] = "none";

    // $("a.quote").click(function() {
    //     window.location = "web+action://quote=?url=" + window.location +
    //                       "&quote=" + window.getSelection().toString();
    //     return false
    // });

    // $$("#search").submit(function() {
    //     $.ajax({method: "GET",
    //              url: "/search?query=" +
    //                   $(this).find("input[name=query]").val()})
    //         .done(function(msg) { $("#resource_preview").html(msg); });
    //     return false
    // });
});

function get_pubkey(armored_pubkey) {
    /*
    handle displaying of fingerprints
    
    */
    var foundKeys = openpgp.key.readArmored(armored_pubkey).keys;
    if (!foundKeys || foundKeys.length !== 1) {
        throw new Error("No key found or more than one key");
    }
    var pubKey = foundKeys[0];
    foundKeys = null;
    return pubKey.primaryKey
}

// activate fast AES-GCM mode (not yet OpenPGP standard)
// openpgp.config.aead_protect = true;  // TODO move to after openpgp load

function sign(payload, handler) {
    // XXX var pubkey = localStorage["pubkey"];
    // XXX var privkey = localStorage["privkey"];
    // XXX var passphrase = "";  // window.prompt("please enter the pass phrase");

    // XXX // console.log(openpgp.key.readArmored(privkey));
    // XXX // var privKeyObj = openpgp.key.readArmored(privkey).keys[0];
    // XXX // privKeyObj.decrypt(passphrase);

    // XXX // options = {
    // XXX //     message: openpgp.cleartext.fromText('Hello, World!'),
    // XXX //     privateKeys: [privKeyObj]
    // XXX // };

    // XXX // openpgp.sign(options).then(function(signed) {
    // XXX //     cleartext = signed.data;
    // XXX //     console.log(cleartext);
    // XXX // });

    // XXX openpgp.key.readArmored(privkey).then(function(privKeyObj) {
    // XXX     // XXX var privKeyObj = z.keys[0];
    // XXX     // XXX privKeyObj.decrypt(passphrase);
    // XXX     // XXX var options = {data: payload, privateKeys: privKeyObj};
    // XXX     var options = {message: openpgp.cleartext.fromText("helloworld"),
    // XXX                    privateKeys: [privKeyObj]}
    // XXX     openpgp.sign(options).then(handler);
    // XXX });
}

function sign_form(form, data, submission_handler) {
    var button = form.find("button");
    button.prop("disabled", true);
    var timestamp = Date.now();
    form.append("<input type=hidden name=published value='" +
                timestamp + "'>");
    data["published"] = timestamp
    var payload = JSON.stringify(data, Object.keys(data).sort(), "  ");
    sign(payload, function(signed) {
        form.append("<input id=signature type=hidden name=signature>");
        $("#signature").val(signed.data);
        // XXX form.submit();
        submission_handler();
        button.prop("disabled", false);
    });
}

function num_to_sxg(n) {
  var d, m, p, s;
  m = "0123456789ABCDEFGHJKLMNPQRSTUVWXYZ_abcdefghijkmnopqrstuvwxyz";
  p = "";
  s = "";
  if (n==="" || n===0) { return "0"; }
  if (n<0) {
    n = -n;
    p = "-";
  }
  while (n>0) {
    d = n % 60;
    s = strcat(m[d], s);
    n = (n-d)/60;
  }
  return strcat(p, s);
}

function num_to_sxgf(n, f) {
  if (!f) { f=1; }
  return str_pad_left(num_to_sxg(n), f, "0");
}

function string($n) {
  if (typeof($n)==="number") {
    return Number($n).toString(); 
  } else if (typeof($n)==="undefined") {
    return "";
  } else {
    return $n.toString();
  }
}

function str_pad_left(s1, n, s2) {
  s1 = string(s1);
  s2 = string(s2);
  n -= strlen(s1);
  while (n >= strlen(s2)) { 
    s1 = strcat(s2, s1); 
    n -= strlen(s2);
  }
  if (n > 0) {
    s1 = strcat(substr(s2, 0, n), s1);
  }
  return s1;
}

function strlen(s) {
  return s.length;
} 

function count(a) {
  return a.length;
}

function strcat() {
  var args, i, r;
  r = "";
  args = arguments;
  for (i=count(args)-1; i>=0; i-=1) {
    r = args[i] + r;
  }
  return r;
}

function getTimeSlug(when) {
    var centiseconds = (((when.hours() * 3600) +
                         (when.minutes() * 60) +
                         when.seconds()) * 100) +
                       Math.round(when.milliseconds() / 10);
    return when.format("Y/MM/DD/") +
           num_to_sxgf(centiseconds, 4)
}

function getTextSlug(words) {
    var padding = "";
    if (words.slice(-1) == " ")
        padding = "_";
    return words.toLowerCase().split(punct_re).join("_")
                .replace(/_$$/gm, "") + padding;
}

/*
function previewImage(file, preview_container) {
    return false
    var reader = new FileReader();
    reader.onload = function (e) {
        preview_container.attr("src", e.target.result);
    }
    reader.readAsDataURL(file);

    // var data = new FormData();
    // data.append("file-0", file);
    // $.ajax({method: "POST",
    //         url: "/editor/media",
    //         contentType: "multipart/form-data",
    //         data: data
    //        }).done(function(msg) {
    //                    console.log("repsonse");
    //                    console.log(msg);
    //                    var body = msg["content"];
    //                    preview_container.html(body);
    //                });
}
*/

function previewResource(url, handler) {
    if (url == "") {
        // preview_container.innerHTML = "";
        return
    }

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/editor/preview/microformats?url=" +
                    encodeURIComponent(url));
    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            // var entry = response["entry"];
            // XXX console.log(response);
            handler(response);
            // var body = "";
            // if ("profile" in response) {
            //     // asd
            // } else if (entry) {
            //     if ("name" in entry)
            //         body = "unknown type";
            //     else if ("photo" in entry)
            //         body = "Photo:<br><img src=" + entry["photo"] + ">";
            //     else
            //         body = "Note:<br>" + entry["content"];
            // }
            // preview_container.innerHTML = body;
        } else
            console.log("request failed: " + xhr.status);
    };
    xhr.send();
}

// $(function() {
//     var current_body = "";
//     function setTimer() {
//         setTimeout(function() {
//             var new_body = $("#body").val();
//             if (new_body != current_body) {
//                 $.ajax({method: "POST",
//                          url: "/content/editor/preview",
//                          data: {content: new_body}
//                         }).done(function(msg) {
//                                     $("#body_readability").html(msg["readability"]);
//                                     $("#body_preview").html(msg["content"]);
//                                 });
//                 current_body = new_body;
//             }
//             setTimer();
//         }, 5000);
//     };
//     setTimer();
// });

const socket_origin = (window.location.protocol == "http:" ? "ws" : "wss") +
                      "://" + window.location.host + "/";

window.onpopstate = function(e) {
    if (e.state === null)
        return
    console.log("popping", e.state);
    updateArticle(window.location, e.state.scroll);
}

function updateArticle(url, scroll) {
    $("#loading").style.display = "block";
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.setRequestHeader("X-Chromeless", "1");
    xhr.onload = function() {
        executeUnloadScripts();

        dom = new DOMParser().parseFromString(xhr.responseText, "text/html");
        newElement = dom.querySelector("body > article");
        var currentElement = $("body > div > article");
        currentElement.height = 0;
        newElement.appendAfter(currentElement);
        currentElement.remove();

        document.body.scrollTop = document.documentElement.scrollTop = scroll;

        $$("body > div > article a:not(.breakout)").each(upgradeLink);
        $$("body > div > article script").each(function() {
            if (this.src != "")
                document.getElementsByTagName("head")[0].appendChild(this);
            else
                eval(this.innerHTML);
        });
        executeLoadScripts();
        upgradeTimestamps();
        bindWebActions();

        h1 = newElement.querySelector("h1");
        title = owner;
        if (h1)
            title = h1.textContent + "\u2009\u2014\u2009" + title;
        window.document.title = title;
        $("#loading").style.display = "none";
    };
    /* xhr.onprogress = function() {
        // progress on transfers from the server to the client (downloads)
        function updateProgress (e) {
            console.log(e);
            if (e.lengthComputable) {
                var percentComplete = e.loaded / e.total * 100;
                debugSocket.send(percentComplete);
                // ...
            } else {
                // Unable to compute progress information since the total size is unknown
            }
        }
    }; */
    xhr.timeout = 10000;
    xhr.ontimeout = function () {
        // TODO exponential backoff?
        console.log(`Request for ${url} timed out. retrying..`);
        updateArticle(url, scroll);
    }
    xhr.send();
}

// TODO back button when coming back from different origin or same page hash

var WEBACTION = false;

function upgradeLink() {
    var url = this.href;
    if (url.indexOf("web+action") == 0) {  // web actions
        this.addEventListener("click", (ev) => {
            if (ev.ctrlKey)
                return
            // ev.preventDefault();
            WEBACTION = true;
            return
        });
        return  // use native
    }
    if (url.indexOf(origin) == -1) {  // different origin
        return  // use native
    }
    if (url.indexOf("#") > -1) {  // same origin, contains fragment identifier
        var url_parts = url.split("#");
        var current_url_parts = window.location.href.split("#");
        if (url_parts[0] == current_url_parts[0])  // same page
            return  // use native
        // different page
        // XXX console.log(url_parts, current_url_parts);
    }
    this.addEventListener("click", (ev) => {
        if (ev.ctrlKey)
            return
        ev.preventDefault();
        history.replaceState({scroll: window.pageYOffset}, "title",
                             window.location);
        updateArticle(url, 0);
        history.pushState({scroll: 0}, "title", url);
    });
}

/*****************************************************************/

window.addEventListener('online',  updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

function updateOnlineStatus(event) {
    console.log("Device is "+(navigator.onLine ? "online" : "offline"));
    
    if(navigator.onLine) {
        $("body").addClass("online").removeClass("offline");
        if(window.syncAllPosts) {
            console.log('syncing posts');
            refreshSavedPosts();
            syncAllPosts();    
        }
    } else {
        $("body").addClass("offline").removeClass("online");
        if(window.refreshSavedPosts) {
            console.log('loading posts');
            refreshSavedPosts();
        }
    }
}

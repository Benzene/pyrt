/*  Copyright (C) 2012 by mountainpenguin (pinguino.de.montana@googlemail.com)
 *  http://github.com/mountainpenguin/pyrt
 *
 *  This file is part of pyRT.
 *  
 *  pyRT is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  pyRT is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with pyRT.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

$(document).ready( function () {
    $(".add_filter_button").live("click", function () {
        var regex = true;
        var positivevals = new Array();
        var negativevals = new Array();
        var sizelims = null;
        var quickexit = null;
        $(this).closest(".add_filter_div").children().each( function () {
            if ($(this).hasClass("add_filter") && $(this).children("input[type=text]")[0].value !== "") {
                regex = $(this).find("div > input[type=checkbox]")[0].checked;
                positivevals.push( $(this).children("input[type='text']")[0].value );
            } else if ($(this).hasClass("and_filter") && $(this).children("input")[0].value !== "") {
                positivevals.push( $(this).children("input")[0].value );
            } else if ($(this).hasClass("not_filter") && $(this).children("input")[0].value !== "") {
                negativevals.push( $(this).children("input")[0].value );
            } else if ($(this).hasClass("size_filter")) {
                var lower = $(this).children("input")[0].value;
                var lowertype = $(this).children("select")[1].value;
                var upper = $(this).children("input")[1].value;
                var uppertype = $(this).children("select")[2].value;
                if (!(lower == "" && upper == "")) {
                    if (!sizelims) {
                        if (lower == "") {
                            lower = 0;
                        }
                        if (upper == "") {
                            upper = 0;
                        }
                        lower *= lowertype;
                        upper *= uppertype;
                        sizelims = new Array(lower, upper);
                    } else {
                        alert("More than one size limit has been specified, remove the second and try again");
                        quickexit = true;
                        return;
                    }
                }
            }
        });
        if (quickexit) {
            return false;
        }
        if (sizelims) {
            sizelims = sizelims.join("||||||");
        } else {
            sizelims = "";
        }
        if (positivevals.length == 0) {
            positivevals = "";
        } else {
            positivevals = positivevals.join("||||||");
        }
        if (negativevals.length == 0) {
            negativevals = "";
        } else {
            negativevals = negativevals.join("||||||");            
        }
        var name = $(this).closest(".remote_setting").attr("id").split("remote_settings_")[1];
        if (positivevals == "" && negativevals == "" && sizelims == "") {} else {
            var req = "request=add_filter&name=" + name;
            req += "&regex=" + regex;
            req += "&positive=" + encodeURIComponent(positivevals);
            req += "&negative=" + encodeURIComponent(negativevals);
            req += "&sizelim=" + encodeURIComponent(sizelims);
            socket.send(req);
        }
    });
    //$(".filter_select").live("change", function() {
    //    var selectelem = $("<select class='filter_select'><option selected='selected'>---</option><option>and</option><option>not</option><option>size</option></select>");
    //    var andinput = $("<input name='add_filter' class='input_filter' type='text' placeholder='Positive Filter' />");
    //    var notinput = $("<input name='not_filter' class='input_filter' type='text' placeholder='Negative Filter' />");
    //    var sizeinput = $("<input class='input_filter size lower' type='number' placeholder='Lower' min=0 /> \
    //                            <select> \
    //                                <option value=1073741824>GB</option> \
    //                                <option value=1048576>MB</option> \
    //                                <option value=1024>KB</option> \
    //                                <option value=1>B</option> \
    //                            </select> \
    //                        <input class='input_filter size upper' type='number' placeholder='Upper' min=0 /> \
    //                            <select> \
    //                                <option value=1073741824>GB</option> \
    //                                <option value=1048576>MB</option> \
    //                                <option value=1024>KB</option> \
    //                                <option value=1>B</option> \
    //                            </select>");
    //    if ($(this).val() == "---") {
    //        if ($(this).parent().children("select").length == 2) {
    //            $(this).parent().prev().append($(this));
    //            $(this).parent().next().remove();
    //        } else {
    //            $(this).parent().remove();
    //        }
    //    } else if ($(this).val() == "and") {
    //        if ($(this).next().length > 0) {
    //            $(this).parent().toggleClass("not_filter and_filter");
    //            $(this).next().attr("placeholder", "Filter");
    //            return;
    //        }
    //        $(this).parent().after(
    //            $("<div class='and_filter' />")
    //            .append(andinput)
    //            .append(selectelem)
    //        );
    //        $(this).parent().next().prepend($(this));
    //    } else if ($(this).val() == "not") {
    //        if ($(this).next().length > 0) {
    //            $(this).parent().toggleClass("not_filter and_filter");
    //            $(this).next().attr("placeholder", "Negative Filter");
    //            return;
    //        }
    //        $(this).parent().after(
    //            $("<div class='not_filter' />")
    //            .append(notinput)
    //            .append(selectelem)
    //        );
    //        $(this).parent().next().prepend($(this));
    //    }
    //});
    $(".filter_group").live("click", function () {
        var name = $(this).closest(".remote_setting").attr("id").split("remote_settings_")[1];
        var index = $(".filter_group", $(this).parent()).index($(this));
        var c = confirm("Are you sure you want to remove this filter?");
        if (c) {
            socket.send("request=remove_filter&name=" + name + "&index=" + index);
        }
    });
    $("#dialog_form").dialog({
        autoOpen: false,
        height: 300,
        width: 350,
        modal: true,
        buttons: {
            "Submit": function () {
                var pw=$("#password").val();
                // encrypt password by normal method (secure from MITM attacks
                // due to the time-based OTP nature [?] )
                var hashed = hashPassword(pw);

//                args.salt = salt;
//                var hash = hashed.split("$")[2];
                // use hash to encrypt message using AES encryption
//                for (i=0; i<args.tocrypt.length; i++) {
//                    var encrypted = CryptoJS.AES.encrypt(args.tocrypt[i][1], hash, {iv: salt, mode: CryptoJS.mode.CFB});
//                    console.log("iv: " + salt + " " + encrypted.iv);
//                    console.log("key: " + hash + " " + encrypted.key);
//                    console.log("encrypted: " + encrypted.ciphertext);
                
                // decrypting with PyCrypto is too complicated to sort out, so
                // send plaintext for now
                
                args.auth = hashed;
                var q_ = []
                $.each(args, function(key, value) {
                    q_.push(key + "=" + encodeURIComponent(value));
                });
                var query = q_.join("&");
                socket.send(query);
                $(this).dialog("close");
            },
            "Cancel": function() { 
                $(this).dialog("close");
            }
        },
        close: function () {
            $("#password").val("");
            args = null;
        }
    });

    $(".remote_row").live("click", function (evt) {
        var next_row = $(this).next();
        if (next_row.hasClass("is_hidden")) {
            next_row.removeClass("is_hidden");
        } else {
            next_row.addClass("is_hidden");
        }
    });
    $("input").live("keydown", function (evt) {
        $(this).prev().css({color:"", "font-weight":"", "font-style":""});
    });
    $(".submit_button").live("click", function (evt) {
        // get arguments
        var inputs = $("input", $(this).parent().parent());
        args = new Object();
        args.tocrypt = [];
        var exit = false;
        inputs.each( function (elem) {
            var key = $(this).attr("name");
            var value = $(this).attr("value");
            if (!value) {
                $(this).prev().css({color: "red", "font-weight": "bold", "font-style": "italic"});
                exit = true;
            } else {
//                args.tocrypt.push( new Array(key, value) );
                args[key] = value
            }
        });
        if (exit) {
            return false;
        } else {
            args.request = "set_source";
            // set args name value for assignment on other side
            args.name = $(this).attr("id").split("submit_")[1];
            $("#dialog_form").dialog("open");
        }
    });
});

function runSocketInit() {
    socket.send("request=get_sources")
}

function runSocketPostInit() {
     $(".bot_button").live("click", function () {
        if ($(this).is(":disabled")) {
            return;
        }

        if ($(this).attr("id").indexOf("start_") !== -1) {
            var name = $(this).attr("id").split("start_")[1];
            socket.send("request=start_bot&arguments=" + name);
        } else {
            var name = $(this).attr("id").split("stop_")[1];
            socket.send("request=stop_bot&arguments=" + name);
        }

        // disable button and replace icon with loading gif
        $(this).attr("disabled", true)
               .find("img").attr("src", "images/loading.gif");
    });
}

function onOpen (evt) {
    console.log("autoSocket opened", evt, socket);
    runSocketInit();
}

function onMessage (evt) {
     if (evt.data == "pong") {
         return;
     }
     if (evt.data.indexOf("ERROR") === 0) {
        console.log(evt.data);
        socket.close();
     } else {
          var response = JSON.parse(evt.data);
          if (response.request == "get_sources") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
                    return false;
               }
               var load = $("div#available").remove();
               var tab = $("table#available > tbody");
               for (i=0; i<response.response.length; i++) {
                    tab.append($(response.response[i].row));
                    tab.append($(response.response[i].req_row));
               }
               runSocketPostInit();
          } else if (response.request == "get_source_single") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
                    return false;
               }
               refresh_drop_down_respond(response.response);
          } else if (response.request == "add_filter") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
                    return false;
               }
               refresh_drop_down(response.name);
          } else if (response.request == "start_bot") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
                    refresh_drop_down(response.name);
                    return false;
               }
               setTimeout(function () { refresh_drop_down(response.name); }, 2000);
          } else if (response.request == "stop_bot") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
               }
               refresh_drop_down(response.name);
          } else if (response.request == "remove_filter") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
                    return false;
               }
               refresh_drop_down(response.name);
          } else if (response.request == "set_source") {
               if (response.error) {
                    console.log("ERROR in request " + response.request + ": " + response.error);
                    return false;
               }
               refresh_drop_down(response.name);
          } else {
            console.log("socket message:", evt.data)
          }
     }
}

function refresh_drop_down(name) {
    // get drop down
    socket.send("request=get_source_single&arguments=" + name);
}
function refresh_drop_down_respond(data) {
    var row = $(data.req_row);
    var name = row.attr("id").split("remote_settings_")[1];
    var started = $(".bot_button", row).attr("id");
    if (started.indexOf("start_") == 0) {
        $(".status-" + name).html("off").removeClass("status-on").addClass("status-off");
    } else {
        $(".status-" + name).html("on").removeClass("status-off").addClass("status-on");
    }
    $("#remote_settings_" + name).html(
        row.html()
    );
}

$(document).ready(function () {
     setTimeout(function () {
        refresh_content("yes");
     }, 5000);
    $("#add-torrent-button").click(function(){
      $("#add_torrent").dialog("open");
    })
    $("#add_torrent").dialog({
          height: 220,
          width: 420,
          modal: true,
          autoOpen: false,
          buttons: {
                  "Add torrent": function() {
                     if (!($("#add_torrent_input").val())) {
                          $("#add_torrent_form").css("border","1px solid red");
                      } else {
                        $("#add_torrent_form").submit();
                      }
                  },
                  Cancel: function() {
                    $( this ).dialog( "close" );
                  }
                }
        });
    loadRClickMenus();
    stripeTable();
});

function stripeTable() {
    var colour_classes = Array("blue", "green");
    $(".torrent-div").each(
        function () {
            col = colour_classes.shift();
            $(this).removeClass("blue green");
            $(this).addClass(col);
            colour_classes.push(col);
        }
    );
}
function loadRClickMenus() {
    $(".torrent-div.rcstart").contextMenu("right_click_start", {
        bindings : {
            "start" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("start_torrent", torrent_id);
            },
            "stop" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("stop_torrent", torrent_id);            
            },
            "remove" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("remove_torrent", torrent_id);
            },
            "delete" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("delete_torrent", torrent_id);
            },
            "rehash" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("hash_torrent", torrent_id);
            },
        },
        menuStyle : {
            minWidth : "10em"
        }
    });
    $(".torrent-div.rcpause").contextMenu("right_click_pause", {
        bindings : {
            "pause" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("pause_torrent", torrent_id);
            },
            "stop" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("stop_torrent", torrent_id);            
            },
            "remove" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("remove_torrent", torrent_id);
            },
            "delete" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("delete_torrent", torrent_id);
            },
            "rehash" : function (t) {
                var torrent_id = t.id.split("torrent_id_")[1];
                command("hash_torrent", torrent_id);
            },
        },
        menuStyle : {
            minWidth : "10em"
        }
    });
    $("#tab_options").bind(
        "click",
        function () {
        window.location = "/options?test=test";
        }
    );
    $("#tab_rss").bind(
        "click",
        function() {
          window.location = "/RSS";
        }
    );
}
function refresh_content(repeat) {
    // get all torrent ids on page
    req = "/ajax?request=get_info_multi&view=" + $("#this_view").html()
    if (!($("#this_sort").html() === "none")) {
        req += "&sortby=" + $("#this_sort").html();
    }
    if (!($("#this_reverse").html() === "none")) {
        req += "&reverse=" + $("#this_reverse").html();
    }
    $.getJSON(req, function (data) {
        $("#global_stats").html(data.system);
        
        // data has structure:
            //{
            //    "torrents" : {},
            //    "system" : system_html,
            //    "torrent_index" : [id, id, id] // this is in the order that they are arranged in the page (or should be if this has changed)
            //}
        torrent_list = $("#torrent_list").find($("tr")).filter(
            function (index) {
                return (!($(this).attr("id").indexOf("torrent_id_") === -1))
            }
        )
        cur_t_ids = new Array();
        for (i=0; i<torrent_list.length; i++) {
            var torrent_id = $(torrent_list[i]).attr("id").split("torrent_id_")[1];
            cur_t_ids.push(torrent_id);
            if (data.torrent_index.indexOf(torrent_id) == -1) {
                remove_torrentrow(torrent_id)
            } else {
                // refresh torrent data
                torrent_data = data.torrents[torrent_id];
                // returned data: ratio, uprate, downrate, status
                $("#t_ratio_" + torrent_id).html(torrent_data.ratio);
                $("#t_uprate_" + torrent_id).html(torrent_data.uprate + "/s");
                $("#t_downrate_" + torrent_id).html(torrent_data.downrate + "/s");
                var oldstatus = $("#t_status_" + torrent_id)
                if (oldstatus.html() != torrent_data.status) {
                    oldstatus.html(torrent_data.status);
                    var reqrefresh = "/ajax?request=get_torrent_row&torrent_id=" + torrent_id;
                    $.ajax({
                        url : reqrefresh,
                        context : $("#t_controls_" + torrent_id),
                        dataType : "html",
                        success : function (newrowhtml) {
                            $(this).html(
                                $("#" + $(this).attr("id"), newrowhtml).html()
                            );
                        },
                        error : function (jqXHR, textStatus, errorThrown) {
                            alert("Error " + jqXHR + " (" + errorThrown + ")");
                        }
                    });
                }
                
            }
        }
          
        // check for new torrents and add them
        for (i=0; i<data.torrent_index.length; i++) {
            torrent_id = data.torrent_index[i];
            if ($.inArray(torrent_id, cur_t_ids) === -1) {
                add_torrentrow(torrent_id, data.torrents[torrent_id])
            }
        }
        
        if (repeat === "yes") {
            setTimeout(function () {
                refresh_content("yes");
            }, 5000);
        }
    });
}

function remove_torrentrow(torrent_id) {
    var row = $("#torrent_id_" + torrent_id);
    if (row.length != 0) {
        $(row).removeClass("blue green").toggleClass("old-torrent-row");
        $(row).effect("pulsate", { times : 1 }, "slow", function() {
            $(row).fadeTo(2000, 0.1, function() {
                $(this).slideRow("up", 1000, function() {
                    $("#torrent_id_" + torrent_id).remove();
                    stripeTable();
                });
            });
        });
    }
}

function add_torrentrow(torrent_id, torrent_data) {
    var req = "/ajax?request=get_torrent_row&torrent_id=" + torrent_id;
    var torrent_list = $("#torrent_list");
    $.ajax({
        url : req,
        context : torrent_list,
        dataType : "html",
        success : function (newrowhtml) {
            $("#torrent_list > tbody > tr:eq(0)").after($(newrowhtml));
            var newrow = $("#torrent_id_" + torrent_id);
            $(newrow).toggleClass("new-torrent-row");
            $(newrow).slideRow("down", 1000, function () {
                $(newrow).fadeTo(2000, 1.0, function() {
                    $(newrow).effect("pulsate", { times : 1 }, "slow", function () {
                        $(newrow).toggleClass("new-torrent-row");
                        stripeTable();
                        loadRClickMenus()
                    });
                });
            });
        },
        error : function (jqXHR, textStatus, errorThrown) {
            alert("Error " + jqXHR + " (" + errorThrown + ")");
        }
    });
}

function select_torrent(elem) {
    // elem.style.backgroundColor = "#00CCFF";
    elem.style.backgroundColor = "#0099FF";
    elem.style.cursor = "help";
}
function deselect_torrent(elem) {
    elem.style.backgroundColor = null;
    elem.style.cursor = "default";
}
function select_tab(elem) {
   elem.style.backgroundColor = "#bbbbbb"; 
}

function deselect_tab(elem) {
    elem.style.backgroundColor = null;
}

function navigate_tab(elem) {
    window.location = "?view=" + elem.id.split("tab_")[1];
}

function navigate_tab_fromRSS(elem) {
     window.location = "/?view=" + elem.id.split("tab_")[1];
}

function navigate_torrent(elem) {
    window.location = "detail?torrent_id=" + elem.id.split("torrent_id_")[1]
}

function removerow(torrent_id) {
    if (row = document.getElementById("newrow_torrent_id_" + torrent_id)) {
        var table = document.getElementById("torrent_list");
        table.deleteRow(row.rowIndex);
    }
    
}
function view_torrent(elem) {
    var torrent_id = elem.id.split("torrent_id_")[1];
    var table = document.getElementById("torrent_list");
    if (oldrow = document.getElementById('newrow_torrent_id_' + torrent_id)) {
        table.deleteRow(oldrow.rowIndex);
    }
    var newrow = table.insertRow(elem.rowIndex + 1);
    var newcell = newrow.insertCell(0);
    newrow.id = "newrow_torrent_id_" + torrent_id;
    newrow.className += " drop_down";
    newcell.innerHTML = "<img src='/images/loading.gif'> <span style='color:red;'>Loading</span>";
    newcell.colSpan = "7";
    var xmlhttp = new XMLHttpRequest();
    var url="ajax"
    xmlhttp.open("POST",url,true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var response = xmlhttp.responseText;
            newcell.innerHTML = response;
        }
    }
    var params = "request=get_torrent_info&html=yesplease&torrent_id=" + torrent_id;
    xmlhttp.send(params);
}

function command(cmd, t_id) {
    if (cmd === "pause_torrent" || cmd === "start_torrent" || cmd === "stop_torrent" || cmd == "remove_torrent" || cmd == "delete_torrent" || cmd == "hash_torrent") {
        var resp;
        if (cmd === "remove_torrent") {
            resp = confirm("Are you sure you want to remove this torrent?");
        } else if (cmd == "delete_torrent") {
            resp = confirm("Are you sure you want to remove this torrent and *permanently* delete its files?");
        } else if (cmd == "hash_torrent") {
            resp = confirm("Are you sure you want to rehash this torrent?\n This process can take a long time for large torrents");
        } else {
            resp = true;
        }
        if (resp) {
            var xmlhttpc = new XMLHttpRequest();
            var url="ajax";
            xmlhttpc.open("POST",url,true);
            xmlhttpc.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            xmlhttpc.onreadystatechange = function() {
                if (xmlhttpc.readyState == 4 && xmlhttpc.status == 200) {
                    var resp = xmlhttpc.responseText.trim()
                    if (resp == "OK") {
                        refresh_content("no");
                    } else {
                        alert("Command Failed with reason: " + resp); 
                    }
                }
            }
            var params = "request=" + cmd + "&torrent_id=" + t_id;
            xmlhttpc.send(params);
        } else {
            return false;
        }
    } else {
        alert("invalid command or command not implemented");
    }
}
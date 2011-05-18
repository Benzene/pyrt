#!/usr/bin/env python

import random
import string
import os
import re

class Handler:
    """
        handler class for various reusable sundry operations
    """
    def __init__(self):
        pass

    def humanTimeDiff(self, secs):
        time_str = ""
        if secs > 60*60*24*7:
            wks = secs / (60 * 60 * 24 * 7)
            time_str += "%iw " % wks
            secs -= wks * (60*60*24*7)
        if secs > 60*60*24:
            dys = secs / (60 * 60 * 24)
            time_str += "%id " % dys
            secs -= dys * (60 * 60 * 24)
        hrs = secs / (60*60)
        secs -= hrs * (60 * 60)
        mins = secs / 60
        secs -= mins * 60
        
        time_str += "%02ih %02i:%02i" % (hrs, mins, secs)
        
        return time_str
        
    def humanSize(self, bytes):
        """
            takes a int/float value of <bytes>
            returns a string of <bytes> in a human readable unit (with two decimal places)
            (currently supports TB, GB, MB, KB and B)
        """
        if bytes > 1024*1024*1024*1024:
            return "%.02f TB" % (float(bytes) / 1024 / 1024 / 1024 / 1024)
        elif bytes > 1024*1024*1024:
            return "%.02f GB" % (float(bytes) / 1024 / 1024 / 1024)
        elif bytes > 1024*1024:
            return "%.02f MB" % (float(bytes) / 1024 / 1024)
        elif bytes > 1024:
            return "%.02f KB" % (float(bytes) / 1024)
        else:
            return "%i B" % bytes

    def getState(self, t):
        """
            outputs a more 'advanced' status from an inputted <t> (rtorrent.Torrent object)
            possible outcomes:
                'Stopped'         # torrent is closed
                'Paused'          # torrent is open but inactive
                'Seeding (idle)'  # torrent is active and complete, but no connected peers
                'Seeding'         # torrent is active, complete, and has connected peers
                'Leeching (idle)' # torrent is active and incomplete, but no connected peers
                'Leeching'        # torrent is active, incomplete, and has connected peers
        """
        status_actual = t.status
        if status_actual == "Active":
            if t.completed_bytes == t.size:
                status = "Seeding"
                if t.peers_connected == 0:
                    status = "Seeding (idle)"
            else:
                status = "Leeching"
                if t.seeds_connected == 0 and t.peers_connected == 0:
                    status = "Leeching (idle)"
        else:
            status = t.status
        return status
    
    def HTMLredirect(self, url, refresh=0, body=""):
        return """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
                <meta http-equiv="REFRESH" content="%i;url=%s">
                <link rel="stylesheet" type="text/css" href="/css/main.css"
                <title>Redirect</title>
            </head>
            <body>
                %s
            </body>
        </html>
        """ % (refresh, url, body)
    
    def getFileStructure(self, files, rtorrent_root):
        folder = {}
        files_dict = {}
        priorites = {"high" : 2, "normal" : 1, "off" : 0}
        for file in files:
            random_id = "".join([random.choice(string.letters + string.digits) for i in range(10)])
            files_dict[random_id] = file
            if file.base_path == rtorrent_root:
                folder["."] = {"___files" : [random_id]}
                break
            else:
                if os.path.basename(file.base_path) not in folder.keys():
                    #create folder entry
                    folder[os.path.basename(file.base_path)] = {
                        "___files" : [],
                        "___size" : 0,
                        "___priority" : [file.priority],
                        "___completion" : 0,
                    }
                    
                for index in range(len(file.path_components)):
                    base = os.path.basename(file.base_path)
                    component = file.path_components[index]
                    if (index + 1) == len(file.path_components):
                        #it's a file
                        #last elem
                        #create entry
                        branch = folder[base]
                        rec_index = 0
                        while rec_index < index:
                            branch["___size"] += file.size
                            if file.priority not in branch["___priority"]:
                                branch["___priority"] += [file.priority]
                            branch["___completion"] = int((float(branch["___completion"]) + file.percentage_complete) / 2)
                            branch = branch[file.path_components[rec_index]]
                            rec_index += 1
                        branch["___files"] += [random_id]
                        branch["___size"] += file.size
                        if file.priority not in branch["___priority"]:
                            branch["___priority"] += [file.priority]
                        branch["___completion"] = int((float(branch["___completion"]) + file.percentage_complete) / 2)
                    else:
                        #it's a dir
                        #count index up
                        rec_index = 0
                        branch = folder[base]
                        while rec_index <= index:
                            if file.path_components[rec_index] not in branch.keys():
                                #create folder entry
                                branch[file.path_components[rec_index]] = {
                                    "___files" : [],
                                    "___size" : 0,
                                    "___priority" : [],
                                    "___completion" : 0,
                                }
                            branch = branch[file.path_components[rec_index]]
                            rec_index += 1
                            
        return (folder, files_dict)

    def fileTreeHTML(self, fileList, RTROOT):
        """
            Takes a list of files as outputted by rtorrent.getFiles and parses it into an html file tree
            Requires the rtorrent root directory
            File attributes:
                abs_path, base_path, path_components, completed_chunks, priority, size, chunks, chunk___size
        """

        DOCUMENT_DIV = """
            <li><span class="file %s">%s</span></li>
        """

        DIRECTORY_DIV = """
            <li><span class="folder">%s</span><ul>
        """
        
        HIDDEN = " style=\"display:none;\""
        
        LEVEL = 0
        
        def _getFiles(level):
            html = ""
            for file in level["___files"]:
                # html += DOCUMENT_DIV % (HIDDEN, os.path.basename(fileDict[file].abs_path), self.humanSize(fileDict[file].size))
                fileName = os.path.basename(fileDict[file].abs_path)
                html += DOCUMENT_DIV % (_getFileType(fileName), fileName)
            return html
            
        def _getDirs(level):
            level_keys = []
            for _key in level.keys():
                if _key[0:3] != "___":
                    level_keys += [_key]
            level_keys.sort()
            html = ""
            for subDirName in level_keys:
                subLevel = level[subDirName]
                # html += DIRECTORY_DIV % (HIDDEN, subDirName, self.humanSize(subLevel["___size"]))
                html += DIRECTORY_DIV % (subDirName)
                html += _getDirs(subLevel)
                html += _getFiles(subLevel)
                html += "</ul></li>"
            return html
            
        def _getFileType(fileName):
            fileType = "file_unknown"
            if fileName.lower().endswith(".avi") or fileName.lower().endswith(".mkv"):
                fileType = "file_video"
            elif fileName.lower().endswith(".rar"):
                fileType = "file_archive"
            elif "." in fileName and re.match("r\d+", fileName.lower().split(".")[-1]):
                fileType = "file_archive"
            elif fileName.lower().endswith(".nfo") or fileName.lower().endswith(".txt"):
                fileType = "file_document"
            elif fileName.lower().endswith(".iso"):
                fileType = "file_disk"
            elif "." in fileName and fileName.lower().split(".")[-1] in ["mp3", "aac", "flac", "m4a", "ogg"]:
                fileType = "file_music"
            return fileType
                
        fileStruct, fileDict = self.getFileStructure(fileList, RTROOT)
        root_keys = fileStruct.keys()
        root_keys.sort()
        if root_keys[0] == ".":
            fileObj = fileDict[fileStruct["."]["___files"][0]]
            fileName = os.path.basename(fileObj.abs_path)
            return """
                <ul id="files_list" class="filetree">
                    %s
                </ul>
                """ % (DOCUMENT_DIV % (_getFileType(fileName), fileName))
                # % (DOCUMENT_DIV % ("", os.path.basename(fileObj.abs_path), self.humanSize(fileObj.size)))
        else:
            #walk through dictionary
            #should only ever be one root_key, "." or the base directory
            html = "<ul id=\"files_list\" class=\"filetree\">"
            root = fileStruct[root_keys[0]]
            #html += DIRECTORY_DIV % ("", root_keys[0], self.humanSize(root["___size"]))
            html += DIRECTORY_DIV % (root_keys[0])
            html += _getDirs(root)
            html += _getFiles(root)
            html += "</ul></li></ul>"
            return html
            
    def fileTreeHTML2(self, fileList, RTROOT):
        """
            Takes a list of files as outputted by rtorrent.getFiles and parses it into an html file tree
            Requires the rtorrent root directory
            File attributes:
                abs_path, base_path, path_components, completed_chunks, priority, size, chunks, chunk___size
        """
        DOCUMENT_DIV = """
            <div class="document"%s>
                <img alt="Document" src="/images/document.png" class="file_img">
                <span class="document_name">%s</span> 
                <span class="directory_size">%s</span>
            </div>
        """
        DIRECTORY_DIV = """
            <div class="directory"%s>
                <img alt="Show Contents" title="Show Contents" onclick="event.cancelBubble = true; show_contents(this.parentNode);" src="/images/folder.png" class="file_img" style="cursor:pointer;">
                <span class="directory_name">%s</span>
                <span class="directory_size">%s</span>
        """
        
        HIDDEN = " style=\"display:none;\""
        
        def _getFiles(level):
            html = ""
            for file in level["___files"]:
                html += DOCUMENT_DIV % (HIDDEN, os.path.basename(fileDict[file].abs_path), self.humanSize(fileDict[file].size))
            return html
            
        def _getDirs(level):
            level_keys = []
            for _key in level.keys():
                if _key[0:3] != "___":
                    level_keys += [_key]
            level_keys.sort()
            html = ""
            for subDirName in level_keys:
                subLevel = level[subDirName]
                html += DIRECTORY_DIV % (HIDDEN, subDirName, self.humanSize(subLevel["___size"]))
                html += _getDirs(subLevel)
                html += _getFiles(subLevel)
                html += "</div>"
            return html
                
        fileStruct, fileDict = self.getFileStructure(fileList, RTROOT)
        root_keys = fileStruct.keys()
        root_keys.sort()
        if root_keys[0] == ".":
            fileObj = fileDict[fileStruct["."]["___files"][0]]
            
            return """
                <div id="files_list">
                    %s
                </div>
                """ % (DOCUMENT_DIV % ("", os.path.basename(fileObj.abs_path), self.humanSize(fileObj.size)))
        else:
            #walk through dictionary
            #should only ever be one root_key, "." or the base directory
            html = "<div id=\"files_list\">"
            root = fileStruct[root_keys[0]]
            html = "<div id=\"files_list\">"
            html += DIRECTORY_DIV % ("", root_keys[0], self.humanSize(root["___size"]))
            html += _getDirs(root)
            html += _getFiles(root)
            html += "</div></div>"
            return html
        
    def torrentHTML(self, torrentList, sort, view, reverse=False):
        """
            Sorts a list of torrent_ids with default information
            Arguments:
                torrentList = list : rtorrent.Torrent objects
                sort = str : value to sort on
                reverse = boolean : reverse or not
            Sort Options:
                name
                size
                ratio
                uprate
                uptotal
                downrate
                downtotal
                leechs              #shorthand for leechs_connected
                leechs_connected
                leechs_total
                seeds               #shorthand for seeds_connected
                seeds_connected
                seeds_total
                peers               #shorthand for peers_connected
                peers_connected
                peers_total
                priority
                status
                tracker
                created
        """
        self.SORT_METHODS = ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status", "tracker","created"]
        if sort not in ["name","size","ratio","uprate","uptotal","downrate","downtotal",
                        "leechs","leechs_connected","leechs_total","seeds",
                        "seeds_connected","seeds_total", "peers","peers_connected",
                        "peers_total","priority","status","tracker","created"]:
            sort = None

        if not sort:
            torrentList.reverse()
        elif sort == "name":
            torrentList = sorted(torrentList, key=lambda x:x.name)
        elif sort == "size":
            torrentList = sorted(torrentList, key=lambda x:x.size)
        elif sort == "ratio":
            torrentList = sorted(torrentList, key=lambda x:x.ratio)
        elif sort == "uprate":
            torrentList = sorted(torrentList, key=lambda x:x.up_rate)
            torrentList.reverse()
        elif sort == "downrate":
            torrentList = sorted(torrentList, key=lambda x:x.down_rate)
        elif sort == "uptotal":
            torrentList = sorted(torrentList, key=lambda x:x.up_total)
        elif sort == "downtotal":
            torrentList = sorted(torrentList, key=lambda x:x.down_total)
        elif sort == "leechs" or sort == "leechs_connected":
            torrentList = sorted(torrentList, key=lambda x:x.peers_connected)
        elif sort == "leechs_total":
            torrentList = sorted(torrentList, key=lambda x:x.peers_total)
        elif sort == "seeds" or sort == "seeds_connected":
            torrentList = sorted(torrentList, key=lambda x:x.seeds_connected)
        elif sort == "seeds_total":
            torrentList = sorted(torrentList, key=lambda x:x.seeds_total)
        elif sort == "peers" or sort == "peers_connected":
            torrentList = sorted(torrentList, key=lambda x:x.peers_connected + x.seeds_connected)
        elif sort == "peers_total":
            torrentList = sorted(torrentList, key=lambda x:x.peers_total + x.seeds_total)
        elif sort == "priority":
            torrentList = sorted(torrentList, key=lambda x:x.priority)
        elif sort == "status":
            torrentList = sorted(torrentList, key=lambda x:x.status)
        elif sort == "tracker":
            #sort by the first listed tracker only
            torrentList = sorted(torrentList, key=lambda x:x.trackers[0].url)
        elif sort == "created":
            torrentList = sorted(torrentList, key=lambda x:x.created)
      
        if reverse:
            torrentList.reverse()

        sorts = {
            "name":"",
            "namesort" : "none",
            "size":"",
            "sizesort" : "none",
            "ratio":"",
            "ratiosort" : "none",
            "uprate" : "",
            "upratesort" : "none",
            "downrate" : "",
            "downratesort" : "none",
            "status" : "",
            "statussort" : "none",
        }
        for type in sorts.keys():
            if type in self.SORT_METHODS:
                sorts[type] = "?view=%s&amp;sortby=%s" % (view, type)
                if type == sort and not reverse:
                    sorts[type] += "&amp;reverse=1"
        if sort in sorts.keys():
            if reverse:
                sorts[sort + "sort"] = "down"
            else:
                sorts[sort + "sort"] = "up"
                    
        
        torrent_html = """
            <table id='torrent_list'>
                <tr>
                    <td class='heading' id="sortby_name" onclick="window.location='%(name)s';">Name <img alt="Sort By Name" src="../images/sort_%(namesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby___size" onclick="window.location='%(size)s';">Size <img alt="Sort By Size" src="../images/sort_%(sizesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_ratio" onclick="window.location='%(ratio)s';">Ratio <img alt="Sort By Ratio" src="../images/sort_%(ratiosort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_uprate" onclick="window.location='%(uprate)s';">Upload speed <img alt="Sort By Upload Speed" src="../images/sort_%(upratesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_downrate" onclick="window.location='%(downrate)s';">Download speed <img alt="Sort By Download Speed" src="../images/sort_%(downratesort)s.gif" class="control_button"></td>
                    <td class='heading' id="sortby_status" onclick="window.location='%(status)s';">Status <img alt="Sort By Status" src="../images/sort_%(statussort)s.gif" class="control_button"></td>
                    <td class='heading'></td>
                </tr>
            """ % sorts
        torrent_html += "<!-- %r -->" % sorts
            
        div_colour_array = ["blue", "green"]
        
        for t in torrentList:
            colour = div_colour_array.pop(0)
            div_colour_array += [colour]
            status = self.getState(t)
            if status == "Stopped" or status == "Paused":
                stopstart = "<span class='control_start control_button' title='Start Torrent'><img onclick='event.cancelBubble = true; command(\"start_torrent\",\"%s\")' class='control_image' alt='Start' src='../images/start.png'></span>" % t.torrent_id
                stoporstart = "rcstart"
            else:
                stopstart = "<span class='control_pause control_button' title='Pause Torrent'><img onclick='event.cancelBubble = true; command(\"pause_torrent\",\"%s\")'class='control_image' alt='Pause' src='../images/pause.png'></span>" % t.torrent_id
                stoporstart = "rcpause"
                
            torrent_html += """
                <tr onmouseover='select_torrent(this);' 
                    onmouseout='deselect_torrent(this);' 
                    onclick='view_torrent(this);'
                    ondblclick='navigate_torrent(this);'
                    class='torrent-div %(colour)s %(stoporstart)s' 
                    id='torrent_id_%(t_id)s'>
                    <td>%(t_name)s</td>
                    <td>%(t___size)s</td>
                    <td title='%(t_uploaded)s up / %(t_downloaded)s down'>%(t_ratio).02f</td>
                    <td>%(t_uprate)s/s</td>
                    <td>%(t_downrate)s/s</td>
                    <td>%(t_status)s</td>
                    <td>
                        %(control_startpause)s
                        <span class='control_stop control_button' title='Stop Torrent'>
                            <img onclick='event.cancelBubble = true; command(\"stop_torrent\",\"%(t_id)s\")'
                                 class='control_image' alt='Stop' src='../images/stop.png'>
                        </span>
                        <span class='control_remove control_button' title='Remove Torrent'>
                            <img onclick='event.cancelBubble = true; command(\"remove_torrent\",\"%(t_id)s\")'
                                 class='control_image' alt='Remove' src='../images/remove.png'>
                        </span>
                        <span class='control_delete control_button' title='Remove Torrent and Files'>
                            <img onclick='event.cancelBubble = true; command(\"delete_torrent\",\"%(t_id)s\")'
                                 class='control_image' alt='Delete' src='../images/delete.png'>
                        </span>
                    </td>
                </tr>
                        """ % {
                            "colour" : colour,
                            "t_id" : t.torrent_id,
                            "t_name" : t.name,
                            "t___size" : self.humanSize(t.size),
                            "t_uploaded" : self.humanSize(t.up_total),
                            "t_downloaded" : self.humanSize(t.down_total),
                            "t_ratio" : float(t.ratio)/1000,
                            "t_uprate" : self.humanSize(t.up_rate),
                            "t_downrate" : self.humanSize(t.down_rate),
                            "t_status" : status,
                            "control_startpause" : stopstart,
                            "stoporstart" : stoporstart,
                        }
        torrent_html += "\n             </table>"

        html = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <!-- HEAD PLACEHOLDER -->
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>rTorrent - webUI</title>
        <link rel="stylesheet" type="text/css" href="/css/main.css">
        <script src="/javascript/jquery-1.6.1.min.js" type="text/javascript"></script>
        <script src="/javascript/jquery.contextmenu.r2.js" type="text/javascript"></script>
        <script src="/javascript/main.js" type="text/javascript"></script>
    </head>
    <body>
        <!-- BODY PLACEHOLDER -->
        <div id="torrent_table">
            %s
        </div>
        <div class="contextMenu" id="right_click_start">
            <ul>
                <li id="start"><img alt="start" src="/images/start.png"> Start</li>
                <li id="stop"><img alt="stop" src="/images/stop.png"> Stop</li>
                <li id="remove"><img alt="remove" src="/images/remove.png"> Remove and <strong>keep</strong> files</li>
                <li id="delete"><img alt="delete" src="/images/delete.png"> Remove and <strong>delete</strong> files</li>
                <li id="rehash"><img alt="rehash" src="/images/hash.png"> Rehash</li>
            </ul>
        </div>
        <div class="contextMenu" id="right_click_pause">
            <ul>
                <li id="pause"><img alt="pause" src="/images/pause.png"> Pause</li>
                <li id="stop"><img alt="stop" src="/images/stop.png"> Stop</li>
                <li id="remove"><img alt="remove" src="/images/remove.png"> Remove and <strong>keep</strong> files</li>
                <li id="delete"><img alt="delete" src="/images/delete.png"> Remove and <strong>delete</strong> files</li>
                <li id="rehash"><img alt="rehash" src="/images/hash.png"> Rehash</li>
            </ul>
        </div>
    </body>
</html>
        """ % (torrent_html)
        return html
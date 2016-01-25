#!/usr/bin/env python

""" Copyright (C) 2012 mountainpenguin (pinguino.de.montana@googlemail.com)
    <http://github.com/mountainpenguin/pyrt>

    This file is part of pyRT.

    pyRT is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyRT is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyRT.  If not, see <http://www.gnu.org/licenses/>.
"""

import random
import string
import os
import re


SORT_METHODS = [
    "name", "size", "ratio", "uprate", "uptotal", "downrate", "downtotal",
    "leechs", "leechs_connected", "leechs_total", "seeds",
    "seeds_connected", "seeds_total",  "peers", "peers_connected",
    "peers_total", "priority", "status",  "tracker", "created"
]


class fileTreeDir(object):
    def __init__(self, name):
        self.ft_type = 1
        self.name = name

    def __repr__(self):
        return "DIR<{0}>".format(self.name)


class fileTreeDoc(object):
    def __init__(self, file_type, name, allowed, fullpath):
        self.ft_type = 2
        self.file_type = file_type
        self.name = name
        self.allowed = allowed,
        self.fullpath = fullpath

    def __repr__(self):
        return "DOC<{0}>".format(self.name)


class fileTreeDirEnd:
    def __init__(self):
        self.ft_type = 3

    def __repr__(self):
        return "DIREND"


def humanTimeDiff(secs):
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


def humanSize(bytes):
    """
        takes a int/float value of <bytes>
        returns a string of <bytes> in a human readable unit (with two decimal places)
        (currently supports TB, GB, MB, KB and B)
    """
    if bytes >= 1024*1024*1024*1024:
        return "%.02f TB" % (float(bytes) / 1024 / 1024 / 1024 / 1024)
    elif bytes >= 1024*1024*1024:
        return "%.02f GB" % (float(bytes) / 1024 / 1024 / 1024)
    elif bytes >= 1024*1024:
        return "%.02f MB" % (float(bytes) / 1024 / 1024)
    elif bytes >= 1024:
        return "%.02f KB" % (float(bytes) / 1024)
    else:
        return "%i B" % bytes


def getState(t):
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


def HTMLredirect(url, refresh=0, body=""):
    return """
    <!DOCTYPE HTML>
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


def getFileStructure(files, rtorrent_root):
    folder = {}
    files_dict = {}
    for file in files:
        random_id = "".join([random.choice(string.letters + string.digits) for i in range(10)])
        files_dict[random_id] = file
        if file.base_path == rtorrent_root:
            folder["."] = {"___files": [random_id]}
            break
        else:
            if os.path.basename(file.base_path) not in folder.keys():
                # create folder entry
                folder[os.path.basename(file.base_path)] = {
                    "___files": [],
                    "___size": 0,
                    "___priority": [file.priority],
                    "___completion": 0,
                }

            for index in range(len(file.path_components)):
                base = os.path.basename(file.base_path)
                if (index + 1) == len(file.path_components):
                    # it's a file
                    # last elem
                    # create entry
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
                    # it's a dir
                    # count index up
                    rec_index = 0
                    branch = folder[base]
                    while rec_index <= index:
                        if file.path_components[rec_index] not in branch.keys():
                            # create folder entry
                            branch[file.path_components[rec_index]] = {
                                "___files": [],
                                "___size": 0,
                                "___priority": [],
                                "___completion": 0,
                            }
                        branch = branch[file.path_components[rec_index]]
                        rec_index += 1

    return (folder, files_dict)


def fileTree(fileList, RTROOT):
    """
        Takes a list of files as outputted by rtorrent.getFiles and parses it into an html file tree
        Requires the rtorrent root directory
        File attributes:
            abs_path, base_path, path_components, completed_chunks, priority, size, chunks, chunk_size, percentage_complete
    """

    def _getFiles(level):
        output = []
        files = sorted(level["___files"], key=lambda x: os.path.basename(fileDict[x].abs_path))

        for file in files:
            fileName = os.path.basename(fileDict[file].abs_path)
            fileProgress = fileDict[file].percentage_complete
            if fileProgress == 100:
                allowed = True
            else:
                allowed = False

            output.append(
                fileTreeDoc(
                    file_type=_getFileType(fileName),
                    name=fileName,
                    allowed=allowed,
                    fullpath=fileDict[file].abs_path
                )
            )

        return output

    def _getDirs(level):
        level_keys = []
        for _key in level.keys():
            if _key[0:3] != "___":
                level_keys += [_key]
        level_keys.sort()
        output = []
        for subDirName in level_keys:
            subLevel = level[subDirName]
            output.append(fileTreeDir(subDirName))
            output += _getDirs(subLevel)
            output += _getFiles(subLevel)
            output.append(fileTreeDirEnd())
        return output

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

    fileStruct, fileDict = getFileStructure(fileList, RTROOT)
    root_keys = fileStruct.keys()
    root_keys.sort()
    if root_keys[0] == ".":
        fileObj = fileDict[fileStruct["."]["___files"][0]]
        fileName = os.path.basename(fileObj.abs_path)
        fileProgress = fileObj.percentage_complete
        if fileProgress == 100:
            # insert download icon
            allowed = True
        else:
            allowed = False
        output = [fileTreeDoc(
            file_type=_getFileType(fileName),
            name=fileName,
            allowed=allowed,
            fullpath=fileObj.abs_path,
        )]
    else:
        # walk through dictionary
        # should only ever be one root_key, "." or the base directory
        root = fileStruct[root_keys[0]]
        output = [fileTreeDir(root_keys[0])]
        output += _getDirs(root)
        output += _getFiles(root)
        output.append(fileTreeDirEnd())
    return output


def sortTorrents(torrentList, sort=None, reverse=False):
    if sort not in SORT_METHODS:
        sort = None

    special_methods = {
        "uprate": {"key": lambda x: x.up_rate, "reverse": True},
        "downrate": {"key": lambda x: x.down_rate, "reverse": True},
        "uptotal": {"key": lambda x: x.up_total},
        "downtotal": {"key": lambda x: x.down_total},
        "leechs": {"key": lambda x: x.peers_connected},
        "leechs_connected": {"key": lambda x: x.peers_connected},
        "leechs_total": {"key": lambda x: x.peers_total},
        "seeds": {"key": lambda x: x.seeds_connected},
        "peers": {"key": lambda x: x.peers_connected + x.seeds_connected},
        "peers_connected": {"key": lambda x: x.peers_connected + x.seeds_connected},
        "peers_total": {"key": lambda x: x.peers_total + x.seeds_total},
        "tracker": {"key": lambda x: x.trackers[0].url},
    }
    if not sort:
        torrentList.reverse()
    elif sort in special_methods:
        torrentList = sorted(torrentList, **special_methods[sort])
    else:
        torrentList = sorted(torrentList, key=lambda x: x.__dict__[sort])

    if reverse:
        torrentList.reverse()

    return torrentList


def process_list(torrentList):
    for t in torrentList:
        t.t_size = humanSize(t.size)
        t.t_uploaded = humanSize(t.up_total)
        t.t_downloaded = humanSize(t.down_total)
        t.t_ratio = "%.02f" % (float(t.ratio)/1000)
        t.t_uprate = humanSize(t.up_rate)
        t.t_downrate = humanSize(t.down_rate)
        t.t_percentage = int((float(t.completed_bytes) / t.size) * 100)
        if t.status == "Active":
            if t.completed_bytes == t.size:
                if t.peers_connected > 0:
                    t.status = "Seeding"
                elif t.peers_connected == 0:
                    t.status = "Seeding (idle)"
            elif t.completed_bytes != t.size:
                if t.seeds_connected > 0 or t.peers_connected > 0:
                    t.status = "Leeching"
                elif t.seeds_connected == 0 and t.peers_connected == 0:
                    t.status = "Leeching (idle)"

    return torrentList
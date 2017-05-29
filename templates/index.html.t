<html>
    <head>
        <title>Liste HFR Steam</title>
        <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script src="jquery.watable.js"></script>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"/>
        <link href="watable.css" rel="stylesheet"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .watable input[type=text].filter {
                width: 100%;
                font-style: italic;
            }
            h1 {
                margin-bottom: 0em;
            }
            h6 {
                font-size: 0.7em;
                margin-top: 0em;
            }
            .main {
                margin-top: 0em;
                margin-bottom: 0em;
                margin-left: 0.5em;
                margin-right: 0.5em;
            }
        </style>
    </head>
    <body>
        <div class="main">
            <div>
                <h1>Liste HFR Steam</h1>
                <h6>Mise à jour le $DATE$</h6>
                <a href="https://github.com/John-Gee/HFRSteam">
                    <img style="position: absolute; top: 0; right: 0; border: 0; max-width: 75px;" src="https://camo.githubusercontent.com/365986a132ccd6a44c23a9169022c0b5c890c387/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f7265645f6161303030302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png">
                </a>

                <form>
                    <input type="text" name="library" id="libraryId" placeholder="https://steamcommunity.com/id/PROFILE" size="34"/>

                    <button type="button" id="myButton">Load Steam Profile</button>
                </form>
            </div>
            <div id="wata" style="width:auto"></div>
            <script type="text/javascript">
                $(document).ready(function(){
                $('input').on('keydown', function(event) {
                    // change enter key behavior
                    if (event.which == 13) {
                        event.preventDefault()
                        $("#myButton").click();
                    }
                });

                $('button').click(function(){
                    var profile = "https://cors-anywhere.herokuapp.com/" + document.getElementById('libraryId').value;
                    if (!profile || /^\s*$/.test(profile))
                        return;

                    // library
                    var library = profile + "/games/?tab=all";
                    $.get(library, function(page) {
                        var divclass = "<div class=\"profile_small_header_bg\">";
                        var beginning = "var rgGames = ";
                        var subpage = page.substring(page.indexOf(divclass));
                        subpage = subpage.substring(subpage.indexOf(beginning) + beginning.length);
                        subpage = subpage.substring(0, subpage.indexOf(";"));
                        var libraryURLs = {};
                        try {
                            var games = jQuery.parseJSON(subpage);
                            var i;
                            var GAMEURL = "http://store.steampowered.com/app/";
                            for (i = 0 ; i < games.length; ++i) {
                                libraryURLs[GAMEURL + games[i].appid] = true;
                            }
                        }
                        catch (e) {
                        }

                        // wishlist
                        var wishlist = profile + "/wishlist/";
                        $.get(wishlist, function(page) {
                            var body = '<div id="body-mock">' + page.replace(/^[\s\S]*<body.*?>|<\/body>[\s\S]*$/ig, '') + '</div>';
                            var data = $(body);
                            var wishlistURLs = {};
                            var games = data.find(".storepage_btn_ctn");
                            var i;
                            for (i = 0; i < games.length; ++i) {
                                var href = games[i].innerHTML.substring(games[i].innerHTML.indexOf("\"") + 1);
                                wishlistURLs[href.substring(0, href.indexOf("\""))] = true;
                            }

                            var data = waTable.getData();
                            // change the rows
                            for (i = 0; i < data.rows.length; ++i) {
                                if (data.rows[i]["nameFormat"]) {
                                    var href = data.rows[i]["nameFormat"];
                                    href = href.substring(href.indexOf("\"") + 1);
                                    href = href.substring(0, href.indexOf("\""));

                                    if (href in libraryURLs) {
                                        data.rows[i]["row-cls"] = "green";
                                        data.rows[i]["store"] = "Library";
                                    }

                                    else if (href in wishlistURLs) {
                                        data.rows[i]["row-cls"] = "blue";
                                        data.rows[i]["store"] = "Wishlist";
                                    }

                                    else {
                                        data.rows[i]["row-cls"] = "";
                                        data.rows[i]["store"] = "";
                                    }
                                }
                            }
                            Platform.performMicrotaskCheckpoint();
                            waTable.setData(data);
                        });
                    });
                });
            });

            var waTable = $('#wata').WATable({
                    debug: false,
                    databind: true,
                    filter: true,
                    sorting: true,
                    sortEmptyLast: true,
                    columnPicker: true,
                    pageSize: $.isNumeric(localStorage.getItem("pageSize")) ? localStorage.getItem("pageSize") : 10,
                    hidePagerOnEmpty: true,
                    types: {
                        string: {
                            placeHolder: "filter"
                        },
                    },
                    data: getData(),
                }).data('WATable');
                
                function getData() {
                    var cols = {
                        name: {
                            index: 1,
                            type: "string",
                            friendly: "Name",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: true,
                            sortOrder: "asc",
                            filter: "",
                            hidden: localStorage.getItem("Name") ? !("true" == localStorage.getItem("Name")) : false,
                        },
                        description: {
                            index: 2,
                            type: "string",
                            friendly: "Description",
                            format: "<div style=\"white-space: normal; text-indent:1em; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: true,
                            filter: "",
                            sorting: false,
                            hidden: localStorage.getItem("Description") ? !("true" == localStorage.getItem("Description")) : false,
                        },
                        category: {
                            index: 3,
                            type: "string",
                            friendly: "Type",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Type") ? !("true" == localStorage.getItem("Type")) : false,
                        },
                        os: {
                            index: 4,
                            type: "string",
                            friendly: "OS",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("OS") ? !("true" == localStorage.getItem("OS")) : false,
                        },
                        price: {
                            index: 5,
                            type: "number",
                            decimals: 2,
                            friendly: "Price",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Price") ? !("true" == localStorage.getItem("Price")) : false,
                        },
                        genres: {
                            index: 6,
                            type: "string",
                            friendly: "Genres",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Genres") ? !("true" == localStorage.getItem("Genres")) : false,
                        },
                        date: {
                            index: 7,
                            type: "string",
                            friendly: "Release Date",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Release Date") ? !("true" == localStorage.getItem("Release Date")) : false,
                        },
                        review: {
                            index: 8,
                            type: "string",
                            friendly: "Reviews",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Reviews") ? !("true" == localStorage.getItem("Reviews")) : false,
                        },
                        requirements: {
                            index: 9,
                            type: "string",
                            friendly: "List",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Requirements") ? !("true" == localStorage.getItem("Requirements")) : false,
                        },
                        store: {
                            index: 10,
                            type: "string",
                            friendly: "Store",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Store") ? !("true" == localStorage.getItem("Store")) : false,
                        },
                        tags: {
                            index: 100,
                            type: "string",
                            friendly: "Tags",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Tags") ? !("true" == localStorage.getItem("Tags")) : true,
                        },
                        details: {
                            index: 101,
                            type: "string",
                            friendly: "Details",
                            format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                            unique: false,
                            filter: "",
                            hidden: localStorage.getItem("Details") ? !("true" == localStorage.getItem("Details")) : true,
                        },
                    };
                    
                    var rows = [];

    $TEMPLATE$

                    var data = {
                        cols: cols,
                        rows: rows,
                    };
                    
                    return data;
                }
                $(document).on('click', 'a', '.btn-group.dropup.pagesize', function(e){
                    var val = $(this).text().toLowerCase();
                    localStorage.setItem("pageSize", val);
                });
                $(document).on('hidden.bs.dropdown', '.btn-group.dropup.columnpicker', function(e){
                    var elem = $(this);
                    var ul = elem[0].childNodes[1];
                    var items = ul.getElementsByTagName("li");
                    for (var i = 0; i < items.length; ++i) {
                        name = items[i].textContent.trim();
                        checked = items[i].getElementsByTagName("input")[0].checked;
                        localStorage.setItem(name, checked);
                    }
                });
            </script>
        </div>
    </body>
</html>

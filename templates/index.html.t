<html>
    <head>
        <title>Liste HFR Steam</title>
        <script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script src="jquery.watable.js"></script>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"/>
        <link href="watable.css" rel="stylesheet"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            .watable input[type=text].filter{
                width: 100%;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div>
            <h1>Liste HFR Steam</h1>
            <h6>(Mise à jour le $DATE$)</h6>
            <a href="https://github.com/John-Gee/HFRSteam">
                <img style="position: absolute; top: 0; right: 0; border: 0; max-width: 75px;" src="https://camo.githubusercontent.com/365986a132ccd6a44c23a9169022c0b5c890c387/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f7265645f6161303030302e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_red_aa0000.png">
                </a>
        </div>
        <div id="wata" style="width:auto"></div>
        <script type="text/javascript">
            $('#wata').WATable({
                debug: false,
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
                    new: {
                        index: 9,
                        type: "bool",
                        friendly: "New",
                        unique: false,
                        filter: "",
                        hidden: localStorage.getItem("New") ? !("true" == localStorage.getItem("New")) : false,
                    },
                    premium: {
                        index: 10,
                        type: "bool",
                        friendly: "Premium",
                        unique: false,
                        filter: "",
                        hidden: localStorage.getItem("Premium") ? !("true" == localStorage.getItem("Premium")) : false,
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
    </body>
</html>

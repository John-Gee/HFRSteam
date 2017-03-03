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
                pageSize: 10,
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
                        tooltip: "The game's name",
                        filter: "",
                    },
                    description: {
                        index: 2,
                        type: "string",
                        friendly: "Description",
                        format: "<div style=\"white-space: normal; text-indent:1em; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: true,
                        tooltip: "The game's description",
                        filter: "",
                        sorting: false,
                    },
                    dlc: {
                        index: 3,
                        type: "bool",
                        friendly: "DLC?",
                        unique: false,
                        tooltip: "Is this a DLC?",
                        filter: "",
                    },
                    os: {
                        index: 4,
                        type: "string",
                        friendly: "Supported OS?",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "Supported OS",
                        filter: "",
                    },
                    price: {
                        index: 5,
                        type: "number",
                        decimals: 2,
                        friendly: "Price",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "The game's price and its retrieved date",
                        filter: "",
                    },
                    genres: {
                        index: 6,
                        type: "string",
                        friendly: "Genres",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "The game's genres",
                        filter: "",
                    },
                    date: {
                        index: 7,
                        type: "string",
                        friendly: "Release Date",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "The game's release date",
                        filter: "",
                    },
                    review: {
                        index: 8,
                        type: "string",
                        friendly: "Reviews",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "The game's average review and the review count",
                        filter: "",
                    },
                    new: {
                        index: 9,
                        type: "bool",
                        friendly: "New?",
                        unique: false,
                        tooltip: "Is this a new game?",
                        filter: "",
                    },
                    tags: {
                        index: 10,
                        type: "string",
                        friendly: "Tags",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "The game's tags",
                        filter: "",
                        hidden: true,
                    },
                    details: {
                        index: 11,
                        type: "string",
                        friendly: "Details",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: false,
                        tooltip: "The game's details",
                        filter: "",
                        hidden: true,
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
        </script>
    </body>
</html>

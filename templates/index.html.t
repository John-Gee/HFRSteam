<html>
    <head>
        <title>HFR Steam List</title>
        <script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
        <script src="jquery.watable.js"></script>
        <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"/>
        <link href="watable.css" rel="stylesheet"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>HFR Steam List</h1>
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
                        placeHolder: ""
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
                        unique: "true",
                        sortOrder: "asc",
                        tooltip: "The game's name",
                        filter: "",
                    },
                    description: {
                        index: 2,
                        type: "string",
                        friendly: "Description",
                        format: "<div style=\"white-space: normal; text-indent:1em; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: "true",
                        tooltip: "The game's description",
                        filter: "",
                    },
                    dlc: {
                        index: 3,
                        type: "bool",
                        friendly: "DLC?",
                        unique: "false",
                        tooltip: "Is this a DLC?",
                        filter: "",
                    },
                    os: {
                        index: 4,
                        type: "string",
                        friendly: "Supported OS?",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: "false",
                        tooltip: "Supported OS",
                        filter: "",
                    },
                    price: {
                        index: 5,
                        type: "number",
                        decimals: 2,
                        friendly: "Price",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: "false",
                        tooltip: "The game's price and its retrieved date",
                        filter: "",
                    },
                    genres: {
                        index: 6,
                        type: "string",
                        friendly: "Genres",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: "false",
                        tooltip: "The game's genres",
                        filter: "",
                    },
                    date: {
                        index: 7,
                        type: "string",
                        friendly: "Release Date",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: "false",
                        tooltip: "The game's release date",
                        filter: "",
                    },
                    review: {
                        index: 8,
                        type: "string",
                        friendly: "Reviews",
                        format: "<div style=\"white-space: normal; text-align: justify; text-justify: inter-word; line-height: 150%\">{0}</div>",
                        unique: "false",
                        tooltip: "The game's average review and the review count",
                        filter: "",
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

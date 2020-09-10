html = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>{{title}}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    </head>
    <body>
    <redoc spec-url='/docs/openapi.json'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"> </script>
    </body>
    </html>
    """

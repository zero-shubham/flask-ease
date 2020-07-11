html = """
<!DOCTYPE html>
<html>
  <head>
    <link
      type="text/css"
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css"
    />
    <link
      rel="shortcut icon"
      href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.26.2/favicon-16x16.png"
    />
    <title>{{title}}</title>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
      const ui = SwaggerUIBundle({
        url: '/docs/openapi.json',
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset,
        ],
        layout: 'BaseLayout',
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
      });
    </script>
  </body>
</html>
"""

<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css"></link>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.js"></script>
    </head>
    <body>
        <div class="ui container" style="padding-top: 10px;">
            <table class="ui celled table">
                <thead>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Complexity</th>
                </thead>
                <tbody>
                    %for row in rows:
                    <tr>
                        <td><a href="{{ row.url }}">{{ row.title }}</a></td>
                        <td>{{ row.author }}</td>
                        <td>{{ row.complexity }}</td>
                    </tr>
                    %end
                </tbody>
            </table>
        </div>
    </body>
</html>

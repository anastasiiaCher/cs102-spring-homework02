<!DOCTYPE html>
<html>

<head>
    <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css">
    </link>
</head>

<body>
    <div class="ui container" style="padding-top: 10px;">
        <table class="ui celled table">
            <thead>
                <th>Title</th>
                <th>Author</th>
                <th>Complexity</th>
                <th>Label (predict)</th>
            </thead>
            <tbody>
                %for row, label in rows:
                <tr>
                    <td><a href="{{ row.url }}">{{ row.title }}</a></td>
                    <td>{{ row.author }}</td>
                    <td>{{ row.complexity }}</td>
                    <td>{{ label }}</td>
                </tr>
                %end
            </tbody>
        </table>
    </div>
</body>

</html>
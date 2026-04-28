# Micro Quiz Hub

## Introduction
This is a web server program, powered by Flask framework, you can use this server to publish exam or survey.

## Run
You can place your launch script at anywhere, just import package `main` in `src`, use Flask development server or your WSGI server.
```python
import main
main.app.run()
```

## Routes
| Route                                       | Method | Description                   |
| ---                                         | ---    | ---                           |
| /page/&lt;path:file&gt;                     | GET    | Get pages.                    |
| /quiz/&lt;quiz_id&gt;                       | GET    | Get quiz configuration.       |
| /paper/&lt;paper_id&gt;                     | GET    | Get paper configuration.      |
| /verify                                     | POST   | Verify token.                 |
| /submit                                     | POST   | Submit.                       |
| /attachment/&lt;path:file&gt;               | GET    | Get attachments.              |
| /result/&lt;quiz_id&gt;?token=&lt;token&gt; | GET    | Get result of quiz for token. |

## Static resource routes(/page, /asset, /attachment) response
If there is no exception, the resource itself is returned; if there is an exception, the exception information page is returned.

## Data routes(/quiz, /paper, /result) response
If there are no exceptions, return the JSON data itself; if there are exceptions, the returned JSON formatted data follows a general format as below:
```json
{
    "code": <status_code>,
    "message": "<Manual read message.>"
}
```
The value of the code field is equal to the HTTP status code.

## POST routes(/verify, /submit) response
All POST methods will return a JSON, general like:
```json
{
    "code": <status_code>,
    "message": "<Manual read message.>"
}
```
The defined values of status code are as follows:
- 0 - No error
- 1 - Token invalid
- 2 - Submitted (duplicate submissions are not allowed)
- 3 - Closed \
If an exception other than those defined above occurs, the value of the code field will be equal to the HTTP status code.

## Quiz configuration
```json
{
    "id": "<quiz_id>",
    "paper": "<paper_id>",
    "group": "<group_id>"/null,
    "deadline": <timestamp>/null,
    "allow_resubmit": <bool>
}
```

## Paper configuration
```json
{
    "id": "<paper_id>",
    "content": "<url>",
    "mime_type": "<mime_type>",
    "paper": [
        {
            "type": "single_selection/multiple_selection/single_line/multiple_line",
            "prompt": "<Prompt, like '[1]'.>",
            "option": ["A", "B", "<Option prompt, like 'C'>"]
        }
    ]
}
```

## Group configuration
```json
{
	"id":"<group_id>",
	"token":[
		"<token>"
	]
}
```
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
| Route                           | Method | Description                   |
| ---                             | ---    | ---                           |
| /page/<file>                    | GET    | Get pages.                    |
| /quiz/<quiz_id>                 | GET    | Get quiz configuration.       |
| /paper/<paper_id>               | GET    | Get paper configuration.      |
| /verify                         | POST   | Verify token.                 |
| /submit                         | POST   | Submit.                       |
| /attachment/<file>              | GET    | Get attachments.              |
| /result/<quiz_id>?token=<token> | GET    | Get result of quiz for token. |

## GET method return
All GET methods will return the original content of the corresponding resources.

## POST method return
All POST methods will return a JSON, general like:
```json
{
    "code": "<status_code>",
    "message": "<Manual read message.>"
}
```
The defined values of status code are as follows:
- 0 - No error
- 1 - Value invalid
- 2 - Submitted (duplicate submissions are not allowed)
- 3 - Closed

## Quiz configuration
```json
{
    "id": "<quiz_id>",
    "paper": "<paper_id>",
    "group": "<group_id>",
    "deadline": "<timestamp>/null",
    "allow_resubmit": "<bool>"
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
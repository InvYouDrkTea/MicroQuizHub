# Micro Quiz Hub

## Introduction
This is a web server program, powered by Flsk framwork, you can use this server to publish exam or survey.

## Run
You can place your launch script at anywhere, just import package `main` in `src`, use Flask development server or your WSGI server.
```python
import main
main.app.run()
```

## Routes
| Route                           | Method | Description                   |
| ---                             | ---    | ---                           |
| /page/<path:file>               | GET    | Get pages.                    |
| /quiz/<quiz_id>                 | GET    | Get quiz configuration.       |
| /paper/<paper_id>               | GET    | Get paper configuration.      |
| /token                          | POST   | Verify token.                 |
| /submit                         | POST   | Submit.                       |
| /attachment/<path:file>         | GET    | Get attachments.              |
| /answer/<quiz_id>?token=<token> | GET    | Get answer of quiz and token. |

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
- 0 - No error.
- 1 - Value invalid.
- 2 - Data unexpected.

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
    "answer": [
        {
            "type": "single_selection/multiple_selection/single_line/multiple_line",
            "prompt": "<Prompt, like '[1]'.>",
            "option": ["A", "B", "<Option prompt, like 'C'>"]
        }
    ]
}
```
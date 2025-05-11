import time
from collections.abc import Generator, Iterator
from typing import Any, Literal, overload

from mock_ai.schemas.chat_completion_request import ModelSettings
from mock_ai.schemas.completion_response import (
    ChatCompletionResponse,
    Delta,
    DeltaChoice,
    Message,
    MessageChoice,
    Usage,
)
from mock_ai.schemas.models_response import ModelInfo

from .chat_model import ChatModel

MD_TEXT = """
Here's a concise list of common Markdown formatting styles (in English), with examples:
1.	**Headings**

# H1
## H2
### H3
#### H4
##### H5
###### H6


2.	**Bold**

**bold text**


3.	**Italic**

*italic text*


4.	**Bold & Italic**

***bold and italic***


5.	**Strikethrough**

~~struck-through text~~


6.	**Blockquote**

> This is a blockquote.


7.	**Ordered List**

1. First item
2. Second item
3. Third item


8.	**Unordered List**

- Bullet point
- Another point
- Yet another


9.	**Task List**

- [ ] To do item
- [x] Completed item


10.	**Inline Code**

Use the `printf()` function.


11.	**Code Block**

```python
def hello():
    print("Hello, world!")
```

12.	**Horizontal Rule**

---


13.	**Link**

[Google](https://www.google.com)


14.	**Image**

![Alt text](https://picsum.photos/id/1/200/300)


15.	**Table**

| Header 1 | Header 2 |
| -------- | -------- |
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |


16.	**Footnote**

Here is a statement.[^1]

[^1]: This is the footnote text.


17.	**Emoji**

:smile:  :rocket:

"""
MD_IMAGE = """18. **Markdown Image**

![Alt text](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAcABwBAREA/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/APAACzBVBJJwAO9dnp/wm8damu6Dw5dRjGf9IKw/+hkVPffCnWNJa7XVNV0Kxa1hErrNe/M2cnYqgElsAHpjkc1wlAODkV694W8c654t8M6n4TuvEctrrFw0cun3c0/lq+3AMJcDK5AyOeTkd+fPvGFn4gsvEtzF4m89tUG1ZJJjuMgUBVYN/EMKOe9YVXtK0bUtdvVs9LsZ7y4YgbIULYycZPoPc8V6lpfwh0/w7p66z8RdXj0y2z8llC4aWQ+mRn8lz9RXPfE3x1pvi46TYaPZTQadpMJghluWDSyrhQM9SMBe5Oc5NcBV7Tda1XRZJJNK1O8sXkG12tZ2iLD0JUjNQ3l9eahN517dT3MvTfNIXb16n6mq9Ff/2Q==)
"""


class MarkdownChatModel(ChatModel):
    @property
    def key(self) -> str:
        return "markdown-chat-model"

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[False],
    ) -> ChatCompletionResponse[MessageChoice]: ...

    @overload
    def get_response(
        self,
        model_settings: ModelSettings,
        stream: Literal[True],
    ) -> Iterator[ChatCompletionResponse[DeltaChoice]]: ...

    def get_response(
        self,
        model_settings: ModelSettings,
        stream: bool,
    ) -> ChatCompletionResponse | Iterator[ChatCompletionResponse[DeltaChoice]]:
        if stream:

            def stream_response() -> Generator[
                ChatCompletionResponse[DeltaChoice], Any, None
            ]:
                for i in range(0, len(MD_TEXT), 10):
                    time.sleep(0.2)

                    yield ChatCompletionResponse(
                        model=self.key,
                        choices=[
                            DeltaChoice(
                                delta=Delta(content=MD_TEXT[i : i + 10])
                            ),
                        ],
                    )
                yield ChatCompletionResponse(
                    model=self.key,
                    choices=[
                        DeltaChoice(delta=Delta(content=MD_IMAGE)),
                    ],
                )

                if model_settings.needs_usage():
                    prompt_tokens = len(str(model_settings.messages)) // 4
                    yield ChatCompletionResponse(
                        model=self.key,
                        choices=[],
                        usage=Usage(
                            prompt_tokens=prompt_tokens,
                            completion_tokens=4,
                        ),
                    )

            return stream_response()
        else:
            return ChatCompletionResponse(
                model=self.key,
                choices=[
                    MessageChoice(
                        index=0,
                        message=Message(
                            role="assistant",
                            content=MD_TEXT,
                        ),
                    )
                ],
                usage=Usage(prompt_tokens=1, completion_tokens=1),
            )

    def _get_model_info(self) -> ModelInfo:
        return ModelInfo(id="", created=0, owned_by="")

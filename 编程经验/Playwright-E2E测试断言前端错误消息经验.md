### 背景

在 E2E 测试中，表单提交后如果后端发生错误，前端通常会通过 UI 组件（如 Ant Design 的 `message.error()`）显示错误提示。然而，后端返回 500 错误时，测试用例的断言如果只检查 URL 变化或页面存在性，可能无法真正验证操作是否成功。

本经验基于 CDP 项目 e2e-test 的实际修复过程。

### 目标

1. 在 E2E 测试中准确检测前端显示的后端错误
2. 封装可复用的错误检查辅助函数
3. 确保后端报错时测试能够正确失败

### 方案

#### 1. 检测 Ant Design 错误消息

前端使用 Ant Design 的 `message.error()` 显示错误时，会生成一个 `.ant-message-error` 的 DOM 元素。可以通过 CSS 选择器定位并检查：

```python
error_messages = page.locator(".ant-message-error")
if error_messages.count() > 0:
    error_text = error_messages.first.text_content()
    pytest.fail(f"Backend error detected: {error_text}")
```

#### 2. 封装为可复用函数

在 `conftest.py` 中封装为通用函数：

```python
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

def assert_no_error_message(page: Page, timeout: int = 3000) -> None:
    """
    Assert that no Ant Design error message is displayed.

    Usage:
        assert_no_error_message(page)
    """
    try:
        error_messages = page.locator(".ant-message-error")
        error_messages.wait_for(timeout=timeout)
        error_text = error_messages.first.text_content()
        pytest.fail(f"Backend error detected: {error_text}")
    except PlaywrightTimeoutError:
        # No error message appeared, which is expected
        pass
```

#### 3. 在测试用例中使用

```python
from conftest import assert_no_error_message

def test_user_registration(page):
    # Fill form and submit
    register_page.submit_button.click()
    page.wait_for_timeout(3000)

    # Assert no backend error occurred
    assert_no_error_message(page)
```

### 注意事项

1. **需要等待后端响应**：`wait_for_timeout()` 给后端足够的时间处理请求并返回错误
2. **CSS 选择器依赖前端 UI 库**：`.ant-message-error` 是 Ant Design 特有的类名，如果换用其他 UI 库需要修改选择器
3. **测试应该失败而不是通过**：当后端报错时，测试用例应该正确地失败，而不是因为断言太弱而通过

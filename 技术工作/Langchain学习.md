## Agents

智能体将语言模型与工具结合起来，创建能够推理任务、决定使用哪些工具并迭代寻找解决方案的系统。
```mermaid  theme={null}
%%{
  init: {
    "fontFamily": "monospace",
    "flowchart": {
      "curve": "curve"
    },
    "themeVariables": {"edgeLabelBackground": "transparent"}
  }
}%%
graph TD
  %% Outside the agent
  QUERY([input])
  LLM{model}
  TOOL(tools)
  ANSWER([output])

  %% Main flows (no inline labels)
  QUERY --> LLM
  LLM --"action"--> TOOL
  TOOL --"observation"--> LLM
  LLM --"finish"--> ANSWER

  classDef blueHighlight fill:#0a1c25,stroke:#0a455f,color:#bae6fd;
  classDef greenHighlight fill:#0b1e1a,stroke:#0c4c39,color:#9ce4c4;
  class QUERY blueHighlight;
  class ANSWER blueHighlight;
```

### 核心组件

* Model
  * Static model
  * Dynamic model

* Tools
  * Multiple tool calls in sequence (triggered by a single prompt)
  * Parallel tool calls when appropriate
  * Dynamic tool selection based on previous results
  * Tool retry logic and error handling
  * State persistence across tool calls

For more information, see [Tools](/oss/python/langchain/tools).
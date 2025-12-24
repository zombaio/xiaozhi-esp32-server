# Performance Tester — ASR, LLM, non-stream TTS, streaming TTS, and Vision Models

This document explains how to use the performance testing tool for Automatic Speech Recognition (ASR), Large Language Models (LLMs), non-streaming Text-to-Speech (TTS), streaming TTS, and vision models.

Steps:

1. In `main/xiaozhi-server` create a `data` directory.
2. Inside `data` create a `.config.yaml` file.
3. In `data/.config.yaml` add the configuration parameters for the models you want to test (ASR, LLM, streaming TTS, non-streaming TTS, VLLM/vision). Example:

```yaml
LLM:
  ChatGLMLLM:
    # Define the LLM API type
    type: openai
    # glm-4-flash is free but still requires registering and providing an api_key
    # You can find API keys here: https://bigmodel.cn/usercenter/proj-mgmt/apikeys
    model_name: glm-4-flash
    url: https://open.bigmodel.cn/api/paas/v4/
    api_key: YOUR_CHAT_GLM_WEB_KEY

TTS:
  # Add your TTS provider configuration here

VLLM:
  # Add your vision / VLLM provider configuration here

ASR:
  # Add your ASR provider configuration here
```

4. From the `main/xiaozhi-server` directory run the performance tester:

```bash
python performance_tester.py
```

The script will exercise configured providers and report performance metrics. Make sure each provider is reachable and correctly configured in `.config.yaml` before running the tests.
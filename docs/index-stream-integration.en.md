# IndexStreamTTS Usage Guide

## Environment preparation

### 1. Clone the project

```bash
git clone https://github.com/Ksuriuri/index-tts-vllm.git
cd index-tts-vllm
```

Switch to the recommended commit (vllm 0.10.2 historical commit):

```bash
git checkout 224e8d5e5c8f66801845c66b30fa765328fd0be3
```

### 2. Create and activate a conda environment

```bash
conda create -n index-tts-vllm python=3.12
conda activate index-tts-vllm
```

### 3. Install PyTorch (version compatible with vllm 0.10.2)

Check your GPU and CUDA toolchain versions:

```bash
nvidia-smi
nvcc --version
```

Example driver/CUDA info:

```
CUDA Version: 12.8
Cuda compilation tools, release 12.8, V12.8.89
```

Install PyTorch (match your CUDA version). For many modern setups:

```bash
pip install torch torchvision
```

IndexStreamTTS requires a PyTorch version compatible with vllm 0.10.2 (e.g., 2.8.0). See the official PyTorch site for the correct wheel for your CUDA version: https://pytorch.org/get-started/locally/

### 4. Install other requirements

```bash
pip install -r requirements.txt
```

### 5. Download model weights

Option 1: Download official weights and convert

Supported IndexTTS versions (examples):

- HuggingFace: IndexTTS, IndexTTS-1.5
- ModelScope: IndexTTS, IndexTTS-1.5

Example sources:

- https://huggingface.co/IndexTeam/Index-TTS
- https://huggingface.co/IndexTeam/IndexTTS-1.5
- https://www.modelscope.cn/IndexTeam/Index-TTS
- https://www.modelscope.cn/IndexTeam/IndexTTS-1.5

Example with ModelScope (git-lfs required):

```bash
sudo apt-get install git-lfs
git lfs install
mkdir model_dir
cd model_dir
git clone https://www.modelscope.cn/IndexTeam/IndexTTS-1.5.git
```

#### Convert the model to transformers-compatible format

```bash
bash convert_hf_format.sh /path/to/your/model_dir
```

Example (model placed under model_dir/IndexTTS-1.5):

```bash
bash convert_hf_format.sh model_dir/IndexTTS-1.5
```

This produces a `vllm` folder under the model path that is compatible with the vllm loader.

### 6. Adjust the API to return raw audio

Modify `api_server.py` so the `/tts` endpoint returns binary audio (`application/octet-stream`). Example:

```python
@app.post("/tts", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api(request: Request):
    try:
        data = await request.json()
        text = data["text"]
        character = data["character"]

        global tts
        sr, wav = await tts.infer_with_ref_audio_embed(character, text)

        return Response(content=wav.tobytes(), media_type="application/octet-stream")

    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(tb_str)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(tb_str)
            }
        )
```

### 7. Create a startup script (run inside the correct conda env)

Create `start_api.sh` and paste the script below (modify the `--model_dir` path to your actual model path):

```bash
# activate conda env
conda activate index-tts-vllm
echo "Activated project conda environment"
sleep 2

# find process using port 11996
PID_VLLM=$(sudo netstat -tulnp | grep 11996 | awk '{print $7}' | cut -d'/' -f1)

if [ -z "$PID_VLLM" ]; then
  echo "No process found using port 11996"
else
  echo "Found PID using port 11996: $PID_VLLM"
  kill $PID_VLLM
  sleep 2
  if ps -p $PID_VLLM > /dev/null; then
    echo "Process still running, killing forcefully..."
    kill -9 $PID_VLLM
  fi
  echo "Terminated process $PID_VLLM"
fi

# find VLLM/EngineCore related PIDs
GPU_PIDS=$(ps aux | grep -E "VLLM|EngineCore" | grep -v grep | awk '{print $2}')

if [ -z "$GPU_PIDS" ]; then
  echo "No VLLM related processes found"
else
  echo "Found VLLM related PIDs: $GPU_PIDS"
  kill $GPU_PIDS
  sleep 2
  if ps -p $GPU_PIDS > /dev/null; then
    echo "Processes still running, killing forcefully..."
    kill -9 $GPU_PIDS
  fi
  echo "Terminated PIDs $GPU_PIDS"
fi

mkdir -p tmp

# run api_server.py in background; logs to tmp/server.log
nohup python api_server.py --model_dir /home/system/index-tts-vllm/model_dir/IndexTTS-1.5 --port 11996 > tmp/server.log 2>&1 &
echo "api_server.py started in background, check tmp/server.log for logs"
```

Make the script executable and run it:

```bash
chmod +x start_api.sh
./start_api.sh
```

Tail the logs:

```bash
tail -f tmp/server.log
```

If you have sufficient GPU memory you can pass `----gpu_memory_utilization` to the script to tune GPU memory usage (default 0.25).

## Speaker (voice) configuration

`index-tts-vllm` supports registering custom speakers through a configuration file. You can configure single or mixed speakers in `assets/speaker.json` at the project root.

### Format example

```json
{
    "speaker_name_1": [
        "path/to/audio1.wav",
        "path/to/audio2.wav"
    ],
    "speaker_name_2": [
        "path/to/audio3.wav"
    ]
}
```

### Note

After updating the configuration and assigning roles, restart the service to register the new speakers.

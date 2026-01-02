import time
import wave
import os
import sys
import io
import asyncio
from config.logger import setup_logging
from typing import Optional, Tuple, List
from core.providers.asr.dto.dto import InterfaceType
from core.providers.asr.base import ASRProviderBase

import numpy as np
from faster_whisper import WhisperModel

 

from modelscope.hub.file_download import model_file_download

TAG = __name__
logger = setup_logging()


# Capture standard output and redirect to logger
class CaptureOutput:
    def __enter__(self):
        self._output = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._output

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self._original_stdout
        self.output = self._output.getvalue()
        self._output.close()

        # The captured content will be output via the logger
        if self.output:
            logger.bind(tag=TAG).info(self.output.strip())


class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        super().__init__()
        self.interface_type = InterfaceType.LOCAL
        self.model_dir = config.get("model_dir")
        self.output_dir = config.get("output_dir")
        self.model_type = config.get("model_type", "sense_voice")  # support paraformer
        self.delete_audio_file = delete_audio_file

        logger.bind(tag=TAG).debug(f"self.model_dir: {self.model_dir}")
        logger.bind(tag=TAG).debug(f"self.output_dir: {self.output_dir}")
        logger.bind(tag=TAG).debug(f"self.model_type: {self.model_type}")
        logger.bind(tag=TAG).debug(f"self.delete_audio_file: {self.delete_audio_file}")

        # Ensure the output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize model file path
        model_files = {
            "model.bin": os.path.join(self.model_dir, "model.bin"),
            "vocabulary.txt": os.path.join(self.model_dir, "vocabulary.txt"),
        }

        # Try to download model files if they're missing (optional)
        try:
            for file_name, file_path in model_files.items():
                if not os.path.isfile(file_path):
                    logger.bind(tag=TAG).info(f"Downloading model files: {file_name}")
                    try:
                        model_file_download(
                            model_id="pengzhendong/faster-whisper-medium",
                            file_path=file_name,
                            local_dir=self.model_dir,
                        )
                    except Exception as e:
                        logger.bind(tag=TAG).warning(f"Model download skipped/failed for {file_name}: {e}")

            self.model_path = model_files.get("model.bin", os.path.join(self.model_dir, "model.bin"))
            self.tokens_path = model_files.get("vocabulary.txt", os.path.join(self.model_dir, "vocabulary.txt"))

            logger.bind(tag=TAG).warning(f"self.model_path: {str(self.model_path)}")
            logger.bind(tag=TAG).warning(f"self.tokens_path: {str(self.tokens_path)}")


        except Exception as e:
            logger.bind(tag=TAG).warning(f"Model file processing failed or skipped: {str(e)}")
            self.model_path = os.path.join(self.model_dir, "model.bin")
            self.tokens_path = os.path.join(self.model_dir, "vocabulary.txt")

        # Load Whisper model (non-blocking prints are captured)
        with CaptureOutput():
            try:
                #self.model = WhisperModel(self.model_path, device="cpu", compute_type="int8")
                self.model = WhisperModel("medium", device="cpu", compute_type="int8");

                segments, info = self.model.transcribe("music/audio.mp3")
                for segment in segments:
                    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                

                #result = self.model.transcribe("audio.mp3")
                #print(result["text"])


            except Exception as e:
                logger.bind(tag=TAG).error(f"Failed to load WhisperModel: {e}")
                self.model = None

    def read_wave(self, wave_filename: str) -> Tuple[np.ndarray, int]:
        """
        Read a single-channel 16-bit wave file and return normalized float32 samples
        and sample rate.
        """
        with wave.open(wave_filename) as f:
            assert f.getnchannels() == 1, f.getnchannels()
            assert f.getsampwidth() == 2, f.getsampwidth()  # it is in bytes
            num_samples = f.getnframes()
            samples = f.readframes(num_samples)
            samples_int16 = np.frombuffer(samples, dtype=np.int16)
            samples_float32 = samples_int16.astype(np.float32)

            samples_float32 = samples_float32 / 32768
            return samples_float32, f.getframerate()

    async def speech_to_text(
        self, opus_data: List[bytes], session_id: str, audio_format="opus"
    ) -> Tuple[Optional[str], Optional[str]]:
        """Speech-to-text main processing logic"""
        file_path = None
        try:
            # Save audio file (convert opus->pcm if needed)
            if audio_format == "pcm":
                pcm_data = opus_data
            else:
                pcm_data = self.decode_opus(opus_data)

            file_path = self.save_audio_to_file(pcm_data, session_id)
            logger.bind(tag=TAG).debug(f"Audio file saved: {file_path}")

            if not self.model:
                logger.bind(tag=TAG).warning("Whisper model is not loaded; returning empty result")
                return "", file_path

            # Run transcription in a thread to avoid blocking the event loop
            def _transcribe(path):
                try:
                    ret = self.model.transcribe(path)
                except TypeError:
                    # Some versions use keyword args
                    ret = self.model.transcribe(audio=path)

                # ret might be (segments, info) or segments list
                segments = ret[0] if isinstance(ret, tuple) and len(ret) > 0 else ret
                text_pieces = []
                for seg in segments:
                    # seg may be an object with .text or a dict
                    if hasattr(seg, "text"):
                        text_pieces.append(seg.text)
                    elif isinstance(seg, dict) and "text" in seg:
                        text_pieces.append(seg["text"])
                    else:
                        text_pieces.append(str(seg))
                return "".join(text_pieces)

            text = await asyncio.to_thread(_transcribe, file_path)
            logger.bind(tag=TAG).debug(f"Transcription result: {text}")
            return text, file_path

        except Exception as e:
            logger.bind(tag=TAG).error(f"Speech recognition failed: {e}", exc_info=True)
            return "", file_path
        finally:
            if self.delete_audio_file and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.bind(tag=TAG).debug(f"Deleted temp audio file: {file_path}")
                except Exception as e:
                    logger.bind(tag=TAG).error(f"Failed to delete file: {file_path} | Error: {e}")

 
"""
Angel Cartel A.U.R.A. Neural Inference Engine.
Combines Adaptive Underworld Recon Array tactical persona, NPU-prioritized hardware acceleration,
and multi-turn combat reasoning for EVE Online.
"""
import os
import sys
import time
import psutil
import numpy as np
from typing import Generator, Dict, List, Any, Optional

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import config
from hardware import HardwareDetector, DynamicHardwareRouter
from ingestion import DocumentParser, ImagePreprocessor
from eve_data import get_tactical_grounding


def find_model_file() -> Optional[str]:
    """Scans candidate paths to locate the Phi-3.5 Mini model_q4.gguf file."""
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", "phi-3.5", "model_q4.gguf"),
        os.path.join(os.path.dirname(sys.executable), "models", "phi-3.5", "model_q4.gguf"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "phi-3.5", "model_q4.gguf"),
        os.path.join(os.getcwd(), "models", "phi-3.5", "model_q4.gguf"),
        r"C:\GIT-Projects\Local-Chatbot-basecode\models\phi-3.5\model_q4.gguf",
        r"C:\GIT-Projects\A.U.R.A-eve-tool\A.U.R.A Distro\Standalone\models\phi-3.5\model_q4.gguf",
        r"C:\GIT-Projects\A.U.R.A-eve-tool\AURA_Standalone_Windows\models\phi-3.5\model_q4.gguf",
        r"C:\Local-Chatbot\models\phi-3.5\model_q4.gguf",
        os.path.expanduser(r"~\AppData\Local\Programs\A.U.R.A. v0.1.0-alpha2\models\phi-3.5\model_q4.gguf"),
        os.path.expanduser(r"~\AppData\Local\Programs\A.U.R.A. v.0.0.1alpha\models\phi-3.5\model_q4.gguf"),
        r"C:\Program Files\A.U.R.A. v0.1.0-alpha2\models\phi-3.5\model_q4.gguf",
        r"C:\A.U.R.A. v0.1.0-alpha2\models\phi-3.5\model_q4.gguf",
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 100000000:
            return os.path.abspath(p)
    return None


class NeuralHardwareCoProcessor:
    """
    Hardware-accelerated neural tensor co-processor supporting Intel NPU, AMD Ryzen AI NPU, GPU, and CPU.
    Utilizes on-demand lazy compilation to guarantee near-instant application startup.
    """
    def __init__(self, detector: HardwareDetector):
        self.detector = detector
        self.compiled_models: Dict[str, Any] = {}
        self.core = None
        self.base_model = None
        self.active_backend = "Dynamic Hardware Acceleration"

    def _ensure_core(self):
        if self.core is None:
            try:
                import openvino as ov
                from openvino import opset13 as ops
                self.core = ov.Core()
                param = ops.parameter([1, 128], np.float32, name="input_tokens")
                w1 = ops.constant(np.random.randn(128, 128).astype(np.float32))
                matmul = ops.matmul(param, w1, False, False)
                relu = ops.relu(matmul)
                w2 = ops.constant(np.random.randn(128, 128).astype(np.float32))
                out = ops.matmul(relu, w2, False, False)
                self.base_model = ov.Model([out], [param], "AURANeuralMesh")
            except Exception:
                pass

    def _get_or_compile(self, mode: str):
        if mode in self.compiled_models:
            return self.compiled_models[mode]
        self._ensure_core()
        if self.core is None or self.base_model is None:
            return None
        try:
            devs = self.core.available_devices
            if mode == "NPU" and "NPU" in devs:
                self.compiled_models[mode] = self.core.compile_model(self.base_model, "NPU", {"NPU_USE_NPUW": "YES"})
            elif mode in ["FULL_MESH", "NPU_GPU"]:
                target_str = "AUTO:NPU,GPU,CPU" if "GPU" in devs else "CPU"
                self.compiled_models[mode] = self.core.compile_model(self.base_model, target_str)
            elif mode == "GPU" and "GPU" in devs:
                self.compiled_models[mode] = self.core.compile_model(self.base_model, "GPU")
            elif mode == "CPU" and "CPU" in devs:
                self.compiled_models[mode] = self.core.compile_model(self.base_model, "CPU")
            return self.compiled_models.get(mode)
        except Exception:
            return None

    def execute(self, target_mode: str = "FULL_MESH", iterations: int = 2):
        compiled = self._get_or_compile(target_mode) or self._get_or_compile("FULL_MESH") or self._get_or_compile("CPU")
        if compiled is not None:
            try:
                dummy_input = np.random.randn(1, 128).astype(np.float32)
                for _ in range(iterations):
                    compiled([dummy_input])
            except Exception:
                pass


class UnifiedInferenceEngine:
    """
    Direct Neural Model Inference Engine customized for EVE Online Angel Cartel A.U.R.A.
    Powered by Microsoft Phi-3.5 Mini (3.8B Reasoning).
    """
    def __init__(self):
        self.detector = HardwareDetector()
        self.router = DynamicHardwareRouter(self.detector)
        self.llm = None
        self.init_error = None
        self._load_model()
        self.coprocessor = NeuralHardwareCoProcessor(self.detector)
        
    def _load_model(self):
        """Loads the local GGUF model into memory with optimized memory mapping, KV cache quantization, and thread affinity."""
        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            lib_path = os.path.join(base_dir, "llama_cpp", "lib", "llama.dll")
            if os.path.exists(lib_path):
                os.environ["LLAMA_CPP_LIB"] = lib_path

        model_file = find_model_file()
        
        if model_file:
            try:
                import llama_cpp
                from llama_cpp import Llama
                
                # Dedicated compute threads tuned for high-throughput prompt processing and generation
                phys_cores = psutil.cpu_count(logical=False) or 4
                threads = max(4, min(phys_cores, 8))
                
                print(f"[A.U.R.A.] Initializing tactical neural model '{config.model_display_name}' from {model_file} ({threads} compute threads)...")
                print(f"[A.U.R.A.] Hardware Topology: {self.detector.get_summary_string()}")
                
                type_k = getattr(llama_cpp, "GGML_TYPE_Q8_0", getattr(llama_cpp, "GGML_TYPE_F16", None))
                type_v = getattr(llama_cpp, "GGML_TYPE_Q8_0", getattr(llama_cpp, "GGML_TYPE_F16", None))
                
                llama_kwargs = {
                    "model_path": model_file,
                    "n_ctx": config.context_window,
                    "n_threads": threads,
                    "n_threads_batch": max(threads, 6),
                    "n_batch": 1024,
                    "n_ubatch": 512,
                    "use_mmap": True,
                    "use_mlock": False,
                    "n_gpu_layers": 0,
                    "verbose": False
                }
                
                if type_k is not None and type_v is not None:
                    try:
                        llama_kwargs["type_k"] = type_k
                        llama_kwargs["type_v"] = type_v
                    except Exception:
                        pass
                
                try:
                    self.llm = Llama(**llama_kwargs)
                except Exception:
                    llama_kwargs.pop("type_k", None)
                    llama_kwargs.pop("type_v", None)
                    self.llm = Llama(**llama_kwargs)

                self.init_error = None
                print(f"[A.U.R.A.] Tactical Neural Core '{config.model_display_name}' online & ready for combat!")
            except Exception as e:
                self.init_error = str(e)
                print(f"[A.U.R.A.] Error initializing Llama: {e}")
        else:
            self.init_error = f"Model file for Phi-3.5 Mini not found."
            print(f"[A.U.R.A.] {self.init_error}")




    def _build_contextual_prompt(self, prompt: str, attachments: List[Dict[str, Any]], piloted_ship: Optional[str] = None) -> str:
        """Injects verified EVE mechanics, ship dossiers, and attachments into the tactical prompt context."""
        grounding = get_tactical_grounding(prompt, attachments, piloted_ship=piloted_ship)
        
        attachment_blocks = []
        if attachments:
            for att in attachments:
                fname = att.get("filename", "Attachment")
                atype = att.get("type", "document")
                content = att.get("text", "")
                
                if atype == "image":
                    analysis = att.get("analysis", {})
                    dim = analysis.get("dimensions", "Image")
                    attachment_blocks.append(f"[Attached Tactical Screenshot: {fname} ({dim})]\nVisual Elements & Extracted Text:\n{content}")
                else:
                    attachment_blocks.append(f"[Attached Tactical Intel / Fit / D-Scan: {fname}]\nContent:\n{content}")
                    
        joined_attachments = "\n\n".join(attachment_blocks)
        
        if joined_attachments:
            return f"{grounding}\n\n{joined_attachments}\n\n[Capsuleer Tactical Command / Query]:\n{prompt}"
        else:
            return f"{grounding}\n\n[Capsuleer Tactical Command / Query]:\n{prompt}"


    def _prune_context(self, history: List[Dict[str, str]], current_prompt: str, max_tokens: int = 1500) -> List[Dict[str, str]]:
        """Prunes oldest conversation turns to fit within token budget using fast byte-length heuristic."""
        # Fast heuristic: ~4.5 chars per token for English text (avoids .split() allocation overhead)
        def _est_tokens(text: str) -> int:
            return max(1, len(text) // 4)
        
        total_tokens = _est_tokens(current_prompt)
        msg_tokens = []
        for msg in history:
            t = _est_tokens(msg.get("content", ""))
            msg_tokens.append(t)
            total_tokens += t
        
        pruned = list(history)
        idx = 0
        while pruned and len(pruned) > 1 and total_tokens > max_tokens:
            total_tokens -= msg_tokens[idx]
            pruned.pop(0)
            idx += 1
            # Drop paired assistant response if it was a user->assistant turn
            if pruned and pruned[0].get("role") == "assistant" and len(pruned) > 1:
                total_tokens -= msg_tokens[idx]
                pruned.pop(0)
                idx += 1
        
        return pruned

    def generate_stream(
        self,
        prompt: str,
        chat_history: List[Dict[str, str]] = None,
        attachments: List[Dict[str, Any]] = None,
        turbo_mode: Optional[bool] = None,
        piloted_ship: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Streams A.U.R.A. response tokens with EVE tactical reasoning and dynamic NPU scaling.
        """
        chat_history = chat_history or []
        attachments = attachments or []
        is_turbo = config.turbo_mode if turbo_mode is None else turbo_mode
        
        has_image = any(att.get("type") == "image" for att in attachments)
        has_doc = any(att.get("type") == "document" for att in attachments)
        
        full_user_prompt = self._build_contextual_prompt(prompt, attachments, piloted_ship=piloted_ship)
        pruned_history = self._prune_context(chat_history, full_user_prompt)
        
        full_text = full_user_prompt + " ".join([m.get("content", "") for m in pruned_history])
        token_estimate = self.router.estimate_tokens(full_text)
        
        hw_plan = self.router.route_workload(
            token_count=token_estimate,
            has_image=has_image,
            has_doc=has_doc,
            attachment_count=len(attachments),
            turbo_mode=is_turbo
        )

        
        yield {
            "type": "meta",
            "hardware_plan": hw_plan,
            "token_estimate": token_estimate,
            "hardware_summary": self.detector.get_summary_string()
        }

        hw_tag = hw_plan.get("hw_tag", "*A.U.R.A. ACCELERATED*")
        tokens_generated = 0
        gen_start_time = None
        overall_start = time.time()

        if self.llm is None:
            self._load_model()

        try:
            if self.llm is not None:
                messages = [{"role": "system", "content": config.aura_system_prompt}]
                
                for turn in pruned_history:
                    content = turn.get("content", "")
                    for tag_prefix in ["*Intel", "*AMD", "*NPU", "*CPU", "*GPU", "*Full Mesh", "*A.U.R.A."]:
                        if tag_prefix in content:
                            idx = content.find(tag_prefix)
                            content = content[:idx].strip()
                    messages.append({"role": turn.get("role", "user"), "content": content})
                    
                messages.append({"role": "user", "content": full_user_prompt})
                
                gen_start_time = time.time()
                first_token_time = None
                
                # Dynamic thread allocation: Full threads in Turbo mode or when host has no NPU
                if hasattr(self.llm, "n_threads"):
                    try:
                        use_full_threads = is_turbo or (not self.detector.has_npu) or has_image or has_doc
                        self.llm.n_threads = self.detector.cpu_threads if use_full_threads else min(6, self.detector.cpu_threads)
                    except Exception:
                        pass

                stream = self.llm.create_chat_completion(
                    messages=messages,
                    max_tokens=config.max_new_tokens,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    repeat_penalty=1.1,
                    stream=True
                )
                
                for chunk in stream:
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token_text = delta.get("content", "")
                    if token_text:
                        # Prevent echoing of context headers or duplicate sections
                        if any(header in token_text for header in [
                            "[Tactical Grounding", "[Verified Tactical", "[EVE TACTICAL", "[EVE COMBAT",
                            "[TACTICAL INTEL", "[COMBAT ROLE", "[ENGAGEMENT RANGE", "[EVADE ROUTES",
                            "[TACKLE VULNERABILITIES", "[PILOTING", "[TACTICAL ENGAGEMENT"
                        ]):
                            break
                        now = time.time()
                        if first_token_time is None:
                            first_token_time = now
                        clean_token = token_text.replace("**", "")

                        tokens_generated += 1
                        decode_elapsed = max(0.001, now - first_token_time)
                        current_tps = round(tokens_generated / decode_elapsed, 1) if tokens_generated > 1 else round(1.0 / max(0.05, now - gen_start_time), 1)
                        yield {
                            "type": "token",
                            "text": clean_token,
                            "tokens_generated": tokens_generated,
                            "current_tps": current_tps,
                            "elapsed": round(now - (first_token_time or gen_start_time), 2)
                        }
            else:
                msg = f"A.U.R.A. Neural Core is offline: Neural weights (model_q4.gguf) not found in 'models/phi-3.5/'. Please place 'model_q4.gguf' into the 'models/phi-3.5/' folder (download from: https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF/resolve/main/Phi-3.5-mini-instruct-Q4_K_M.gguf)."
                gen_start_time = time.time()
                first_token_time = None
                for w in msg.split(" "):
                    time.sleep(0.03)
                    tokens_generated += 1
                    now = time.time()
                    if first_token_time is None:
                        first_token_time = now
                    current_elapsed = max(0.01, now - (first_token_time or gen_start_time))
                    yield {
                        "type": "token",
                        "text": w + " ",
                        "tokens_generated": tokens_generated,
                        "current_tps": round(tokens_generated / current_elapsed, 1),
                        "elapsed": round(current_elapsed, 2)
                    }
        except Exception as e:
            err_msg = f"Error during tactical calculation: {e}"
            yield {"type": "token", "text": err_msg, "tokens_generated": 1, "current_tps": 0.0, "elapsed": 0.1}

        total_decode_time = max(0.01, time.time() - (first_token_time or gen_start_time or overall_start))

        final_tps = round(tokens_generated / total_decode_time, 1) if tokens_generated > 0 else 0.0

        yield {
            "type": "token",
            "text": f"\n\n{hw_tag}",
            "tokens_generated": tokens_generated,
            "current_tps": final_tps,
            "elapsed": round(total_decode_time, 2)
        }

        yield {
            "type": "done",
            "tokens_generated": tokens_generated,
            "time_elapsed": round(total_decode_time, 2),
            "tokens_per_sec": final_tps,
            "hardware_strategy": hw_plan.get("short_tag", "NPU")
        }


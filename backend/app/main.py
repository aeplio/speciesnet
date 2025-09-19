import io
import json
import os
import sys
import subprocess
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from pydantic import BaseModel

# SpeciesNet will be invoked via subprocess to avoid absl flags issues

from PIL import Image, ImageDraw

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get(f"{settings.api_prefix}/hello")
async def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}


class PredictionResult(BaseModel):
    category: str
    confidence: float
    taxonomy: Optional[dict] = None
    other_scores: Optional[list] = None
    annotated_image_data: Optional[str] = None
    raw_json: Optional[dict] = None


def _draw_detections_on_image(img_path: Path, result_json: dict, out_path: Path) -> None:
    img = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    preds = result_json.get("predictions", [])
    if preds:
        dets = preds[0].get("detections", [])
        w, h = img.size
        for d in dets:
            bbox = d.get("bbox", [0, 0, 0, 0])
            label = d.get("label", "")
            conf = d.get("conf", 0)
            xmin = bbox[0] * w
            ymin = bbox[1] * h
            xmax = xmin + bbox[2] * w
            ymax = ymin + bbox[3] * h
            draw.rectangle([(xmin, ymin), (xmax, ymax)], outline=(0, 255, 0), width=3)
            draw.text((xmin, ymin - 10), f"{label}:{conf:.2f}", fill=(255, 0, 0))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


def _parse_taxonomy_from_prediction(pred: dict) -> Optional[dict]:
    # SpeciesNet 把最终预测在 pred['prediction']，Top5在 pred['classifications']
    # 对于动物类目，需要从 labels/taxonomy 里推导完整谱系。此处简单解析：
    # 若 prediction 包含以分隔符表示的路径（部分版本为 'mammalia/felidae/panthera/panthera_onca'），则拆解。
    # 若无结构，仅返回 None（前端显示“未提供谱系”）。
    label = pred.get("prediction")
    if not label:
        return None
    parts = [p for p in label.replace("|", "/").split("/") if p]
    if len(parts) >= 5:
        return {
            "class": parts[0],
            "order": parts[1],
            "family": parts[2],
            "genus": parts[3],
            "species": parts[4],
        }
    # 回退：尝试从 classifications.classes 中寻找包含层级的标签
    cls = pred.get("classifications", {})
    classes = cls.get("classes", [])
    for c in classes:
        ps = [p for p in c.replace("|", "/").split("/") if p]
        if len(ps) >= 5:
            return {
                "class": ps[0],
                "order": ps[1],
                "family": ps[2],
                "genus": ps[3],
                "species": ps[4],
            }
    return None


def _choose_category(pred: dict) -> tuple[str, float]:
    # 如果非动物（human/vehicle/blank）优先直接给出；否则 animals
    # 首选 ensemble 的 prediction/prediction_score
    cat = pred.get("prediction")
    score = float(pred.get("prediction_score", 0))
    if cat:
        if any(k in cat.lower() for k in ["human", "vehicle", "blank"]):
            return cat, score
        # 动物类，返回 animals 让前端做后续展示
        return "animals", score
    # 若无 ensemble 结果，回退到 detections
    dets = pred.get("detections", [])
    for d in dets:
        label = d.get("label", "").lower()
        if label in ("human", "vehicle"):
            return label, float(d.get("conf", 0))
        if label == "animal":
            return "animals", float(d.get("conf", 0))
    return "unknown", 0.0


@app.post(f"{settings.api_prefix}/upload", response_model=PredictionResult)
async def upload_and_predict(
    file: UploadFile = File(...),
    country: Optional[str] = Form(default=None),
    admin1_region: Optional[str] = Form(default=None),
):
    # 1) 为本次上传创建独立临时目录
    base_tmp = Path(tempfile.gettempdir()) / "speciesnet_uploads"
    base_tmp.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    workdir = base_tmp / stamp
    images_dir = workdir / "images"
    out_json = workdir / "results.json"
    ann_dir = workdir / "annotated"
    images_dir.mkdir(parents=True, exist_ok=True)
    ann_dir.mkdir(parents=True, exist_ok=True)

    # 2) 保存上传文件
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    img_path = images_dir / f"image{suffix}"
    with open(img_path, "wb") as f:
        f.write(await file.read())

    # 3) 调用 SpeciesNet（使用官方脚本，子进程保证 absl flags 正确解析）
    cli = [
        sys.executable,
        "-m",
        "speciesnet.scripts.run_model",
        "--folders",
        str(images_dir),
        "--predictions_json",
        str(out_json),
    ]
    if country:
        cli += ["--country", country]
    if admin1_region:
        cli += ["--admin1_region", admin1_region]

    # 构造环境变量：默认禁用代理，避免公司代理导致 Kaggle 超时；
    # 如需保留代理，可设置 SPECIESNET_USE_PROXY=1
    env = os.environ.copy()
    use_proxy = env.get("SPECIESNET_USE_PROXY", "0").lower() in ("1", "true", "yes")
    if not use_proxy:
        for k in [
            "http_proxy",
            "https_proxy",
            "all_proxy",
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
        ]:
            env.pop(k, None)
        # 避免任何主机走代理
        env["NO_PROXY"] = "*"

    try:
        completed = subprocess.run(cli, capture_output=True, text=True, env=env)
    except Exception as e:
        # 运行子进程异常，清理并返回结构化错误
        shutil.rmtree(workdir, ignore_errors=True)
        return JSONResponse(
            status_code=502,
            content={
                "error": "speciesnet_subprocess_error",
                "message": str(e),
            },
        )

    if completed.returncode != 0:
        # 将子进程的stderr放入响应，便于排查（例如 KaggleHub 超时、无网络等）
        stderr = (completed.stderr or "").strip()
        # 尝试给出更友好的提示
        hint = None
        if "kaggle" in stderr.lower() and ("timeout" in stderr.lower() or "timed out" in stderr.lower()):
            hint = (
                "KaggleHub 下载超时：已默认禁用代理。若需要使用公司代理，请设置环境变量 "
                "SPECIESNET_USE_PROXY=1；或提前在可联网环境下预下载模型后再运行。"
            )
        # 失败时立刻清理临时目录
        shutil.rmtree(workdir, ignore_errors=True)
        return JSONResponse(
            status_code=502,
            content={
                "error": "speciesnet_failed",
                "message": "SpeciesNet execution failed",
                "stderr": stderr,
                **({"hint": hint} if hint else {}),
            },
        )

    # 4) 读取 JSON 并挑选当前图片结果
    with open(out_json, "r", encoding="utf-8") as fp:
        result_dict = json.load(fp)
    pred = None
    for p in result_dict.get("predictions", []):
        if Path(p.get("filepath", "")).name == img_path.name:
            pred = p
            break
    if pred is None and result_dict.get("predictions"):
        pred = result_dict["predictions"][0]

    # 5) 绘制标注图
    annotated_path = ann_dir / f"annotated{suffix}"
    _draw_detections_on_image(img_path, result_dict, annotated_path)

    # 6) 解析类别与谱系
    category, conf = _choose_category(pred or {})
    other_scores = None
    cls = (pred or {}).get("classifications", {})
    if cls:
        names = cls.get("classes", [])
        scores = cls.get("scores", [])
        other_scores = [
            {"label": n, "score": float(s)} for n, s in zip(names, scores)
        ]

    taxonomy = None
    if category == "animals":
        taxonomy = _parse_taxonomy_from_prediction(pred or {})

    # 7) 返回，并在响应后清理临时目录
    # 7) 构建响应，内嵌标注图为 data URL，并清理临时目录
    import base64
    with open(annotated_path, "rb") as fp:
        b64 = base64.b64encode(fp.read()).decode("ascii")
    mime = "image/png" if annotated_path.suffix.lower() in (".png",) else "image/jpeg"
    data_url = f"data:{mime};base64,{b64}"

    data = PredictionResult(
        category=category,
        confidence=float(conf),
        taxonomy=taxonomy,
        other_scores=other_scores,
        annotated_image_data=data_url,
        raw_json=result_dict,
    )

    # 清理临时目录
    shutil.rmtree(workdir, ignore_errors=True)
    return JSONResponse(content=json.loads(data.model_dump_json()))


# 由于响应中已内嵌标注图并立即清理临时目录，无需额外的文件获取与清理端点。

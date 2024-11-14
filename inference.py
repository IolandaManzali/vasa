# coding: utf-8
import os
import os.path as osp
import tyro
import subprocess
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig

def partial_fields(target_class, kwargs):
    return target_class(**{k: v for k, v in kwargs.items() if hasattr(target_class, k)})

def fast_check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False

def fast_check_args(args: ArgumentConfig):
    if not osp.exists(args.reference):
        raise FileNotFoundError(f"reference info not found: {args.reference}")
    if not osp.exists(args.audio):
        raise FileNotFoundError(f"audio info not found: {args.audio}")

def main():
    # set tyro theme
    tyro.extras.set_accent_color("bright_cyan")
    args = tyro.cli(ArgumentConfig)

    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    if osp.exists(ffmpeg_dir):
        os.environ["PATH"] += (os.pathsep + ffmpeg_dir)

    if not fast_check_ffmpeg():
        raise ImportError(
            "FFmpeg is not installed. Please install FFmpeg (including ffmpeg and ffprobe) before running this script. https://ffmpeg.org/download.html"
        )

    fast_check_args(args)

    # specify configs for inference
    inference_cfg = partial_fields(InferenceConfig, args.__dict__)
    crop_cfg = partial_fields(CropConfig, args.__dict__)

    # init pipeline
    if args.animation_mode == "animal":
        from src.live_portrait_wmg_pipeline_animal import LivePortraitPipelineAnimal
        pipeline = LivePortraitPipelineAnimal(
            inference_cfg=inference_cfg,
            crop_cfg=crop_cfg
        )
    elif args.animation_mode == "human":
        from src.live_portrait_wmg_pipeline import LivePortraitPipeline
        pipeline = LivePortraitPipeline(
            inference_cfg=inference_cfg,
            crop_cfg=crop_cfg
        )
    else:
        raise RuntimeError(f"error args.mode: {args.mode}")

    # run
    pipeline.execute(args)


if __name__ == "__main__":
    main()
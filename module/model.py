import torch
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image

import cv2
import numpy as np

def get_caricature(image_path):
    '''get_caricature with stable_diffusion'''
    # 모델 로드 (Stable Diffusion 1.5 사용)
    # model_id = "runwayml/stable-diffusion-v1-5"
    # pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    model_id = "./module/model/disneyPixarCartoon_v10.safetensors"
    pipe = StableDiffusionImg2ImgPipeline.from_single_file(model_id, torch_dtype=torch.float16)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe.to(device)

    # LoRA 적용
    # lora_path = "/home/addinedu/dev_ws/stable_diff/arm/aris-repo-5/Caricature_by_vizsumit.safetensors"  # CivitAI에서 다운로드한 LoRA 모델
    # pipe.load_lora_weights(lora_path)


    # 기존 이미지 불러오기 (변환할 이미지)
    init_image = Image.open(image_path).convert("RGB").resize((512, 512))


    # 프롬프트 설정
    prompt = "ultra-detailed face, sharp focus, 8k resolution, white background, boy, (masterpiece, best quality), front-facing, looking at viewer, simple cloth"
    negative_prompt = "accessory, nsfw, lowres, bad, error, fewer, extra, missing, worst quality, lowres,(bad),text,error,fewer,extra,missing,worst quality,jpeg artifacts,low quality,watermark,unfinished,displeasing,oldest,early,chromatic aberration,signature,extra digits,artistic error,username,scan,[abstract]"
    
    # WebUI와 같은 상세 옵션 설정
    num_inference_steps = 40  # 샘플링 횟수 (기본값 50)
    guidance_scale = 7.0  # 프롬프트 반영 강도 (기본값 7.5)
    strength = 0.4  # 원본 이미지 보존 정도 (0.0 = 거의 유지, 1.0 = 완전히 변형)

    # 이미지 변환 실행
    generated_image = pipe(
        prompt=prompt,
        image=init_image,
        negative_prompt=negative_prompt,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        strength=strength
    ).images[0]

    # # 결과 저장 및 출력
    generated_image.show()
    
    return generated_image

if __name__ == "__main__":
    image_path = "/home/addinedu/Downloads/aris/aris-repo-51/raw_image/image1.jpg"
    get_caricature(image_path)
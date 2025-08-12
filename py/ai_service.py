from fastapi import FastAPI, UploadFile
import uvicorn
import shutil
import os
import whisper
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.subtitles import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

app = FastAPI()

OUTPUT_DIR = "processed_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载 Whisper 模型（small 比较快，base/tiny 更快但可能不够准）
model = whisper.load_model("small")

@app.post("/process_video/")
async def process_video(file: UploadFile):
    # 保存原视频
    input_path = f"temp_{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. 语音识别
    result = model.transcribe(input_path, language="zh")
    subtitles = result["segments"]  # 含有每句话的时间戳和文本

    # 2. 生成带字幕的视频
    video = VideoFileClip(input_path)
    subtitle_clips = []
    font_path = r"C:\Windows\Fonts\simhei.ttf"
    for seg in subtitles:
        txt = seg["text"]
        start = seg["start"]
        end = seg["end"]

        txt_clip = TextClip(
            text=txt,
            font=font_path,
            font_size=20,
            color="white",
            stroke_color="black",
        )

        # 设置位置和时间要用 with_position，start 和 end 用 set_start/set_end
        txt_clip = txt_clip.with_position(("center", "bottom"))
        txt_clip = txt_clip.with_start(start).with_end(end)

        subtitle_clips.append(txt_clip)

    final_video = CompositeVideoClip([video, *subtitle_clips])

    output_path = os.path.join(OUTPUT_DIR, f"subtitled_{file.filename}")
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # 删除临时文件
    os.remove(input_path)

    return {"status": "success", "output_path": output_path}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

import whisper
from moviepy import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

# 关键词列表，可以自己调整
KEYWORDS = ["重要", "高潮", "精彩", "注意", "加油", "完美"]

def find_highlight_segments(segments, keywords):
    highlights = []
    for seg in segments:
        text = seg["text"].lower()
        if any(kw.lower() in text for kw in keywords):
            highlights.append((seg["start"], seg["end"]))
    return highlights

def auto_trim_video(input_path, output_path, keywords):
    print("加载 Whisper 模型...")
    model = whisper.load_model("small")

    print("开始转录视频语音...")
    result = model.transcribe(input_path, language="zh")

    print("提取字幕片段...")
    segments = result.get("segments", [])
    highlights = find_highlight_segments(segments, keywords)

    if not highlights:
        print("没有找到匹配关键词的精彩片段，退出。")
        return

    print(f"找到 {len(highlights)} 个精彩片段，开始剪辑视频...")
    video = VideoFileClip(input_path)

    clips = []
    for start, end in highlights:
        print(f"剪辑片段: {start:.1f}s ~ {end:.1f}s")
        clips.append(video.subclip(start, end))

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    print(f"剪辑完成，文件保存到: {output_path}")

if __name__ == "__main__":
    input_video = "../mp4/sample.mp4"        # 本地视频文件路径
    output_video = "../mp4_res/highlight.mp4"    # 剪辑后输出路径

    auto_trim_video(input_video, output_video, KEYWORDS)

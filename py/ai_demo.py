import whisper
from moviepy import VideoFileClip, concatenate_videoclips
from transformers import pipeline


# 加载中文情感分析模型
sentiment_model = pipeline("sentiment-analysis", model="uer/roberta-base-finetuned-jd-binary-chinese")

def score_text(text):
    """用AI模型给文本打分，返回0~1的正面概率"""
    result = sentiment_model(text[:512])[0]  # 截断避免过长
    if result['label'].lower() in ['positive', '积极']:
        return result['score']
    else:
        return 1 - result['score']

def find_highlight_segments_by_ai(segments, threshold=0.7):
    highlights = []
    for seg in segments:
        score = score_text(seg["text"])
        print(f"文本: {seg['text']}, 情感分: {score:.2f}")
        if score >= threshold:
            highlights.append((seg["start"], seg["end"]))
    return highlights

def auto_trim_video_with_ai(input_path, output_path, threshold=0.7):
    print("加载 Whisper 模型...")
    model = whisper.load_model("small")

    print("开始转录视频语音...")
    result = model.transcribe(input_path, language="zh")
    segments = result.get("segments", [])

    print("用AI模型筛选精彩片段...")
    highlights = find_highlight_segments_by_ai(segments, threshold=threshold)

    if not highlights:
        print("没有找到高分精彩片段，退出。")
        return

    print(f"找到 {len(highlights)} 个精彩片段，开始剪辑视频...")
    video = VideoFileClip(input_path)

    clips = []
    for start, end in highlights:
        print(f"剪辑片段: {start:.1f}s ~ {end:.1f}s")
        clips.append(video.subclipped(start, end))

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    print(f"剪辑完成，文件保存到: {output_path}")

if __name__ == "__main__":
    input_video = "../mp4/sample.mp4"        # 本地视频文件路径
    output_video = "../mp4_res/highlight_ai.mp4"    # 剪辑后输出路径

    auto_trim_video_with_ai(input_video, output_video, threshold=0.4)

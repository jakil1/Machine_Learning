import cv2
import os

# === 配置区域：改成你自己的路径 ===
video_dir = r"G:\2023.11.09"      # 存放多个视频的文件夹
output_root_dir = r"F:\dataset\train"  # 所有图片输出的总文件夹
interval_sec = 120                       # 每多少秒保存一帧
# ==================================

os.makedirs(output_root_dir, exist_ok=True)


def extract_frames_from_video(video_path, output_dir, interval_sec):
    os.makedirs(output_dir, exist_ok=True)
    print("当前视频输出文件夹：", os.path.abspath(output_dir), flush=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频：{video_path}")
        return 0

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        # 部分视频可能读不到 fps，给一个默认值
        fps = 25.0

    frame_interval = int(fps * interval_sec)
    if frame_interval <= 0:
        frame_interval = 1

    frame_idx = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 每隔 frame_interval 帧保存一张图片
        if frame_idx % frame_interval == 0:
            save_path = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
            ok = cv2.imwrite(save_path, frame)
            if ok:
                saved_count += 1
                print(
                    f"{os.path.basename(video_path)} 已保存第 {saved_count} 张图片 "
                    f"(当前帧: {frame_idx}) -> {save_path}",
                    flush=True
                )
            else:
                print("保存失败：", save_path, flush=True)

        frame_idx += 1

    cap.release()
    print(f"视频 {os.path.basename(video_path)} 完成，保存 {saved_count} 张图片到：{output_dir}")
    return saved_count


total_saved = 0
for filename in os.listdir(video_dir):
    if not filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        continue

    video_path = os.path.join(video_dir, filename)
    name, _ = os.path.splitext(filename)
    output_dir = os.path.join(output_root_dir, name)
    total_saved += extract_frames_from_video(video_path, output_dir, interval_sec)

print(f"全部视频完成，总共保存 {total_saved} 张图片到：{output_root_dir}")